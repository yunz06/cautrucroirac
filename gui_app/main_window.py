import sys
import json
import networkx as nx
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QMessageBox, 
                             QComboBox, QFileDialog, QGroupBox, QInputDialog,
                             QDialog, QTextEdit, QCheckBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont

# Import Canvas vẽ đồ thị
from gui_app.canvas import MapCanvas 

# ============================================================
# IMPORT THUẬT TOÁN (XỬ LÝ LỖI NẾU THIẾU FILE)
# ============================================================
try:
    from algorithms.flow import MaxFlow 
except ImportError: 
    MaxFlow = None
    print("⚠️ Cảnh báo: Không tìm thấy module algorithms/flow.py")

try:
    from algorithms.mst import run_prim, run_kruskal
except ImportError: 
    run_prim, run_kruskal = None, None
    print("⚠️ Cảnh báo: Không tìm thấy module algorithms/mst.py")

try:
    from algorithms.traversal import run_bfs, run_dfs
except ImportError: 
    run_bfs, run_dfs = None, None
    print("⚠️ Cảnh báo: Không tìm thấy module algorithms/traversal.py")

try:
    from algorithms.shortest_path import a_star_search, TrafficGraph
except ImportError: 
    a_star_search, TrafficGraph = None, None
    print("⚠️ Cảnh báo: Không tìm thấy module algorithms/shortest_path.py")

try:
    from algorithms.check_bipartite import check_bipartite
except ImportError: 
    check_bipartite = None
    print("⚠️ Cảnh báo: Không tìm thấy module algorithms/check_bipartite.py")

try:
    from algorithms.euler import find_euler_path
