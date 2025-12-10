#Kiểm tra đồ thị 2 phía (bipartite)

from collections import deque

def check_bipartite(adj_list):
    """
    Kiểm tra đồ thị có phải là đồ thị 2 phía (bipartite) hay không.
    Input: adj_list (dict): Danh sách kề {u: [v1, v2, ...]}
    Output: (is_bipartite, color_map)
            - is_bipartite: True/False
            - color_map: Dict {node: 0/1} nếu là bipartite, ngược lại None
    """
    color_map = {}
    is_bipartite = True

    # Duyệt qua tất cả các đỉnh để xử lý đồ thị không liên thông
    for node in adj_list:
        if node not in color_map:
            # Bắt đầu BFS từ đỉnh chưa được tô màu
            queue = deque([node])
            color_map[node] = 0  # Gán màu 0 cho đỉnh bắt đầu

            while queue:
                u = queue.popleft()
                
                # Duyệt các đỉnh kề
                neighbors = adj_list.get(u, [])
                for v in neighbors:
                    # Nếu v là tuple (v, w) (trường hợp có trọng số) -> lấy v[0]
                    if isinstance(v, tuple):
                        v = v[0]
                    
                    if v not in color_map:
                        # Tô màu đối lập với u
                        color_map[v] = 1 - color_map[u]
                        queue.append(v)
                    elif color_map[v] == color_map[u]:
                        # Nếu v đã có màu và cùng màu với u -> Không phải 2 phía
                        return False, {}
    
    return True, color_map