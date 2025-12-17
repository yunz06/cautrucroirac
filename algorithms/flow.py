#Thuật toán Ford-Fulkerson

from collections import deque

class MaxFlow: 
    def __init__(self, graph):
        self.graph = graph  
        self.n = len(graph)

    def bfs(self, residual_graph, s, t, parent):
        visited = [False] * self.n
        queue = []
        
        queue.append(s)
        visited[s] = True
        parent[s] = -1
        
        while queue:
            u = queue.pop(0)
            
            for v in range(self.n):
                # Kiểm tra trên residual_graph 
                # Đk: Chưa thăm VÀ dung lượng còn lại (residual) > 0
                if visited[v] == False and residual_graph[u][v] > 0:
                    queue.append(v)
                    visited[v] = True
                    parent[v] = u
                    if v == t:
                        return True
        return False

    def ford_fulkerson(self, s, t):
        # Tạo ma trận dư thừa ban đầu (copy từ graph gốc)
        residual = [row[:] for row in self.graph]
        
        parent = [-1] * self.n
        max_flow = 0
        
        # Ma trận lưu luồng thực tế
        flow_matrix = [[0] * self.n for _ in range(self.n)]

        # 2. Vòng lặp chính: Truyền 'residual' vào cho bfs tìm đường
        while self.bfs(residual, s, t, parent):
            path_flow = float("inf")
            s_node = t # Biến tạm để truy vết ngược từ đích về nguồn
            
            # Bước A: Tìm độ thắt cổ chai (bottleneck) của đường đi này
            while s_node != s:
                u = parent[s_node]
                path_flow = min(path_flow, residual[u][s_node])
                s_node = u

            # Bước B: Cập nhật lại đồ thị dư thừa và luồng
            v = t
            while v != s:
                u = parent[v]
                
                # Giảm capacity chiều xuôi
                residual[u][v] -= path_flow
                # Tăng capacity chiều ngược
                residual[v][u] += path_flow

                # Ghi nhận luồng vào kết quả
                flow_matrix[u][v] += path_flow
                
                v = u

            max_flow += path_flow
            
            # Reset parent cho vòng lặp sau
            parent = [-1] * self.n

        return max_flow, flow_matrix