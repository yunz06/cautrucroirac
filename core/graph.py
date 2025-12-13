#class Graph , Node , Edge 

import json

class Node:
    """Đại diện cho một Đỉnh (Node) trong đồ thị."""
    def __init__(self, key):
        self.key = key        
        self.neighbors = []     # Danh sách các đối tượng Edge đi ra

        # Thuộc tính tối thiểu cho DFS
        self.color = 'white'    # Trạng thái duyệt ('white', 'gray', 'black')
        self.parent = None      # Đỉnh cha
    
    # Phương thức để dễ dàng chuyển đổi sang dictionary khi lưu JSON
    def to_dict(self):
        return {
            'key': self.key,
            # Lưu key của các đỉnh đích và trọng số
            'edges': [{'dest_key': edge.destination.key, 
                       'weight': edge.weight} 
                      for edge in self.neighbors]
        }

    def __repr__(self):
        return f"Node('{self.key}')"

class Edge:
    """Đại diện cho một Cạnh (Edge) trong đồ thị."""
    def __init__(self, source, destination, weight=1):
        self.source = source          # Đối tượng Node nguồn
        self.destination = destination  # Đối tượng Node đích
        self.weight = weight          # Trọng số
    
    def __repr__(self):
        return f"Edge({self.source.key}->{self.destination.key}, w={self.weight})"

class Graph:
    """Quản lý đồ thị."""
    def __init__(self, directed=False):
        self.nodes = {}       # {key: Node value}
        self.directed = directed

    def add_node(self, key):
        """Thêm một đỉnh mới hoặc trả về đỉnh đã tồn tại."""
        if key not in self.nodes:
            new_node = Node(key)
            self.nodes[key] = new_node
        return self.nodes[key]

    def add_edge(self, u_key, v_key, weight=1):
        """Thêm cạnh (u -> v)."""
        u_node = self.add_node(u_key)
        v_node = self.add_node(v_key)

        new_edge = Edge(u_node, v_node, weight)
        u_node.add_neighbor(new_edge)

        if not self.directed:
            # Thêm cạnh ngược cho đồ thị vô hướng (v -> u)
            reverse_edge = Edge(v_node, u_node, weight)
            v_node.add_neighbor(reverse_edge)
    
    ## --- Tính năng Lưu/Tải JSON Đơn giản ---
    
    def save_to_json(self, file_path):
        """Lưu toàn bộ đồ thị sang định dạng JSON đơn giản."""
        data = {
            'directed': self.directed,
            'nodes': [node.to_dict() for node in self.nodes.values()]
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Đã lưu đồ thị thành công vào {file_path}")

    @classmethod
    def load_from_json(cls, file_path):
        """Tải đồ thị từ tệp JSON đơn giản."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        new_graph = cls(directed=data.get('directed', False))
        
        # 1. Tạo tất cả các Node
        for node_data in data['nodes']:
            new_graph.add_node(node_data['key'])
        
        # 2. Thêm các Edge
        for node_data in data['nodes']:
            u_key = node_data['key']
            u_node = new_graph.get_node(u_key)
            
            for edge_data in node_data['edges']:
                v_key = edge_data['dest_key']
                v_node = new_graph.get_node(v_key)
                
                # Tạo và thêm đối tượng Edge
                new_edge = Edge(
                    source=u_node, 
                    destination=v_node, 
                    weight=edge_data.get('weight', 1)
                )
                u_node.neighbors.append(new_edge)
        
        print(f"Đã tải đồ thị thành công từ {file_path}")
        return new_graph

    def get_node(self, key):
        """Lấy một Node từ key."""
        return self.nodes.get(key)