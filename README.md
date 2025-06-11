# Ant Run WebSocket Client

## Giới thiệu
Ant Run WebSocket Client là một ứng dụng tự động chơi trò chơi Ant Run thông qua kết nối WebSocket. Ứng dụng này được thiết kế để tự động thu thập điểm và đạt được điểm số mục tiêu ngẫu nhiên từ 160-200 điểm.

## Tính năng chính
- **Đăng nhập tự động**: Tự động lấy token thông qua đăng nhập bằng số điện thoại và mật khẩu
- **Hỗ trợ nhiều tài khoản**: Chạy tuần tự cho nhiều tài khoản từ file cấu hình
- **Điểm số ngẫu nhiên**: Mục tiêu điểm số được tạo ngẫu nhiên từ 160-200 mỗi lần chạy
- **Thu thập xu tự động**: Phân tích và thu thập tất cả xu/cookie trong game
- **Xử lý lỗi toàn diện**: Tiếp tục với tài khoản tiếp theo nếu một tài khoản gặp lỗi
- **Logging chi tiết**: Theo dõi tiến trình và kết quả cho từng tài khoản

## Cài đặt
1. Đảm bảo bạn đã cài đặt Python 3.7 trở lên.
2. Cài đặt các thư viện cần thiết bằng cách chạy lệnh sau:
   ```bash
   pip install -r requirements.txt
   ```

## Cấu hình

### Cách 1: Sử dụng cấu hình toàn cục
Cập nhật các biến toàn cục trong tệp `ant_run_auto.py`:
```python
PASSWORD = "your_password_here"
PHONE = "your_phone_here" 
SIGNATURE = "your_signature_here"
```

### Cách 2: Sử dụng file cấu hình cho nhiều tài khoản (Khuyến nghị)
Tạo hoặc cập nhật tệp `config.json` với định dạng sau:
```json
[
    {
        "phone": "0855801178",
        "password": "your_password_here",
        "signature": "WmhOU51DV8SAbtSbIfpEikqAjBJTy3OTdKv8dhEapd4="
    },
    {
        "phone": "0785021097", 
        "password": "another_password_here",
        "signature": "QcioHJozpzgq/jf3/2tblQhJxLLHTClJ6Gx7tKZuFoE="
    }
]
```

### Lấy thông tin cấu hình
- **phone**: Số điện thoại tài khoản CellphoneS
- **password**: Mật khẩu tài khoản
- **signature**: Lấy từ request WebSocket của trình duyệt khi chơi game

## Sử dụng
Chạy ứng dụng bằng lệnh sau:
```bash
python ant_run_auto.py
```

## Luồng hoạt động
1. **Kiểm tra cấu hình**: Ưu tiên sử dụng biến toàn cục, nếu không có thì đọc từ `config.json`
2. **Đăng nhập tự động**: Gọi API đăng nhập để lấy token cho mỗi tài khoản
3. **Checkin nhiệm vụ**: Thực hiện checkin trước khi bắt đầu game
4. **Kết nối WebSocket**: Thiết lập kết nối và bắt đầu game
5. **Thu thập xu**: Tự động phân tích segment và thu thập xu/cookie
6. **Theo dõi điểm số**: Dừng khi đạt điểm số mục tiêu
7. **Chuyển tài khoản**: Tiếp tục với tài khoản tiếp theo (nếu có)

## Tính năng nâng cao
- **Xử lý lỗi thông minh**: Bỏ qua tài khoản lỗi và tiếp tục với tài khoản khác
- **Tính toán chính xác**: Sử dụng công thức từ mã nguồn JavaScript gốc của game
- **Logging chi tiết**: Hiển thị tiến trình điểm số theo format "Hiện tại/Mục tiêu"
- **Quản lý kết nối**: Tự động xử lý mất kết nối và lỗi WebSocket

## Ghi chú quan trọng
- **Kết nối ổn định**: Đảm bảo kết nối internet ổn định để tránh lỗi
- **Thông tin chính xác**: Kiểm tra phone, password và signature trước khi chạy
- **Checkin bắt buộc**: Nếu checkin thất bại, ứng dụng sẽ dừng cho tài khoản đó
- **Sử dụng có trách nhiệm**: Tuân thủ điều khoản sử dụng của game

## Xử lý sự cố
- **Lỗi đăng nhập**: Kiểm tra phone/password trong cấu hình
- **Lỗi checkin**: Đảm bảo tài khoản có quyền truy cập game
- **Lỗi kết nối**: Kiểm tra kết nối internet và firewall
- **Lỗi signature**: Lấy lại signature mới từ trình duyệt
