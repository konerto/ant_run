import asyncio
import json
import logging

import websockets

# Set up logging for debugging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

TOKEN = "your_token_here"  # Replace with your actual token
PHONE = "0123456789"  # Replace with your actual phone number

TARGET_SCORE = 200  # Target score to reach in the game
CURRENT_SCORE = 0  # Track current score

# WebSocket URL with parameters
WS_URL = f"wss://api-game.cellphones.com.vn/ws/ant_run?game_code=ant_run&token={TOKEN}&signature=dVp0QXhSaVJONWo2TzM4U1BGMnVRZnNoYWNFdjFXV1JBdXR4eE5CQWdKcz0=&phone={PHONE}&ua=android"

# Messages
SEGMENT_REQUEST = {"segment_gen": True}
TOTAL_DISTANCE = 0.0  # Track total distance traveled like the game does


def create_collect_action(lane, z_pos, pz_pos, y_pos, segment_id):
    """Create a collect action message using exact game logic"""
    return {
        "action": "collect",
        "lane": lane,
        "z_pos": z_pos,
        "pz_pos": pz_pos,  # Should be totalDistance - 7 according to game code
        "y_pos": y_pos,
        "segment_id": segment_id,
    }


def handle_score_update(score_data):
    """Handle score updates from the server and check if target is reached"""
    global CURRENT_SCORE

    # Extract score from various possible response formats
    new_score = None
    if isinstance(score_data, dict):
        # Check different possible score fields
        if "score" in score_data:
            new_score = score_data["score"]
        elif "total_score" in score_data:
            new_score = score_data["total_score"]
        elif "current_score" in score_data:
            new_score = score_data["current_score"]

    if new_score is not None and new_score != CURRENT_SCORE:
        CURRENT_SCORE = new_score
        logger.info(f"📊 Score Update: {CURRENT_SCORE}/{TARGET_SCORE}")

        # Check if target score is reached
        if CURRENT_SCORE >= TARGET_SCORE:
            logger.info(
                f"🎯 TARGET SCORE REACHED! Current: {CURRENT_SCORE}, Target: {TARGET_SCORE}"
            )
            return True  # Signal to stop the game

    return False  # Continue playing


def parse_game_segment(segment_data):
    """Parse the game segment and extract coins to collect"""
    coins = []
    obstacles = []

    for item in segment_data:
        # Server sends objects with lane, z, y, type, segment_id structure
        if item.get("type") == "coin" or item.get("type") == "cookie":
            # This is a coin/pickup - extract the exact data the server provides
            coins.append(
                {
                    "lane": item.get("lane", 0),
                    "z": item.get("z", 0),
                    "y": item.get("y", 0),
                    "segment_id": item.get("segment_id", 0),
                    "type": item.get("type", "coin"),
                }
            )
        elif item.get("type") == "obstacle" or item.get("type") == "divable":
            # This is an obstacle
            obstacles.append(item)

    return coins, obstacles


async def collect_coins(websocket, coins):
    """Automatically collect coins by sending collect actions with accurate pz_pos"""
    global TOTAL_DISTANCE

    logger.info(
        f"💰 Starting to collect {len(coins)} coins (Score: {CURRENT_SCORE}/{TARGET_SCORE})"
    )

    for coin in coins:
        # Use the exact pz_pos calculation from the game: this.totalDistance - 7
        pz_pos = TOTAL_DISTANCE - 7

        # Y position mapping from game: obj.worldPos.y > 0 ? 1 : 0
        y_pos = 1 if coin["y"] > 0 else 0

        # Use exact parameters that match the game's sendMessageSocketAction
        collect_action = create_collect_action(
            lane=coin["lane"],  # Direct from server data
            z_pos=coin["z"],  # obj.worldPos.z equivalent
            pz_pos=pz_pos,  # this.totalDistance - 7
            y_pos=y_pos,  # obj.worldPos.y > 0 ? 1 : 0
            segment_id=coin["segment_id"],  # obj.segmentId
        )

        message = json.dumps(collect_action)
        logger.info(
            f"Collecting {coin['type']} at lane {coin['lane']}, z={coin['z']}, y={coin['y']}, pz_pos={pz_pos}: {message}"
        )
        await websocket.send(message)

        # Small delay between actions
        await asyncio.sleep(0.1)

        # Simulate distance progress (in real game this would be based on actual movement)
        TOTAL_DISTANCE += 0.5

    logger.info(f"✅ Finished collecting {len(coins)} coins")