except ImportError: 
    find_euler_path = None
    print("⚠️ Cảnh báo: Không tìm thấy module algorithms/euler.py")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Cấu hình cửa sổ chính
        self.setWindowTitle("UrbanFlow - Hệ thống Phân tích & Tối ưu Lộ trình Giao thông")
        self.setGeometry(100, 100, 1300, 850)
        
        # Khởi tạo Canvas (vùng vẽ)
        self.canvas = MapCanvas()
        
        # Khởi tạo Timer cho Animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_animation_step)
        
        # Các biến lưu trữ trạng thái chạy thuật toán
        self.anim_queue = []          # Hàng đợi các bước animation
        self.current_path_str = []    # Lưu chuỗi log
        self.full_path_result = []    # Lưu kết quả đầy đủ
        
        # Xây dựng giao diện
        self.setup_ui()

    def setup_ui(self):
        """Thiết lập toàn bộ giao diện người dùng"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QHBoxLayout(main_widget)

        # -----------------------------------------------------------
        # CỘT TRÁI: PANEL ĐIỀU KHIỂN
        # -----------------------------------------------------------
        controls_panel = QVBoxLayout()
        controls_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # --- GROUP 1: QUẢN LÝ FILE ---
        file_group = QGroupBox("Quản lý File & Dữ liệu")
        file_layout = QVBoxLayout()
        
        btn_save = QPushButton("💾 Lưu Đồ Thị")
        btn_save.clicked.connect(self.save_graph)
        
        btn_load = QPushButton("📂 Mở Đồ Thị")
        btn_load.clicked.connect(self.load_graph)
        
        btn_clear = QPushButton("🗑️ Xóa Tất Cả")
        btn_clear.clicked.connect(self.clear_graph)
        
        # --- [ĐÃ ĐỔI TÊN NÚT BẤM CHO SANG] ---
        btn_convert = QPushButton("🔄 Số hóa Dữ liệu")
        btn_convert.clicked.connect(self.show_representation_dialog)
        
        file_layout.addWidget(btn_save)
        file_layout.addWidget(btn_load)
        file_layout.addWidget(btn_convert)
        file_layout.addWidget(btn_clear)
        file_group.setLayout(file_layout)
        controls_panel.addWidget(file_group)

        # --- GROUP 2: CÔNG CỤ VẼ ---
        draw_group = QGroupBox("Công cụ Vẽ Đồ Thị")
        draw_layout = QVBoxLayout()
        
        self.chk_directed = QCheckBox("Đường 1chiều/2chiều (Directed)")
        self.chk_directed.setChecked(True) # Mặc định là có hướng
        self.chk_directed.setStyleSheet("color: #f1c40f; font-weight: bold; margin-bottom: 5px;")
        self.chk_directed.toggled.connect(self.toggle_directed)
        draw_layout.addWidget(self.chk_directed)
        
        btn_node = QPushButton("🔴 Vẽ Giao Lộ (Node)")
        btn_node.clicked.connect(lambda: self.canvas.set_mode("draw_node"))
        
        btn_edge = QPushButton("➖ Vẽ Tuyến Đường (Edge)")
        btn_edge.clicked.connect(lambda: self.canvas.set_mode("draw_edge"))
        
        btn_view = QPushButton("👆 Chọn / Di chuyển")
        btn_view.clicked.connect(lambda: self.canvas.set_mode("view"))
        
        draw_layout.addWidget(btn_node)
        draw_layout.addWidget(btn_edge)
        draw_layout.addWidget(btn_view)
        draw_group.setLayout(draw_layout)
        controls_panel.addWidget(draw_group)

        # --- GROUP 3: THUẬT TOÁN ---
        algo_group = QGroupBox("Thuật toán & Phân tích")
        algo_layout = QVBoxLayout()
        
        algo_layout.addWidget(QLabel("Chọn chức năng:"))
        self.algo_selector = QComboBox()
        self.algo_selector.addItems([
            "1. Tìm đường ngắn nhất (Dijkstra/A*)",
            "2. Luồng cực đại (Max Flow)",
            "3. Cây khung nhỏ nhất Prim (MST)",
            "4. Cây khung nhỏ nhất Kruskal (MST)",
            "5. Chu trình Euler (Hierholzer)",
            "6. Duyệt BFS (Theo chiều rộng)",
            "7. Duyệt DFS (Theo chiều sâu)",
            "8. Kiểm tra Đồ thị 2 phía (Bipartite)"
        ])
        self.algo_selector.currentIndexChanged.connect(self.on_algo_change)
        algo_layout.addWidget(self.algo_selector)

        # Khu vực nhập Start / End
        self.input_container = QWidget()
        input_layout = QHBoxLayout(self.input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("ID Bắt đầu")
        self.sink_input = QLineEdit()
        self.sink_input.setPlaceholderText("ID Kết thúc")
        
        input_layout.addWidget(QLabel("Start:"))
        input_layout.addWidget(self.source_input)
        input_layout.addWidget(QLabel("End:"))
        input_layout.addWidget(self.sink_input)
        
        algo_layout.addWidget(self.input_container)

        # Nút chạy
        btn_run = QPushButton("▶️ CHẠY THUẬT TOÁN")
        btn_run.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; 
                color: white; 
                font-weight: bold; 
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_run.clicked.connect(self.run_algorithm)
        algo_layout.addWidget(btn_run)

        # LABEL TRẠNG THÁI (REAL-TIME LOG)
        self.lbl_status = QLabel("Trạng thái: Sẵn sàng")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet("""
            QLabel {
                color: #00ff00; 
                font-weight: bold; 
                font-size: 13px; 
                background-color: #222;
                padding: 5px;
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 10px;
            }
        """)
        algo_layout.addWidget(self.lbl_status)
        
        algo_group.setLayout(algo_layout)
        controls_panel.addWidget(algo_group)

        # Label hướng dẫn
        help_lbl = QLabel("💡 Giữ Shift + Click nút cuối để vẽ cạnh cong.\n🖱️ Chuột phải để kéo tạo cạnh nhanh.")
        help_lbl.setStyleSheet("color: #bbb; font-style: italic; font-size: 11px; margin-top: 10px;")
        controls_panel.addWidget(help_lbl)

        # Thêm Panel vào layout chính
        layout.addLayout(controls_panel, 1) # Tỷ lệ 1
        layout.addWidget(self.canvas, 4)    # Tỷ lệ 4

    # =========================================================================
    # CÁC HÀM XỬ LÝ LOGIC
    # =========================================================================

    def get_clean_adj_list(self, weighted=False, directed=False):
        """Chuyển đổi dữ liệu Canvas sang Danh sách kề chuẩn"""
        n = len(self.canvas.nodes)
        adj = {i: [] for i in range(n)}
        
        for item in self.canvas.edges:
            # Unpack thông minh (bỏ qua is_curved nếu có)
            if len(item) == 4: u, v, w, _ = item
            else: u, v, w = item
            
            # Nếu thuật toán cần trọng số -> lưu tuple (v, w)
            val = (v, float(w)) if weighted else v
            adj[u].append(val)
            
            # Nếu là đồ thị vô hướng, thêm cạnh ngược lại
            if not directed:
                val_rev = (u, float(w)) if weighted else u
                adj[v].append(val_rev)
                
        return adj

    def toggle_directed(self, checked):
        self.canvas.set_graph_type(checked)

    def on_algo_change(self):
        txt = self.algo_selector.currentText()
        # Nhóm cần cả Start và End
        if "ngắn nhất" in txt or "Max Flow" in txt:
            self.input_container.setVisible(True)
            self.source_input.setVisible(True)
            self.sink_input.setVisible(True)
        # Nhóm chỉ cần Start
        elif "BFS" in txt or "DFS" in txt or "Prim" in txt:
            self.input_container.setVisible(True)
            self.source_input.setVisible(True)
            self.sink_input.setVisible(False)
        # Nhóm không cần nhập gì
        else:
            self.input_container.setVisible(False)

    def get_inputs(self, n, need_sink=True):
        try:
            txt_s = self.source_input.text()
            if not txt_s: raise ValueError("Chưa nhập đỉnh Start")
            s = int(txt_s)
            if not (0 <= s < n): raise ValueError(f"Đỉnh Start {s} không tồn tại")
            
            t = None
            if need_sink:
                txt_t = self.sink_input.text()
                if not txt_t: raise ValueError("Chưa nhập đỉnh End")
                t = int(txt_t)
                if not (0 <= t < n): raise ValueError(f"Đỉnh End {t} không tồn tại")
            return s, t
        except ValueError as ve:
            QMessageBox.warning(self, "Lỗi Nhập liệu", str(ve))
            return None, None
        except Exception:
            QMessageBox.warning(self, "Lỗi", "ID đỉnh phải là số nguyên.")
            return None, None

    # =========================================================================
    # HÀM CHẠY THUẬT TOÁN (RUN ALGORITHM)
    # =========================================================================
    def run_algorithm(self):
        try:
            self.canvas.reset_algo_visuals() # Chỉ xóa màu tô
        except AttributeError:
            pass

        self.timer.stop()
        self.anim_queue = []
        self.lbl_status.setText("Đang xử lý...")
        
        algo = self.algo_selector.currentText()
        n = len(self.canvas.nodes)
        
        if n == 0: 
            QMessageBox.warning(self, "Lỗi", "Bản đồ chưa có đỉnh nào!")
            return

        is_directed = self.chk_directed.isChecked()
        G_nx = self.get_nx_graph(weighted=True, directed=is_directed)

        try:
            # 1. TÌM ĐƯỜNG NGẮN NHẤT
            if "ngắn nhất" in algo:
                s, t = self.get_inputs(n, need_sink=True)
                if s is None: return

                try:
                    path = nx.dijkstra_path(G_nx, s, t, weight='weight')
                    cost = nx.dijkstra_path_length(G_nx, s, t, weight='weight')
                    
                    edges_hl = [(path[i], path[i+1]) for i in range(len(path)-1)]
                    self.canvas.highlight_edges = edges_hl
                    self.canvas.update()
                    
                    msg = f"Chi phí: {cost}\nLộ trình: {' -> '.join(map(str, path))}"
                    self.lbl_status.setText(f"Hoàn tất: {msg}")
                    QMessageBox.information(self, "Kết quả (Dijkstra)", msg)
                    
                except nx.NetworkXNoPath:
                    self.lbl_status.setText("Không tìm thấy đường đi.")
                    QMessageBox.warning(self, "Kết quả", "Không có đường đi giữa 2 điểm này.")

            # 2. MAX FLOW
            elif "Max Flow" in algo:
                if not MaxFlow:
                    QMessageBox.warning(self, "Thiếu Module", "Không tìm thấy flow.py")
                    return
                
                s, t = self.get_inputs(n, need_sink=True)
                if s is None: return
                
                matrix = [[0]*n for _ in range(n)]
                capacity_matrix = [[0]*n for _ in range(n)]

                for item in self.canvas.edges:
                    if len(item) == 4: u, v, w, _ = item
                    else: u, v, w = item
                    
                    matrix[u][v] = int(w)
                    capacity_matrix[u][v] = int(w)
                    if not is_directed: 
                        matrix[v][u] = int(w)
                        capacity_matrix[v][u] = int(w)

                mf = MaxFlow(matrix)
                max_val, flow_mat = mf.ford_fulkerson(s, t)
                
                hl = []
                self.canvas.custom_edge_labels = {} # Reset nhãn

                for u in range(n):
                    for v in range(n):
                        f = flow_mat[u][v]
                        c = capacity_matrix[u][v]
                        if c > 0: # Có cạnh
                            if f > 0: hl.append((u, v))
                            self.canvas.custom_edge_labels[(u, v)] = f"{f}/{c}"
                
                self.canvas.highlight_edges = hl
                self.canvas.update()
                
                self.lbl_status.setText(f"Max Flow: {max_val}")
                QMessageBox.information(self, "Kết quả Max Flow", f"Luồng cực đại: {max_val}")

            # 3 & 4. MST (Prim/Kruskal)
            elif "Prim" in algo or "Kruskal" in algo:
                if not (run_prim and run_kruskal):
                    QMessageBox.warning(self, "Thiếu Module", "Không tìm thấy mst.py")
                    return
                
                adj_w = self.get_clean_adj_list(weighted=True, directed=False)
                
                if not nx.is_connected(G_nx.to_undirected()):
                      QMessageBox.warning(self, "Lỗi", "Đồ thị không liên thông, không thể tìm cây khung!")
                      return
                
                if "Prim" in algo:
                    mst_edges, total = run_prim(adj_w)
                    name = "Prim"
                else:
                    mst_edges, total = run_kruskal(adj_w)
                    name = "Kruskal"
                
                self.canvas.highlight_edges = mst_edges
                self.canvas.update()
                
                self.lbl_status.setText(f"{name}: Tổng trọng số {total}")
                QMessageBox.information(self, "Kết quả MST", f"Thuật toán {name}\nTổng trọng số: {total}")

            # 5. EULER
            elif "Euler" in algo:
                if not find_euler_path:
                    QMessageBox.warning(self, "Thiếu Module", "Không tìm thấy euler.py")
                    return
                
                adj = self.get_clean_adj_list(weighted=False, directed=is_directed)
                path = find_euler_path(adj)
                
                if path:
                    self.anim_queue = list(path)
                    self.full_path_result = list(path)
                    self.current_path_str = []
                    self.canvas.highlight_edges = []
                    self.lbl_status.setText("Xe đang chạy Euler...")
                    
                    # Đặt xe vào vị trí đầu
                    self.canvas.car_position = path[0]
                    self.canvas.update()
                    self.timer.start(600)
                else:
                    self.lbl_status.setText("Không có chu trình Euler.")
                    QMessageBox.warning(self, "Lỗi Euler", "Vi phạm điều kiện Euler (Bậc lẻ/Mất cân bằng).")

            # 6 & 7. BFS / DFS
            elif "BFS" in algo or "DFS" in algo:
                if not (run_bfs and run_dfs):
                    QMessageBox.warning(self, "Thiếu Module", "Không tìm thấy traversal.py")
                    return
                
                s, _ = self.get_inputs(n, need_sink=False)
                if s is None: return
                
                adj = self.get_clean_adj_list(weighted=False, directed=is_directed)
                
                if "BFS" in algo:
                    path = run_bfs(adj, s)
                    name = "BFS"
                else:
                    path = run_dfs(adj, s)
                    name = "DFS"
                
                self.anim_queue = list(path)
                self.full_path_result = list(path)
                self.current_path_str = []
                self.canvas.visited_nodes = []
                
                self.lbl_status.setText(f"Đang chạy {name}...")
                self.timer.start(800)

            # 8. BIPARTITE
            elif "2 phía" in algo:
                if not check_bipartite:
                    QMessageBox.warning(self, "Thiếu Module", "Không tìm thấy check_bipartite.py")
                    return
                
                adj = self.get_clean_adj_list(weighted=False, directed=False)
                is_bi, color_map = check_bipartite(adj)
                
                if is_bi:
                    self.lbl_status.setText("✅ Đồ thị 2 phía")
                    QMessageBox.information(self, "Kết quả", "LÀ đồ thị 2 phía.")
                else:
                    self.lbl_status.setText("❌ Không phải 2 phía")
                    QMessageBox.warning(self, "Kết quả", "KHÔNG phải đồ thị 2 phía.")

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Lỗi Runtime", str(e))

    # =========================================================================
    # ANIMATION
    # =========================================================================
    def on_animation_step(self):
        algo = self.algo_selector.currentText()
        
        # Euler Animation
        if "Euler" in algo:
            if len(self.anim_queue) > 1:
                u = self.anim_queue.pop(0)
                v = self.anim_queue[0]
                
                self.canvas.highlight_edges.append((u, v))
                self.canvas.car_position = v # Cập nhật vị trí xe
                self.canvas.update()
                
                self.lbl_status.setText(f"Xe đi qua: {u} -> {v}")
            else:
                self.timer.stop()
                path_str = " -> ".join(map(str, self.full_path_result))
                QMessageBox.information(self, "Thành công", f"Lộ trình Euler:\n{path_str}")
        
        # BFS/DFS Animation
        elif "BFS" in algo or "DFS" in algo:
            if self.anim_queue:
                node = self.anim_queue.pop(0)
                self.canvas.visited_nodes.append(node)
                self.canvas.update()
                
                self.current_path_str.append(str(node))
                self.lbl_status.setText(f"Duyệt: {' -> '.join(self.current_path_str)}")
            else:
                self.timer.stop()
                final_text = " -> ".join(map(str, self.full_path_result))
                QMessageBox.information(self, "Duyệt Xong", f"Thứ tự:\n{final_text}")

    # =========================================================================
    # CÁC HÀM PHỤ TRỢ (NETWORKX, DIALOG...)
    # =========================================================================
    def get_nx_graph(self, weighted=False, directed=False):
        G = nx.DiGraph() if directed else nx.Graph()
        for i in range(len(self.canvas.nodes)):
            G.add_node(i)
        for item in self.canvas.edges:
            if len(item) == 4: u, v, w, _ = item
            else: u, v, w = item
            
            if weighted: G.add_edge(u, v, weight=int(w))
            else: G.add_edge(u, v)
        return G

    def show_representation_dialog(self):
        n = len(self.canvas.nodes)
        if n == 0: return
        is_directed = self.chk_directed.isChecked()
        
        adj_list = self.get_clean_adj_list(weighted=True, directed=is_directed)
        adj_matrix = [[0]*n for _ in range(n)]
        
        for u, neighbors in adj_list.items():
            for v, w in neighbors:
                adj_matrix[u][v] = int(w)
        
        # 1. Ma trận kề
        txt = "--- MA TRẬN KỀ (Adjacency Matrix) ---\n"
        txt += "\n".join([" ".join(f"{x:3}" for x in row) for row in adj_matrix])
        
        # 2. Danh sách kề
        txt += "\n\n--- DANH SÁCH KỀ (Adjacency List) ---\n"
        for k, v in adj_list.items():
            txt += f"Node {k}: {v}\n"

        # 3. Danh sách cạnh (Mới thêm)
        txt += "\n\n--- DANH SÁCH CẠNH (Edge List) ---\n"
        txt += "Format: (Nguồn, Đích, Trọng số)\n"
        edge_list_str = []
        for item in self.canvas.edges:
            # item có thể là (u, v, w) hoặc (u, v, w, is_curved)
            if len(item) >= 3:
                u, v, w = item[0], item[1], item[2]
                edge_list_str.append(f"({u}, {v}, {w})")
        
        txt += "\n".join(edge_list_str)
            
        dlg = QDialog(self)
        dlg.setWindowTitle("Số hóa Dữ liệu Đồ thị")
        dlg.resize(600, 600)
        box = QVBoxLayout()
        edit = QTextEdit()
        edit.setPlainText(txt)
        edit.setFont(QFont("Courier New", 10))
        box.addWidget(edit)
        dlg.setLayout(box)
        dlg.exec()

    def save_graph(self):
        path, _ = QFileDialog.getSaveFileName(self, "Lưu File", "", "JSON Files (*.json)")
        if path:
            # Lưu y nguyên data từ canvas (có 4 tham số)
            data = {
                "nodes": [list(n) for n in self.canvas.nodes],
                "edges": [list(e) for e in self.canvas.edges],
                "directed": self.chk_directed.isChecked()
            }
            try:
                with open(path, 'w') as f: json.dump(data, f)
                QMessageBox.information(self, "Thành công", "Đã lưu file!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def load_graph(self):
        path, _ = QFileDialog.getOpenFileName(self, "Mở File", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, 'r') as f: data = json.load(f)
                
                self.canvas.clear_map()
                self.canvas.nodes = [tuple(n) for n in data["nodes"]]
                
                new_edges = []
                for e in data["edges"]:
                    if len(e) == 3:
                        new_edges.append((e[0], e[1], e[2], False)) # Mặc định thẳng
                    else:
                        new_edges.append(tuple(e))
                
                self.canvas.edges = new_edges
                is_dir = data.get("directed", True)
                self.chk_directed.setChecked(is_dir)
                self.canvas.set_graph_type(is_dir)
                self.canvas.update()
                QMessageBox.information(self, "Thành công", "Đã tải đồ thị!")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def clear_graph(self):
        confirm = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa toàn bộ bản đồ không?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.canvas.clear_map()
            self.lbl_status.setText("Đã xóa tất cả.")