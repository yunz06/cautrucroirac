#class Graph , Node , Edge 

import json
from PyQt6.QtWidgets import QFileDialog

class Node:
    """
    Đại diện cho một Đỉnh (Node), lưu trữ vị trí vật lý (x, y) trên Canvas.
    Key (index) dùng để tham chiếu.
    """
    def __init__(self, key: int, x: float = 0.0, y: float = 0.0):
        self.key = key          
        self.x = x              # Tọa độ X trên Canvas
        self.y = y              # Tọa độ Y trên Canvas
        self.neighbors = []     # Danh sách các đối tượng Edge đi ra
           
        self.parent = None      
        self.distance = float('inf') 

    def add_neighbor(self, edge):
        """Thêm một Edge đi ra từ nút này."""
        self.neighbors.append(edge)

    def get_position(self):
        """Trả về tuple tọa độ (x, y)."""
        return (self.x, self.y)

    def __repr__(self):
        return f"Node({self.key}, pos=({self.x:.1f}, {self.y:.1f}))"

class Edge:
    """
    Đại diện cho một Cạnh (Edge), bao gồm trọng số và cờ cong.
    """
    def __init__(self, source: Node, destination: Node, weight: float = 1.0, is_curved: bool = False):
        self.source = source          
        self.destination = destination  
        self.weight = weight          
        self.is_curved = is_curved    

    def __repr__(self):
        return f"Edge({self.source.key}->{self.destination.key}, w={self.weight})"

class Graph:
    """
    Graph Adapter: Quản lý cấu trúc Node/Edge và chuyển đổi giữa dữ liệu Canvas (GUI) 
    và cấu trúc đối tượng (Logic).
    """
    def __init__(self, directed=False):
        self.nodes = {}       # {index: Node object}
        self.directed = directed

    def get_node(self, key: int) -> Node:
        """Lấy một Node từ key (index)."""
        return self.nodes.get(key)

    def from_canvas_data(self, canvas_nodes_data: list, canvas_edges_data: list):
        """
        Khôi phục đối tượng Node/Edge từ dữ liệu list of tuples của MapCanvas.
        
        - canvas_nodes_data: List of (x, y)
        - canvas_edges_data: List of (u_index, v_index, weight, is_curved_bool)
        """
        
        # 1. Khởi tạo tất cả các Node và lưu trữ vị trí (x, y)
        num_nodes = len(canvas_nodes_data)
        for i, (x, y) in enumerate(canvas_nodes_data):
            self.nodes[i] = Node(i, x, y) 

        # 2. Thêm các Edge
        for u_idx, v_idx, weight_val, is_curved in canvas_edges_data:
            if u_idx not in self.nodes or v_idx not in self.nodes:
                continue

            u_node = self.nodes[u_idx]
            v_node = self.nodes[v_idx]
            
            try:
                # Trọng số có thể là int/str từ dữ liệu lưu, ép về float để tính toán
                weight = float(weight_val) 
            except (ValueError, TypeError):
                weight = 1.0 

            # Cạnh xuôi (u -> v)
            u_node.add_neighbor(Edge(u_node, v_node, weight, is_curved))

            if not self.directed:
                # Cạnh ngược (v -> u) cho đồ thị vô hướng
                v_node.add_neighbor(Edge(v_node, u_node, weight, is_curved))
        
        return self

    def to_canvas_data(self):
        """
        Chuyển đổi cấu trúc Graph ngược lại về định dạng list of tuples của Canvas.
        """
        nodes_data = [node.get_position() for node in self.nodes.values()]
        
        edges_data = []
        seen_edges = set()

        for u_node in self.nodes.values():
            for edge in u_node.neighbors:
                u, v = u_node.key, edge.destination.key
                
                if not self.directed:
                    # Đồ thị vô hướng, chỉ cần lưu một chiều
                    key = tuple(sorted((u, v)))
                    if key in seen_edges:
                        continue
                    seen_edges.add(key)
                
                # Lưu dưới dạng tuple: (u, v, weight, is_curved)
                edges_data.append((u, v, int(edge.weight), edge.is_curved))

        return nodes_data, edges_data
    
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