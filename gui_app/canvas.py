# gui_app/canvas.py

import math
from PyQt6.QtWidgets import QWidget, QInputDialog
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF, QPainterPath
from PyQt6.QtCore import Qt, QPoint, QRect, QPointF

class MapCanvas(QWidget):
    def __init__(self):
        super().__init__()
        
        # Danh sách tọa độ nút [(x, y), ...]
        self.nodes = [] 
        
        # Danh sách cạnh [(u, v, weight, is_curved), ...]
        self.edges = [] 
        
        # Các biến trạng thái
        self.current_mode = "view" 
        self.selected_node = None     # Nút đang click chọn
        self.dragging_node = None     # Nút đang kéo thả
        
        # Biến hỗ trợ hiển thị thuật toán
        self.highlight_edges = []
        self.visited_nodes = []
        
        # Cờ: True = Có mũi tên, False = Không mũi tên
        self.is_directed = True 

        # Style giao diện
        self.setStyleSheet("background-color: #1e1e1e; border: 2px solid #555;")
        self.node_radius = 22

    # --- CÁC HÀM SETTING ---
    def set_mode(self, mode):
        self.current_mode = mode
        self.selected_node = None
        self.update()

    def set_graph_type(self, is_directed):
        self.is_directed = is_directed
        self.update()

    # --- [QUAN TRỌNG] HÀM BỊ THIẾU ĐÃ ĐƯỢC THÊM LẠI ---
    def reset_algo_visuals(self):
        self.highlight_edges = []
        self.visited_nodes = []
        self.update()

    def clear_map(self):
        self.nodes = []
        self.edges = []
        self.reset_algo_visuals() # Gọi hàm reset trạng thái thuật toán
        self.selected_node = None
        self.update()

    # --- HELPER: TÌM NÚT TẠI VỊ TRÍ CLICK ---
    def get_node_at(self, x, y):
        for i, (nx, ny) in enumerate(self.nodes):
            dist = math.sqrt((x - nx)**2 + (y - ny)**2)
            if dist <= self.node_radius + 5: 
                return i
        return None
    
    # --- HELPER: TÍNH TÂM ĐỒ THỊ ---
    def get_graph_centroid(self):
        if not self.nodes: return (0, 0)
        sum_x = sum(n[0] for n in self.nodes)
        sum_y = sum(n[1] for n in self.nodes)
        return (sum_x / len(self.nodes), sum_y / len(self.nodes))

    # ==========================================================
    # XỬ LÝ SỰ KIỆN CHUỘT
    # ==========================================================
    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        x = event.position().x()
        y = event.position().y()
        clicked_node = self.get_node_at(x, y)

        # 1. Chế độ vẽ Đỉnh
        if self.current_mode == "draw_node":
            if clicked_node is None:
                self.nodes.append((x, y))
                self.update()
        
        # 2. Chế độ vẽ Cạnh
        elif self.current_mode == "draw_edge":
            if clicked_node is not None:
                if self.selected_node is None:
                    self.selected_node = clicked_node
                else:
                    if clicked_node != self.selected_node:
                        # Check Shift để vẽ cong
                        modifiers = event.modifiers()
                        is_curved = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
                        
                        start = self.selected_node
                        end = clicked_node
                        
                        weight, ok = QInputDialog.getInt(
                            self, "Trọng số", f"Từ {start} -> {end}:", 
                            value=1, min=1, max=999
                        )
                        
                        if ok:
                            exists = False
                            for idx, (eu, ev, ew, e_curve) in enumerate(self.edges):
                                if eu == start and ev == end:
                                    self.edges[idx] = (start, end, weight, is_curved) 
                                    exists = True
                                    break
                            
                            if not exists:
                                self.edges.append((start, end, weight, is_curved))
                        
                        self.selected_node = None 
                    else:
                        self.selected_node = None
            else:
                self.selected_node = None
            self.update()

        # 3. Chế độ Di chuyển
        elif self.current_mode == "view":
            if clicked_node is not None:
                self.selected_node = clicked_node
                self.dragging_node = clicked_node 
            else:
                self.selected_node = None
            self.update()

    def mouseMoveEvent(self, event):
        if self.current_mode == "view" and self.dragging_node is not None:
            x = event.position().x()
            y = event.position().y()
            self.nodes[self.dragging_node] = (x, y)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging_node = None

    # ==========================================================
    # VẼ GIAO DIỆN
    # ==========================================================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        font_weight = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font_weight)
        
        graph_center = self.get_graph_centroid()

        # 1. Vẽ Cạnh
        for u, v, w, is_curved in self.edges:
            if u >= len(self.nodes) or v >= len(self.nodes): continue

            p1 = QPointF(self.nodes[u][0], self.nodes[u][1])
            p2 = QPointF(self.nodes[v][0], self.nodes[v][1])

            is_highlight = False
            for hu, hv in self.highlight_edges:
                if (hu == u and hv == v) or (not self.is_directed and hu == v and hv == u):
                    is_highlight = True
                    break
            
            color = QColor("#00ff00") if is_highlight else QColor("#ffffff")
            width = 3 if is_highlight else 2
            painter.setPen(QPen(color, width))
            painter.setBrush(Qt.BrushStyle.NoBrush)

            if is_curved:
                self.draw_curved_edge_smart(painter, p1, p2, str(w), graph_center)
            else:
                self.draw_straight_edge(painter, p1, p2, str(w), draw_arrow=self.is_directed)

        # 2. Vẽ Nút
        font_node = QFont("Segoe UI", 12, QFont.Weight.Bold)
        painter.setFont(font_node)

        for i, (x, y) in enumerate(self.nodes):
            if i == self.selected_node: brush_color = QColor("#f1c40f")
            elif i in self.visited_nodes: brush_color = QColor("#2ecc71")
            else: brush_color = QColor("#e74c3c")

            painter.setBrush(QBrush(brush_color))
            painter.setPen(QPen(Qt.GlobalColor.white, 3))
            
            painter.drawEllipse(QPointF(x, y), self.node_radius, self.node_radius)
            
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            rect = QRect(int(x - self.node_radius), int(y - self.node_radius), 
                         int(self.node_radius*2), int(self.node_radius*2))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(i))

    # --- CÁC HÀM VẼ CHI TIẾT ---
    def draw_straight_edge(self, painter, p1, p2, text, draw_arrow=False):
        painter.drawLine(p1, p2)
        if draw_arrow: self.draw_arrow_head(painter, p1, p2)
        mid = (p1 + p2) / 2
        self.draw_weight_text(painter, mid, text)

    def draw_curved_edge_smart(self, painter, p1, p2, text, graph_center):
        path = QPainterPath()
        path.moveTo(p1)
        
        mid_x = (p1.x() + p2.x()) / 2
        mid_y = (p1.y() + p2.y()) / 2
        
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        dist = math.sqrt(dx*dx + dy*dy)
        if dist == 0: dist = 1
        
        offset = dist * 0.3 

        nx = -dy / dist
        ny = dx / dist

        c1_x = mid_x + nx * offset
        c1_y = mid_y + ny * offset
        c2_x = mid_x - nx * offset
        c2_y = mid_y - ny * offset

        cx, cy = graph_center
        dist_c1 = (c1_x - cx)**2 + (c1_y - cy)**2
        dist_c2 = (c2_x - cx)**2 + (c2_y - cy)**2

        if dist_c1 > dist_c2:
            ctrl_point = QPointF(c1_x, c1_y)
        else:
            ctrl_point = QPointF(c2_x, c2_y)
        
        path.quadTo(ctrl_point, p2)
        painter.drawPath(path)
        
        self.draw_arrow_head(painter, ctrl_point, p2)
        self.draw_weight_text(painter, ctrl_point, text)

    def draw_arrow_head(self, painter, start_p, end_p):
        arrow_size = 18
        margin = self.node_radius + 5
        
        dx = end_p.x() - start_p.x()
        dy = end_p.y() - start_p.y()
        angle = math.atan2(dy, dx)
        
        end_x = end_p.x() - margin * math.cos(angle)
        end_y = end_p.y() - margin * math.sin(angle)
        real_end = QPointF(end_x, end_y)

        p1 = QPointF(real_end.x() - arrow_size * math.cos(angle - math.pi / 6),
                     real_end.y() - arrow_size * math.sin(angle - math.pi / 6))
        p2 = QPointF(real_end.x() - arrow_size * math.cos(angle + math.pi / 6),
                     real_end.y() - arrow_size * math.sin(angle + math.pi / 6))
        
        painter.setBrush(QBrush(painter.pen().color())) 
        painter.drawPolygon(QPolygonF([real_end, p1, p2]))

    def draw_weight_text(self, painter, pos, text):
        rect_w = 32
        rect_h = 22
        rect = QRect(int(pos.x()) - rect_w//2, int(pos.y()) - rect_h//2, rect_w, rect_h)
        
        painter.save() 
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#222222")) 
        painter.setOpacity(0.9)
        painter.drawRect(rect)
        
        painter.setPen(QColor("#f1c40f"))
        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()