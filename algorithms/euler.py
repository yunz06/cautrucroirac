#Thuật toán Fleury và Hierholzer

import copy

def find_euler_path(adj_list):
    """
    Tìm chu trình hoặc đường đi Euler dùng thuật toán Hierholzer.
    Input: adj_list (dict): {u: [v1, v2, ...]} hoặc {u: [(v1, w), ...]}
    Output: list nodes [u, v, ..., k] hoặc None nếu không có.
    """
    
    # 1. Chuẩn hóa adj_list (bỏ trọng số nếu có) & Đếm bậc
    graph = {}
    degree = {}
    nodes = list(adj_list.keys())
    
    edge_count = 0
    
    for u in nodes:
        degree[u] = 0
        graph[u] = []
        
    for u, neighbors in adj_list.items():
        for v_data in neighbors:
            # Xử lý nếu v_data là tuple (v, w)
            v = v_data[0] if isinstance(v_data, tuple) else v_data
            
            # Vì đồ thị vô hướng lưu 2 chiều trong adj_list, ta chỉ cần add bình thường
            # Tuy nhiên, cần đảm bảo adj_list đầu vào là chuẩn 2 chiều
            graph[u].append(v)
            degree[u] += 1
            edge_count += 1
            
    # edge_count đang đếm 2 lần mỗi cạnh
    edge_count //= 2

    # 2. Kiểm tra điều kiện Euler
    odd_degree_nodes = [v for v in nodes if degree[v] % 2 != 0]
    
    start_node = None
    
    if len(odd_degree_nodes) == 0:
        # Chu trình Euler
        # Chọn đỉnh bất kỳ có bậc > 0 làm start
        for v in nodes:
            if degree[v] > 0:
                start_node = v
                break
        if start_node is None: # Đồ thị rỗng hoặc toàn đỉnh cô lập
            return []
            
    elif len(odd_degree_nodes) == 2:
        # Đường đi Euler: Bắt đầu tại 1 trong 2 đỉnh bậc lẻ
        start_node = odd_degree_nodes[0]
    else:
        # Không có Euler
        return None

    # 3. Thuật toán Hierholzer
    # Dùng stack để tìm đường
    path = []
    stack = [start_node]
    
    # Tạo copy graph để xóa cạnh dần
    current_graph = copy.deepcopy(graph)

    while stack:
        u = stack[-1]
        
        if current_graph[u]:
            v = current_graph[u][0]
            
            # Xóa cạnh u-v (cả 2 chiều)
            current_graph[u].remove(v)
            if v in current_graph:
                current_graph[v].remove(u)
                
            stack.append(v)
        else:
            path.append(stack.pop())
            
    return path[::-1] # Đảo ngược lại để có thứ tự đúng