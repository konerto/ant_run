# 🐜 Ant Run Auto - Hướng Dẫn Sử Dụng

Bot tự động chơi game Ant Run của CellphoneS, kết nối WebSocket và thu thập điểm số một cách tự động.

## 🎯 Tính Năng

- **Chơi Tự Động**: Kết nối server game và chơi tự động
- **Thu Thập Xu**: Tự động phân tích và thu thập tất cả xu/cookie trong game
- **Dừng Theo Mục Tiêu**: Tự động dừng khi đạt điểm số mong muốn
- **Tính Toán Chính Xác**: Sử dụng công thức từ mã nguồn JavaScript gốc của game
- **Theo Dõi Real-time**: Log chi tiết các hành động và tiến trình điểm số
- **Xử Lý Lỗi**: Quản lý kết nối WebSocket ổn định
- **Hiển Thị Tiến Trình**: Cập nhật điểm số theo format Hiện Tại/Mục Tiêu

## 📋 Yêu Cầu

- Python 3.7 trở lên
- Thư viện `websockets` và `httpx`
- Token xác thực và số điện thoại hợp lệ

## 🚀 Hướng Dẫn Nhanh

### 1. Cài Đặt

```bash
# Tải project về
cd d:\ant_run

# Tạo môi trường ảo (khuyến nghị)
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows:
venv\Scripts\activate

# Cài đặt thư viện cần thiết
pip install -r requirements.txt
```

### 2. Cấu Hình

Mở file `ant_run_auto.py` và cập nhật các thông tin sau:

```python
TOKEN = "token_của_bạn"     # Thay bằng token thật
PHONE = "số_điện_thoại"     # Thay bằng số điện thoại của bạn
TARGET_SCORE = 200          # Đặt điểm số mục tiêu
BASE_SIGNATURE = "signature" # Thay bằng signature từ URI gốc
```

### 3. Chạy Bot

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
