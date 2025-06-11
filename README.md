# Ant Run WebSocket Client

## Giới thiệu
Ant Run WebSocket Client là một ứng dụng tự động chơi trò chơi Ant Run thông qua kết nối WebSocket. Ứng dụng này được thiết kế để tự động thu thập điểm và đạt được điểm số mục tiêu.

## Cài đặt
1. Đảm bảo bạn đã cài đặt Python 3.7 trở lên.
2. Cài đặt các thư viện cần thiết bằng cách chạy lệnh sau:
   ```bash
   pip install -r requirements.txt
   ```

## Cấu hình
Trước khi chạy ứng dụng, bạn cần cập nhật các thông tin sau trong tệp `ant_run_auto.py`:
- `TOKEN`: Thay thế bằng mã thông báo thực tế của bạn.
- `PHONE`: Thay thế bằng số điện thoại thực tế của bạn.
- `SIGNATURE`: Thay thế bằng chữ ký cơ sở thực tế của bạn.

### Cấu hình nhiều tài khoản
Bạn có thể sử dụng tệp `config.json` để cấu hình nhiều tài khoản. Tệp này nên chứa một mảng các đối tượng, mỗi đối tượng có các trường `token`, `phone`, và `signature`. Ví dụ:
```json
[
    {
        "token": "your_token_here",
        "phone": "your_phone_here",
        "signature": "your_signature_here"
    },
    {
        "token": "another_token_here",
        "phone": "another_phone_here",
        "signature": "another_signature_here"
    }
]
```

## Sử dụng
Chạy ứng dụng bằng lệnh sau:
```bash
python ant_run_auto.py
```

## Tính năng
- Tự động kết nối đến WebSocket và gửi yêu cầu để bắt đầu trò chơi.
- Tự động thu thập điểm và kiểm tra điểm số mục tiêu.
- Dừng trò chơi khi đạt được điểm số mục tiêu.

## Ghi chú
- Đảm bảo rằng bạn có kết nối internet ổn định để tránh các lỗi kết nối.
- Nếu bạn gặp bất kỳ vấn đề nào, hãy kiểm tra nhật ký để biết thêm thông tin chi tiết.
