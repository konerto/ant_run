# 🐜 Ant Run WebSocket Client

An automated Python WebSocket client for the Ant Run game that connects to the game server, automatically collects coins, and manages game state with customizable target scoring.

## 🎯 Features

- **Automated Gameplay**: Connects to the Ant Run game server and plays automatically
- **Smart Coin Collection**: Analyzes game segments and collects all available coins/cookies
- **Target Score System**: Automatically stops when a configurable target score is reached
- **Accurate Game Physics**: Uses exact calculations reverse-engineered from the game's JavaScript code
- **Real-time Logging**: Comprehensive logging of game actions, score progress, and server responses
- **Comprehensive Testing**: Offline simulation framework with real server data validation
- **Error Handling**: Robust WebSocket connection management and error recovery
- **Score Progress Tracking**: Real-time score updates in Current/Target format

## 📋 Requirements

- Python 3.7+
- `websockets` library
- Valid authentication token and phone number for the game server

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd d:\ant_run

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit `websocket_client.py` and update these variables:

```python
TOKEN = "your_actual_token_here"  # Replace with your game token
PHONE = "your_phone_number"       # Replace with your phone number
TARGET_SCORE = 200                # Set your desired target score
```

### 3. Run the Client

```bash
python websocket_client.py
```

## 🎮 How It Works

### Game Flow
1. **Connection**: Establishes WebSocket connection to the game server
2. **Segment Request**: Requests game segments containing coins and obstacles
3. **Parsing**: Analyzes segment data to identify collectible items
4. **Collection**: Automatically sends collect actions for all coins/cookies
5. **Progress Tracking**: Updates score and distance traveled
6. **Target Check**: Monitors score progress and stops when target is reached

### Key Calculations
The client uses exact calculations reverse-engineered from the game's JavaScript:

- **Player Position**: `pz_pos = totalDistance - 7`
- **Lane Mapping**: `-1 → x=-175, 0 → x=0, 1 → x=175`
- **Y Position**: `y_pos = 1 if y > 0 else 0`
- **Distance Progression**: Base segment size of 30 units plus variable offset

## 📁 Project Structure

```
d:\ant_run\
├── websocket_client.py      # Main WebSocket client script
├── game_simulation.py       # Simulation and testing framework
├── test_target_score.py     # Target score functionality tests
├── requirements.txt         # Python dependencies
├── game-control-v33.js     # Original game JavaScript (for reference)
├── game_log                # Server communication logs
├── venv\                   # Python virtual environment
└── README.md               # This file
```

## 🔧 Configuration Options

### Target Score System
```python
TARGET_SCORE = 200    # Game will stop when this score is reached
CURRENT_SCORE = 0     # Tracks current score (automatically updated)
```

### WebSocket URL Parameters
- `game_code`: Game identifier ("ant_run")
- `token`: Authentication token (required)
- `signature`: Game signature (pre-configured)
- `phone`: Phone number (required)
- `ua`: User agent ("android")

## 📊 Logging and Debug Information

The client provides detailed logging:

- **Connection Status**: WebSocket connection events
- **Game Progress**: Score updates in format `Current/Target` (e.g., "45/200")
- **Coin Collection**: Details of each collect action sent
- **Server Responses**: Raw and formatted server messages
- **Distance Tracking**: Total distance traveled updates
- **Target Achievement**: Clear notification when target score is reached

### Sample Output
```
2024-12-31 14:30:15 - INFO - 🐜 Starting Ant Run WebSocket Client...
2024-12-31 14:30:15 - INFO - 🎯 Target Score: 200
2024-12-31 14:30:15 - INFO - 📊 The game will automatically stop when the target score is reached
2024-12-31 14:30:16 - INFO - Connecting to WebSocket: wss://api-game.cellphones.com.vn/ws/ant_run...
2024-12-31 14:30:16 - INFO - Connected successfully!
2024-12-31 14:30:17 - INFO - Received game segment with 8 objects
2024-12-31 14:30:17 - INFO - Found 5 coins and 3 obstacles
2024-12-31 14:30:17 - INFO - 💰 Starting to collect 5 coins (Score: 0/200)
2024-12-31 14:30:18 - INFO - 📊 Score Update: 45/200
2024-12-31 14:30:20 - INFO - 🎯 TARGET SCORE REACHED! Current: 205, Target: 200
2024-12-31 14:30:20 - INFO - 🏆 SUCCESS: Target score achieved!
2024-12-31 14:30:20 - INFO - Final Score: 205 (Target: 200) ✅
```

## 🧪 Testing and Simulation

### Game Simulation
Run `game_simulation.py` for offline testing:

```bash
python game_simulation.py
```

Features:
- Mock game sessions with realistic data
- Distance calculation validation
- Real server data analysis
- Game mechanics testing without WebSocket connection

### Target Score Testing
Run `test_target_score.py` to test the target score functionality:

```bash
python test_target_score.py
```

## 🔍 Technical Details

### Reverse Engineering
The client's accuracy comes from analyzing the original game's JavaScript code (`game-control-v33.js`):

- **Message Format**: `{action, lane, z_pos, pz_pos, y_pos, segment_id}`
- **Distance Calculation**: Uses `this.totalDistance - 7` for `pz_pos`
- **Object Detection**: Handles "coin", "cookie", and "obstacle" types
- **Segment Management**: Tracks segment IDs and progression

### Server Communication
- **Outbound**: Segment requests and collect actions
- **Inbound**: Game segments, score updates, and game state
- **Protocol**: JSON messages over WebSocket (WSS)

### Error Handling
- WebSocket connection failures
- Invalid server responses
- Authentication errors
- Network timeouts

## 🛠️ Customization

### Modify Target Score
```python
TARGET_SCORE = 500  # Set higher target for longer gameplay
```

### Adjust Collection Delays
```python
await asyncio.sleep(0.1)  # Delay between collect actions (in seconds)
```

### Enable/Disable Logging
```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
logging.basicConfig(level=logging.WARNING)  # Less verbose
```

## 🚨 Important Notes

### Authentication
- Ensure your `TOKEN` and `PHONE` are valid and authorized
- Tokens may expire and need renewal
- Invalid credentials will result in connection failures

### Rate Limiting
- The server may have rate limits on actions
- Built-in delays help prevent throttling
- Monitor server responses for rate limit warnings

### Game Rules
- Some servers may detect automated play
- Use responsibly and in accordance with game terms
- The client mimics human-like behavior patterns

## 🐛 Troubleshooting

### Common Issues

**Connection Failed**
```
Error: Invalid WebSocket URI
```
- Check your TOKEN and PHONE values
- Verify internet connection
- Ensure the game server is accessible

**No Coins Collected**
```
Found 0 coins and 0 obstacles
```
- Server may not be sending game segments
- Check authentication status
- Verify segment request format

**Target Score Not Reached**
```
❌ Target score not reached
```
- Increase TARGET_SCORE value
- Check if game ended prematurely
- Review server responses for errors

### Debug Steps
1. Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
2. Check raw server responses in console output
3. Verify WebSocket connection establishment
4. Monitor score update messages
5. Review game_log file for detailed communication

## 📝 License

This project is for educational and research purposes. Please ensure compliance with the game's terms of service before use.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes with the simulation framework
4. Submit a pull request with detailed descriptions

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the game_log for server communication details
3. Test with the simulation framework first
4. Ensure all requirements are properly installed

---

**Happy Gaming! 🎮🐜**
