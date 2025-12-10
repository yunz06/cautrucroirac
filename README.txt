========================================================================
   URBANFLOW - HỆ THỐNG PHÂN TÍCH VÀ TỐI ƯU LỘ TRÌNH GIAO THÔNG THÔNG MINH
========================================================================

1. THÔNG TIN CHUNG
------------------
- Môn học: Cấu trúc rời rạc / Lý thuyết đồ thị
- Nhóm thực hiện: Nhóm F
- Thành viên:
  1. [Phan Gia Kiệt] - [077206002235]
  2. [Lê Vũ Khánh Nguyên] - [077206007297]
  3. [Nguyễn Đức Thiện] - [075206018130]
  4. [Nguyễn Tiến Phát Đạt] - [060206013686]
  5. [Trần Hoàng Thông] - [075206008044]
  6. [Huỳnh Nguyễn Anh Kiệt] - [075206003158]

2. GIỚI THIỆU
-------------
UrbanFlow là ứng dụng phần mềm mô phỏng mạng lưới giao thông đô thị dưới dạng đồ thị (Graph). 
Ứng dụng cung cấp các công cụ trực quan để thiết kế bản đồ, phân tích luồng giao thông và áp dụng các thuật toán tối ưu hóa lộ trình.

3. YÊU CẦU HỆ THỐNG
-------------------
- Ngôn ngữ lập trình: Python (Phiên bản 3.8 trở lên)
- Thư viện giao diện: PyQt6
- Thư viện thuật toán: NetworkX

4. HƯỚNG DẪN CÀI ĐẶT
--------------------
Bước 1: Cài đặt Python (nếu chưa có).
Bước 2: Mở Terminal/Command Prompt tại thư mục chứa source code.
Bước 3: Cài đặt các thư viện cần thiết bằng lệnh:
   
   pip install -r requirements.txt

(Hoặc cài thủ công: pip install PyQt6 networkx)

5. HƯỚNG DẪN SỬ DỤNG
--------------------
Chạy file chính để khởi động ứng dụng:

   python main.py

* Các thao tác cơ bản trên bản đồ:
  - Thêm Giao Lộ (Nút): Giữ phím CTRL + Click Chuột Trái (hoặc chọn công cụ "Vẽ Đỉnh").
  - Nối Đường (Cạnh): Click Chuột Phải vào nút bắt đầu, giữ và kéo đến nút kết thúc.
  - Di chuyển: Chọn công cụ "Di chuyển", bấm giữ chuột trái vào nút và kéo.
  - Sửa Trọng Số (Độ dài/Tắc đường): Double Click (nhấp đúp) vào con số trên đường nối.

6. CÁC TÍNH NĂNG CHÍNH (THUẬT TOÁN)
-----------------------------------
A. Chức năng Cơ bản:
   - Vẽ, chỉnh sửa, lưu và mở bản đồ giao thông (định dạng JSON).
   - Chuyển đổi biểu diễn dữ liệu: Ma trận kề <-> Danh sách kề <-> Danh sách cạnh.

B. Phân tích & Tối ưu:
   1. Tìm đường đi ngắn nhất (Dijkstra):
      - Ứng dụng: Mô phỏng GPS, tìm lộ trình nhanh nhất từ điểm A đến B.
   
   2. Luồng cực đại (Max Flow - Edmonds-Karp/Ford-Fulkerson):
      - Ứng dụng: Tính toán năng lực thông hành của tuyến đường, xác định điểm nghẽn (nút thắt cổ chai).

   3. Cây khung nhỏ nhất (MST - Prim/Kruskal):
      - Ứng dụng: Tối ưu hóa chi phí xây dựng hạ tầng (cáp quang, đường ống) kết nối các điểm.

   4. Chu trình Euler (Fleury/Hierholzer):
      - Ứng dụng: Lập lộ trình cho xe dịch vụ (quét đường, thu gom rác) đi qua mọi con đường đúng 1 lần.

   5. Duyệt & Kiểm tra (BFS/DFS/Bipartite):
      - Ứng dụng: Rà soát khu vực, kiểm tra tính liên thông và phân lớp mạng lưới.

7. CẤU TRÚC THƯ MỤC
-------------------
source code/
 ├── main.py                # File chạy chính
 ├── requirements.txt       # Danh sách thư viện
 ├── gui_app/               # Giao diện người dùng (UI)
 │    ├── main_window.py    # Cửa sổ chính & Xử lý logic sự kiện
 │    └── canvas.py         # Màn hình vẽ đồ thị
 ├── algorithms/            # Các module thuật toán
 │    ├── flow.py           # Ford-Fulkerson
 │    └── ...
 ├── core/                  # Cấu trúc dữ liệu lõi
 

========================================================================