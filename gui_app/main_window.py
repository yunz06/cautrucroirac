import sys
import json
import networkx as nx
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QMessageBox, 
                             QComboBox, QFileDialog, QGroupBox, QInputDialog,
                             QDialog, QTextEdit, QCheckBox) # <--- Thêm QCheckBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont

from gui_app.canvas import MapCanvas 
from algorithms.flow import MaxFlow 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UrbanFlow - Hệ thống Phân tích Giao thông Thông minh")
        self.setGeometry(100, 100, 1250, 800)
        
        self.canvas = MapCanvas()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_animation_step)
        self.anim_queue = [] 
        
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # --- CỘT TRÁI ---
        controls_panel = QVBoxLayout()
        controls_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 1. Quản lý File
        file_group = QGroupBox("Quản lý")
        file_layout = QVBoxLayout()
        btn_save = QPushButton("💾 Lưu Đồ Thị")
        btn_save.clicked.connect(self.save_graph)
        btn_load = QPushButton("📂 Mở Đồ Thị")
        btn_load.clicked.connect(self.load_graph)
        btn_clear = QPushButton("🗑️ Xóa Tất Cả")
        btn_clear.clicked.connect(self.clear_graph)
        btn_convert = QPushButton("🔄 Chuyển đổi Biểu diễn")
        btn_convert.clicked.connect(self.show_representation_dialog)
        
        file_layout.addWidget(btn_save)
        file_layout.addWidget(btn_load)
        file_layout.addWidget(btn_convert)
        file_layout.addWidget(btn_clear)
        file_group.setLayout(file_layout)
        controls_panel.addWidget(file_group)

        # 2. Vẽ
        draw_group = QGroupBox("Công cụ Vẽ")
        draw_layout = QVBoxLayout()
        
        # --- CHECKBOX CHỌN LOẠI ĐỒ THỊ ---
        self.chk_directed = QCheckBox("Đồ thị có hướng (Directed)")
        self.chk_directed.setStyleSheet("color: yellow; font-weight: bold;")
        self.chk_directed.toggled.connect(self.toggle_directed)
        draw_layout.addWidget(self.chk_directed)
        # ---------------------------------

        btn_node = QPushButton("🔴 Vẽ Đỉnh")
        btn_node.clicked.connect(lambda: self.canvas.set_mode("draw_node"))
        btn_edge = QPushButton("➖ Vẽ Cạnh")
        btn_edge.clicked.connect(lambda: self.canvas.set_mode("draw_edge"))
        btn_view = QPushButton("👆 Chọn / Di chuyển")
        btn_view.clicked.connect(lambda: self.canvas.set_mode("view"))
        draw_layout.addWidget(btn_node)
        draw_layout.addWidget(btn_edge)
        draw_layout.addWidget(btn_view)
        draw_group.setLayout(draw_layout)
        controls_panel.addWidget(draw_group)

        # 3. Thuật toán
        algo_group = QGroupBox("Thuật toán")
        algo_layout = QVBoxLayout()
        
        self.algo_selector = QComboBox()
        self.algo_selector.addItems([
            "Tìm đường ngắn nhất (Dijkstra)",
            "Duyệt BFS",
            "Duyệt DFS",
            "Kiểm tra Đồ thị 2 phía",
            "Prim (MST)",
            "Kruskal (MST)",
            "Max Flow (Ford-Fulkerson)",
            "Euler Cycle"
        ])
        self.algo_selector.currentIndexChanged.connect(self.on_algo_change)
        algo_layout.addWidget(QLabel("Chọn chức năng:"))
        algo_layout.addWidget(self.algo_selector)

        self.input_container = QWidget()
        input_layout = QHBoxLayout(self.input_container)
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("Start")
        self.sink_input = QLineEdit()
        self.sink_input.setPlaceholderText("End")
        input_layout.addWidget(QLabel("S:"))
        input_layout.addWidget(self.source_input)
        input_layout.addWidget(QLabel("E:"))
        input_layout.addWidget(self.sink_input)
        algo_layout.addWidget(self.input_container)

        btn_run = QPushButton("▶️ CHẠY NGAY")
        btn_run.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 10px;")
        btn_run.clicked.connect(self.run_algorithm)
        algo_layout.addWidget(btn_run)
        
        algo_group.setLayout(algo_layout)
        controls_panel.addWidget(algo_group)

        help_label = QLabel("Giữ Ctrl + Click: Thêm nút nhanh\nChuột phải: Kéo tạo cạnh")
        help_label.setStyleSheet("color: #aaa; font-style: italic;")
        controls_panel.addWidget(help_label)

        layout.addLayout(controls_panel, 1)
        layout.addWidget(self.canvas, 4)

    # --- XỬ LÝ SỰ KIỆN ---
    def toggle_directed(self, checked):
        # Báo cho Canvas biết để vẽ mũi tên
        self.canvas.is_directed = checked
        self.canvas.update()

    def on_algo_change(self):
        txt = self.algo_selector.currentText()
        if "BFS" in txt or "DFS" in txt or "Prim" in txt:
            self.source_input.setVisible(True)
            self.sink_input.setVisible(False)
        elif "Euler" in txt or "Kruskal" in txt or "2 phía" in txt:
            self.input_container.setVisible(False)
        else:
            self.input_container.setVisible(True)

    def run_algorithm(self):
        self.canvas.reset_algo_visuals()
        self.timer.stop()
        self.anim_queue = []
        
        algo = self.algo_selector.currentText()
        n = len(self.canvas.nodes)
        if n == 0: return

        # Tự động tạo đồ thị đúng loại (Có hướng hoặc Vô hướng)
        # Dựa trên trạng thái Checkbox
        is_directed = self.chk_directed.isChecked()
        G = self.get_nx_graph(weighted=True, directed=is_directed)

        try:
            # 1. DIJKSTRA
            if "Dijkstra" in algo:
                s, t = self.get_inputs(n)
                if s is None: return
                try:
                    path = nx.dijkstra_path(G, s, t, weight='weight')
                    cost = nx.dijkstra_path_length(G, s, t, weight='weight')
                    edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                    self.canvas.highlight_edges = edges
                    self.canvas.update()
                    QMessageBox.information(self, "Kết quả", f"Chi phí: {cost}\nĐường đi: {path}")
                except:
                    QMessageBox.warning(self, "Lỗi", "Không có đường đi!")

            # 2. BFS / DFS
            elif "BFS" in algo or "DFS" in algo:
                s, _ = self.get_inputs(n, need_sink=False)
                if s is None: return
                
                if "BFS" in algo:
                    nodes_order = list(nx.bfs_tree(G, source=s))
                else: 
                    nodes_order = list(nx.dfs_preorder_nodes(G, source=s))
                
                self.anim_queue = nodes_order
                self.canvas.highlight_nodes = []
                self.timer.start(1000)

            # 3. BIPARTITE (Chỉ chạy trên vô hướng)
            elif "2 phía" in algo:
                if is_directed:
                    # Bipartite thường xét trên vô hướng, ta convert tạm
                    G = G.to_undirected()
                if nx.is_bipartite(G):
                    colors = nx.bipartite.color(G)
                    self.canvas.node_colors = {n: QColor("#3498db") if c==0 else QColor("#e67e22") for n, c in colors.items()}
                    self.canvas.update()
                    QMessageBox.information(self, "Kết quả", "Là đồ thị 2 phía!")
                else:
                    QMessageBox.warning(self, "Kết quả", "KHÔNG phải đồ thị 2 phía.")

            # 4. MST (Prim/Kruskal) - Luôn coi là Vô hướng
            elif "Prim" in algo or "Kruskal" in algo:
                # MST định nghĩa trên đồ thị vô hướng
                G_undirected = G.to_undirected() 
                if not nx.is_connected(G_undirected):
                     QMessageBox.warning(self, "Lỗi", "Đồ thị phải liên thông!")
                     return
                
                if "Prim" in algo:
                    mst = nx.minimum_spanning_tree(G_undirected, algorithm='prim')
                else:
                    mst = nx.minimum_spanning_tree(G_undirected, algorithm='kruskal')
                
                self.canvas.highlight_edges = list(mst.edges())
                self.canvas.update()
                weight = mst.size(weight='weight')
                QMessageBox.information(self, "MST", f"Tổng trọng số cây khung: {weight}")

            # 5. MAX FLOW (Luôn là Có hướng)
            elif "Max Flow" in algo:
                s, t = self.get_inputs(n)
                if s is None: return
                
                # Tạo ma trận kề
                matrix = [[0]*n for _ in range(n)]
                for u, v, w in self.canvas.edges:
                    matrix[u][v] = int(w)
                    # Nếu đang ở chế độ Vô hướng, thì MaxFlow hiểu là đường 2 chiều
                    if not is_directed: 
                        matrix[v][u] = int(w)

                mf = MaxFlow(matrix)
                val, flow_mat = mf.ford_fulkerson(s, t)
                
                highlight = []
                for u in range(n):
                    for v in range(n):
                        if flow_mat[u][v] > 0: highlight.append((u, v))
                self.canvas.highlight_edges = highlight
                self.canvas.update()
                QMessageBox.information(self, "Max Flow", f"Luồng cực đại: {val}")

            # 6. EULER
            elif "Euler" in algo:
                # Euler có cả phiên bản có hướng và vô hướng
                if is_directed:
                    if not nx.is_strongly_connected(G):
                         QMessageBox.warning(self, "Lỗi", "Đồ thị có hướng phải liên thông mạnh!")
                         return
                else:
                    if not nx.is_connected(G):
                        QMessageBox.warning(self, "Lỗi", "Đồ thị phải liên thông!")
                        return
                try:
                    circuit = list(nx.eulerian_circuit(G))
                    self.anim_queue = [u for u, v in circuit] + [circuit[-1][1]]
                    self.canvas.car_position = self.anim_queue[0]
                    self.canvas.highlight_edges = []
                    self.timer.start(500)
                except nx.NetworkXError:
                    QMessageBox.warning(self, "Lỗi", "Không có chu trình Euler (Vi phạm bậc chẵn/cân bằng).")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def on_animation_step(self):
        algo = self.algo_selector.currentText()
        if "Euler" in algo:
            if len(self.anim_queue) > 1:
                u = self.anim_queue.pop(0)
                v = self.anim_queue[0]
                self.canvas.car_position = v
                self.canvas.highlight_edges.append((u, v))
                self.canvas.update()
            else:
                self.timer.stop()
                QMessageBox.information(self, "Xong", "Đã chạy hết!")
        elif "BFS" in algo or "DFS" in algo:
            if self.anim_queue:
                node = self.anim_queue.pop(0)
                self.canvas.highlight_nodes.append(node)
                self.canvas.update()
            else:
                self.timer.stop()
                QMessageBox.information(self, "Xong", "Đã duyệt xong!")

    def show_representation_dialog(self):
        n = len(self.canvas.nodes)
        if n == 0: return
        is_directed = self.chk_directed.isChecked()

        # Ma trận kề
        adj_matrix = [[0]*n for _ in range(n)]
        for u, v, w in self.canvas.edges:
            adj_matrix[u][v] = w
            if not is_directed:
                adj_matrix[v][u] = w
        
        txt_matrix = "Ma trận kề:\n" + "\n".join([" ".join(f"{x:2}" for x in row) for row in adj_matrix])

        # Danh sách kề
        adj_list = {i: [] for i in range(n)}
        for u, v, w in self.canvas.edges:
            adj_list[u].append(v)
            if not is_directed:
                adj_list[v].append(u)
        
        txt_adj_list = "Danh sách kề:\n"
        for k, v in adj_list.items():
            txt_adj_list += f"{k}: {v}\n"

        txt_edges = f"Danh sách cạnh:\n{self.canvas.edges}"

        dialog = QDialog(self)
        dialog.setWindowTitle("Biểu diễn Đồ thị")
        dialog.resize(600, 400)
        vbox = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setPlainText(f"{txt_matrix}\n\n{'-'*20}\n\n{txt_adj_list}\n\n{'-'*20}\n\n{txt_edges}")
        text_edit.setFont(QFont("Courier New", 10))
        vbox.addWidget(text_edit)
        dialog.setLayout(vbox)
        dialog.exec()

    def get_inputs(self, n, need_sink=True):
        try:
            s = int(self.source_input.text())
            if s < 0 or s >= n: raise ValueError()
            t = None
            if need_sink:
                t = int(self.sink_input.text())
                if t < 0 or t >= n: raise ValueError()
            return s, t
        except:
            QMessageBox.warning(self, "Lỗi Input", "Nhập đỉnh Start/End chưa đúng!")
            return None, None

    def get_nx_graph(self, weighted=False, directed=False):
        # Tạo đồ thị NetworkX tương ứng với lựa chọn
        G = nx.DiGraph() if directed else nx.Graph()
        for u, v, w in self.canvas.edges:
            if weighted:
                G.add_edge(u, v, weight=int(w))
            else:
                G.add_edge(u, v)
        return G

    def save_graph(self):
        path, _ = QFileDialog.getSaveFileName(self, "Lưu", "", "JSON (*.json)")
        if path:
            data = {"nodes": self.canvas.nodes, "edges": self.canvas.edges}
            with open(path, 'w') as f: json.dump(data, f)

    def load_graph(self):
        path, _ = QFileDialog.getOpenFileName(self, "Mở", "", "JSON (*.json)")
        if path:
            with open(path, 'r') as f: data = json.load(f)
            self.canvas.clear_map()
            self.canvas.nodes = [tuple(n) for n in data["nodes"]]
            self.canvas.edges = [tuple(e) for e in data["edges"]]
            self.canvas.update()

    def clear_graph(self):
        self.canvas.clear_map()