#Duyệt đồ thị theo các chiến lược: BFS & DFS

from collections import deque

# --- 1. BFS ---
def run_bfs(adj_list, start_node):
    if start_node not in adj_list:
        return []

    visited = set()
    queue = deque([start_node])
    visited.add(start_node)
    
    visited_order = [] 

    while queue:
        current = queue.popleft()
        visited_order.append(current)
        neighbors = sorted(adj_list.get(current, [])) # Sắp xếp để duyệt theo thứ tự
        
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return visited_order

# --- 2. DFS ---
def run_dfs(adj_list, start_node):
    """
    Thuật toán DFS (Duyệt theo chiều sâu)
    Input: adj_list, start_node
    Output: Danh sách thứ tự duyệt
    """
    if start_node not in adj_list:
        return []

    visited = set()
    visited_order = []

    # Hàm đệ quy nội bộ
    def dfs_recursive(u):
        visited.add(u)
        visited_order.append(u)
        
        # Lấy danh sách kề và sắp xếp
        neighbors = sorted(adj_list.get(u, []))
        for v in neighbors:
            if v not in visited:
                dfs_recursive(v)

    # Bắt đầu chạy
    dfs_recursive(start_node)
    return visited_order