async def connect_websocket():
    """Connect to the WebSocket and handle communication"""
    global TOTAL_DISTANCE, CURRENT_SCORE

    try:
        logger.info(f"Connecting to WebSocket: {WS_URL}")  # Connect to the WebSocket
        async with websockets.connect(WS_URL) as websocket:
            logger.info("Connected successfully!")
            logger.info(f"🎯 Target Score: {TARGET_SCORE}")

            current_segment = 1
            TOTAL_DISTANCE = (
                7.0  # Initialize with small offset since pz_pos = totalDistance - 7
            )
            CURRENT_SCORE = 0  # Reset score

            # Send the initial segment request
            message_to_send = json.dumps(SEGMENT_REQUEST)
            logger.info(f"Sending message: {message_to_send}")
            await websocket.send(message_to_send)

            # Listen for responses
            while True:
                try:
                    response = await websocket.recv()
                    logger.info(f"Received response: {response}")

                    # Try to parse as JSON for better formatting
                    try:
                        parsed_response = json.loads(response)
                        print("Response (formatted):")
                        print(json.dumps(parsed_response, indent=2))

                        # Check for score updates first (could be in any response)
                        target_reached = handle_score_update(parsed_response)
                        if target_reached:
                            logger.info("🏆 TARGET SCORE REACHED! Stopping the game...")
                            break

                        # Check if this is a game segment (list of game objects)
                        if (
                            isinstance(parsed_response, list)
                            and len(parsed_response) > 0
                        ):
                            # This is a game segment
                            logger.info(
                                f"Received game segment with {len(parsed_response)} objects"
                            )

                            # Debug: print first few objects to understand server data structure
                            for i, obj in enumerate(parsed_response[:3]):
                                logger.info(f"Object {i + 1}: {obj}")

                            # Parse the segment
                            coins, obstacles = parse_game_segment(parsed_response)
                            logger.info(
                                f"Found {len(coins)} coins and {len(obstacles)} obstacles"
                            )  # Automatically collect all coins
                            if coins:
                                await collect_coins(websocket, coins)

                                # Wait a bit for all responses
                                await asyncio.sleep(1)

                                # Check score again after collecting coins
                                if CURRENT_SCORE >= TARGET_SCORE:
                                    logger.info(
                                        "🏆 TARGET SCORE REACHED after collecting coins! Stopping the game..."
                                    )
                                    break

                                # Request next segment - using game's exact logic
                                logger.info("Requesting next segment...")
                                next_segment_msg = json.dumps(SEGMENT_REQUEST)
                                await websocket.send(next_segment_msg)
                                current_segment += 1

                                # Update distance based on game's segmentSize (30) + random offset
                                segment_distance = 30 + (
                                    current_segment % 5
                                )  # Simulate segmentSizeVariable
                                TOTAL_DISTANCE += segment_distance
                                logger.info(
                                    f"Updated total distance to: {TOTAL_DISTANCE}"
                                )
                            else:
                                # No coins, but still request next segment to keep game flowing
                                logger.info(
                                    "No coins found, requesting next segment..."
                                )
                                next_segment_msg = json.dumps(SEGMENT_REQUEST)
                                await websocket.send(next_segment_msg)
                                current_segment += 1
                                TOTAL_DISTANCE += 30

                        # Check if this is a specific score update message
                        elif isinstance(parsed_response, dict) and (
                            "score" in parsed_response
                            or "total_score" in parsed_response
                        ):
                            logger.info(f"💰 Score update message: {parsed_response}")

                            # Check if game is over
                            if parsed_response.get("is_over", False):
                                logger.info("🎮 Game over signal received!")
                                break

                    except json.JSONDecodeError:
                        print(f"Response (raw): {response}")

                except websockets.exceptions.ConnectionClosed:
                    logger.info("WebSocket connection closed")
                    break
                except Exception as e:
                    logger.error(f"Error receiving message: {e}")
                    break

            # Final score report
            logger.info(f"🏁 Game ended. Final Score: {CURRENT_SCORE}/{TARGET_SCORE}")
            if CURRENT_SCORE >= TARGET_SCORE:
                logger.info("🎉 SUCCESS: Target score achieved!")
            else:
                logger.info("❌ Target score not reached.")

    except websockets.exceptions.InvalidURI:
        logger.error("Invalid WebSocket URI")
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"WebSocket error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def main():
    """Main function to run the WebSocket client"""
    print("🐜 Starting Ant Run WebSocket Client...")
    print(f"🎯 Target Score: {TARGET_SCORE}")
    print("📊 The game will automatically stop when the target score is reached")
    print("Press Ctrl+C to stop manually\n")

    try:
        await connect_websocket()
    except KeyboardInterrupt:
        print(
            f"\n⏹️  WebSocket client stopped by user. Final Score: {CURRENT_SCORE}/{TARGET_SCORE}"
        )
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
