#File chạy chính ( kết nối giao diện & thuật toán )

import sys
import traceback

# Kiểm tra xem máy đã cài PyQt6 chưa để báo lỗi dễ hiểu hơn
try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    print("❌ LỖI: Chưa cài đặt thư viện PyQt6.")
    print("👉 Vui lòng chạy lệnh: pip install -r requirements.txt")
    sys.exit(1)

# Import giao diện chính từ thư mục gui_app
try:
    from gui_app.main_window import MainWindow
except ImportError as e:
    print(f"❌ LỖI IMPORT: {e}")
    sys.exit(1)

def main():
    # 1. Khởi tạo ứng dụng Qt
    app = QApplication(sys.argv)
    
    # 2. Thiết lập thông tin ứng dụng
    app.setApplicationName("UrbanFlow")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Nhom_F_GTVT")

    # 3. Khởi tạo và hiển thị cửa sổ chính
    # Bọc trong try-except để nếu code lỗi thì nó in ra màn hình đen (console) cho dễ sửa
    try:
        window = MainWindow()
        window.show()
        
        print("✅ Ứng dụng UrbanFlow đã khởi động thành công!")
        
        # 4. Bắt đầu vòng lặp sự kiện (Giữ cho cửa sổ luôn mở)
        sys.exit(app.exec())
        
    except Exception:
        print("❌ CÓ LỖI XẢY RA KHI CHẠY ỨNG DỤNG:")
        traceback.print_exc()

if __name__ == "__main__":
    main()