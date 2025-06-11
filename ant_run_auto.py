import asyncio
import base64
import json
import logging
import random
import urllib.parse

import httpx
import websockets

# Set up logging for debugging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variables
PASSWORD = ""
PHONE = ""  # Replace with your actual phone number
SIGNATURE = ""  # Base signature from the original URI

TARGET_SCORE = random.randint(160, 200)  # Target score to reach in the game
CURRENT_SCORE = 0  # Track current score


def generate_signature():
    """Generate signature following the game's JavaScript logic"""
    # The JavaScript does: decodeURIComponent(signatureParam) then btoa(signEncodeUrl)
    # Since we already have the base signature, we simulate the same process
    try:
        # URL decode the signature (in case it was URL encoded)
        sign_encode_url = urllib.parse.unquote(SIGNATURE)
        # Base64 encode it (like btoa in JavaScript)
        sign_base64 = base64.b64encode(sign_encode_url.encode()).decode()
        return sign_base64
    except Exception as e:
        logger.warning(f"Error generating signature: {e}, using base signature")
        return SIGNATURE


def build_websocket_url():
    """Build WebSocket URL with generated signature"""
    signature = generate_signature()
    ua = "android"  # Following the game's logic for non-iOS

    url = (
        f"wss://api-game.cellphones.com.vn/ws/ant_run"
        f"?game_code=ant_run"
        f"&token={TOKEN}"
        f"&signature={urllib.parse.quote(signature)}"
        f"&phone={PHONE}"
        f"&ua={ua}"
    )
    return url


TOKEN = ""
WS_URL = ""
CHECKIN_API_URL = (
    "https://api.cellphones.com.vn/minigame-flip-card/tasks?game_code=ant_run"
)

# Messages
SEGMENT_REQUEST = {"segment_gen": True}
TOTAL_DISTANCE = 0.0  # Track total distance traveled like the game does


async def checkin_tasks():
    """Checkin tasks before starting the game"""
    try:
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "android",
        }

        logger.info("🔄 Checking in tasks before starting game...")

        async with httpx.AsyncClient() as client:
            response = await client.get(CHECKIN_API_URL, headers=headers)

            if response.status_code == 200:
                logger.info("✅ Task checkin successful!")
                try:
                    task_data = response.json()
                    logger.info(f"📋 Task data: {json.dumps(task_data, indent=2)}")
                except json.JSONDecodeError:
                    logger.info(f"📋 Task response: {response.text}")
                return True
            else:
                logger.warning(
                    f"⚠️ Task checkin failed with status {response.status_code}: {response.text}"
                )
                return False

    except httpx.RequestError as e:
        logger.error(f"❌ HTTP request error during task checkin: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during task checkin: {e}")
        return False


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


# Load configuration from JSON file
def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error("Configuration file 'config.json' not found.")
        return []


async def run_websocket_client():
    """Run the WebSocket client with the current configuration."""
    try:
        checkin_success = await checkin_tasks()
        if not checkin_success:
            logger.error("❌ Task checkin failed. Exiting.")
            return

        await connect_websocket()
    except KeyboardInterrupt:
        print(
            f"\n⏹️  WebSocket client stopped by user. Final Score: {CURRENT_SCORE}/{TARGET_SCORE}"
        )
    except Exception as e:
        logger.error(f"Error in run_websocket_client: {e}")


async def login(phone, password):
    """Perform login to get the token."""
    url = "https://api.smember.com.vn/sso/v1/auth/login"
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://smember.com.vn",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://smember.com.vn/",
        "sec-ch-ua": '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        "x-client-type": "web",
    }
    data = {"phone": phone, "password": password}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json().get("data", {}).get("token")
            else:
                logger.error(
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                return None
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return None


# Main function to run the WebSocket client for each account
async def main():
    """Main function to run the WebSocket client for each account"""
    global PHONE, PASSWORD, SIGNATURE, TOKEN, WS_URL
    print("🐜 Starting Ant Run WebSocket Client...")
    print(f"🎯 Target Score: {TARGET_SCORE}")
    print("📊 The game will automatically stop when the target score is reached")
    print("Press Ctrl+C to stop manually\n")

    if PHONE and PASSWORD and SIGNATURE:
        TOKEN = await login(PHONE, PASSWORD)
        if not TOKEN:
            logger.error(f"Failed to get token for account {PHONE}. Exiting.")
            return
        # Rebuild WebSocket URL for global configuration
        WS_URL = build_websocket_url()
        await run_websocket_client()
    else:
        configs = load_config()
        if not configs:
            logger.error(
                "No configurations found and global configuration is incomplete. Exiting."
            )
            return

        for config in configs:
            PHONE = config.get("phone", "")
            SIGNATURE = config.get("signature", "")
            PASSWORD = config.get("password", "")

            if not PHONE or not SIGNATURE or not PASSWORD:
                logger.warning(f"Missing configuration for account {PHONE}. Skipping.")
                continue

            # Perform login to get the token
            TOKEN = await login(PHONE, PASSWORD)
            if not TOKEN:
                logger.error(f"Failed to get token for account {PHONE}. Skipping.")
                continue

            # Rebuild WebSocket URL for each configuration
            WS_URL = build_websocket_url()
            await run_websocket_client()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
