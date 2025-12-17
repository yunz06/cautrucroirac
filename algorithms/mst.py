#Thuật toán Prim và Kruskal

# --- PHẦN 1: THUẬT TOÁN KRUSKAL ---
class KruskalSolver:
    def __init__(self, num_nodes):
        self.V = num_nodes
        self.parent = list(range(num_nodes))
        self.rank = [0] * num_nodes

    def find(self, i):
        if self.parent[i] == i:
            return i
        return self.find(self.parent[i])

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x != root_y:
            if self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            elif self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
            else:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1
            return True
        return False

def run_kruskal(adj_list):
    """
    Thuật toán Kruskal tìm cây khung cực tiểu
    Input: adj_list (Danh sách kề)
    Output: (Danh sách cạnh MST, Tổng trọng số)
    """
    # 1. Chuyển đổi danh sách kề thành danh sách cạnh [u, v, w]
    edges = []
    num_nodes = len(adj_list)
    
    # Duyệt để lấy cạnh (tránh trùng lặp vì đồ thị vô hướng)
    seen_edges = set()
    for u in adj_list:
        for v, w in adj_list[u]:
            if u < v: # Chỉ lấy 1 chiều để không bị trùng (0-1 và 1-0)
                edges.append([u, v, w])
    
    # 2. Sắp xếp cạnh theo trọng số tăng dần
    edges.sort(key=lambda x: x[2])
    
    solver = KruskalSolver(num_nodes)
    mst_edges = []
    total_weight = 0
    
    # 3. Duyệt từng cạnh và nối lại
    for u, v, w in edges:
        if solver.union(u, v):
            mst_edges.append((u, v)) # Lưu lại để vẽ
            total_weight += w
            
    return mst_edges, total_weight

# --- PHẦN 2: THUẬT TOÁN PRIM ---
def run_prim(adj_list):
    """
    Thuật toán Prim tìm cây khung cực tiểu
    Input: adj_list (Danh sách kề)
    Output: (Danh sách cạnh MST, Tổng trọng số)
    """
    num_nodes = len(adj_list)
    if num_nodes == 0: return [], 0
    
    # Khởi tạo
    key = {i: float('inf') for i in range(num_nodes)} # Trọng số nhỏ nhất để nối vào MST
    parent = {i: -1 for i in range(num_nodes)}        # Đỉnh cha để truy vết
    mst_set = {i: False for i in range(num_nodes)}    # Đánh dấu đỉnh đã vào MST
    
    # Bắt đầu từ đỉnh 0
    key[0] = 0
    
    for _ in range(num_nodes):
        # Tìm đỉnh u có key nhỏ nhất chưa nằm trong MST
        u = -1
        min_val = float('inf')
        
        for i in range(num_nodes):
            if not mst_set[i] and key[i] < min_val:
                min_val = key[i]
                u = i
        
        if u == -1: break # Không còn đỉnh nào nối được (đồ thị rời rạc)
        
        mst_set[u] = True
        
        # Cập nhật key cho các đỉnh kề v của u
        if u in adj_list:
            for v, w in adj_list[u]:
                if not mst_set[v] and w < key[v]:
                    key[v] = w
                    parent[v] = u

    # Tổng hợp kết quả
    mst_edges = []
    total_weight = 0
    for i in range(1, num_nodes):
        if parent[i] != -1:
            mst_edges.append((parent[i], i))
            total_weight += key[i]
            
    return mst_edges, total_weight