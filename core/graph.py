#class Graph , Node , Edge 

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
    Graph Adapter: Quản lý cấu trúc Node/Edge Objects và cung cấp 
    danh sách kề (Adjacency List) dễ dùng cho các thuật toán.
    """
    def __init__(self, directed: bool = False):
        self.nodes = {}             # {index: Node object}
        self.edges = []             # List of Edge objects (chỉ lưu cạnh đi)
        self.directed = directed
        self._adj_list = {}         # Danh sách kề được tính toán

    def num_nodes(self):
        return len(self.nodes)

    def build_adjacency_list(self):
        """
        Tính toán và trả về Danh sách kề chuẩn {u: [(v, w), ...]} 
        dùng cho các thuật toán.
        """
        n = self.num_nodes
        adj = {i: [] for i in self.nodes.keys()}
        
        for edge in self.edges:
            u = edge.source_key
            v = edge.destination_key
            w = edge.weight

            # Cạnh xuôi (u -> v)
            adj[u].append((v, w))
            
            # Cạnh ngược (v -> u) nếu là đồ thị vô hướng
            if not self.directed:
                adj[v].append((u, w))
                
        self._adj_list = adj
        return self._adj_list

    def from_canvas_data(self, canvas_nodes_data: list, canvas_edges_data: list):
        """
        Khôi phục đối tượng Node/Edge từ dữ liệu list of tuples của MapCanvas.
        """
        self.nodes.clear()
        self.edges.clear()

        # 1. Khởi tạo tất cả các Node 
        for i, (x, y) in enumerate(canvas_nodes_data):
            self.nodes[i] = Node(i, x, y) 

        # 2. Thêm các Edge (chỉ thêm cạnh xuôi cho đồ thị có hướng)
        for u_idx, v_idx, weight_val, is_curved in canvas_edges_data:
            if u_idx not in self.nodes or v_idx not in self.nodes:
                continue
            
            try:
                weight = float(weight_val) 
            except (ValueError, TypeError):
                weight = 1.0 

            # Thêm Edge Object vào list
            self.edges.append(Edge(u_idx, v_idx, weight, is_curved))
            
            # Nếu vô hướng và cạnh ngược chưa được thêm
            if not self.directed and (v_idx, u_idx, weight_val, is_curved) not in canvas_edges_data:
                pass 

        # 3. Xây dựng danh sách kề sau khi có đủ Node và Edge
        self.build_adjacency_list()
        
        return self

    def to_canvas_data(self):
        """
        Chuyển đổi cấu trúc Graph ngược lại về định dạng list of tuples của Canvas.
        """
        nodes_data = [node.get_position() for node in self.nodes.values()]
        
        # Chỉ cần trả về dữ liệu thô của các Edge đã được lưu (chỉ 1 chiều)
        edges_data = [edge.get_raw_data() for edge in self.edges]

        return nodes_data, edges_data