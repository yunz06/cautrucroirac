#Tìm đường đi ngắn nhất (dijkstra)

import heapq
from typing import Dict, List, Tuple, Optional
from core.converters import euclidean_distance, calculate_eta_hours

class TrafficGraph:
    def __init__(self):
        self.nodes: Dict[str, Tuple[float, float]] = {}
        self.edges: Dict[str, List[Dict]] = {}

    def add_node(self, node_id: str, x: float, y: float) -> None:
        self.nodes[node_id] = (x, y)
        if node_id not in self.edges:
            self.edges[node_id] = []

    def add_road(self, u: str, v: str, distance_km: float, 
                 speed_limit_kmh: float = 40, 
                 traffic_multiplier: float = 1.0, 
                 one_way: bool = False) -> None:
        
        if u not in self.nodes or v not in self.nodes:
            return 

        # Tính thời gian đi hết cạnh này
        base_time = calculate_eta_hours(distance_km, speed_limit_kmh)
        real_time = base_time * traffic_multiplier

        edge_data = {
            'to': v,
            'distance': distance_km,       # Trọng số khoảng cách
            'weight_time': real_time       # Trọng số thời gian (có tắc đường)
        }

        self.edges[u].append(edge_data)

        if not one_way:
            reverse_edge_data = edge_data.copy()
            reverse_edge_data['to'] = u
            self.edges[v].append(reverse_edge_data)

    def get_coords(self, node_id: str) -> Tuple[float, float]:
        return self.nodes.get(node_id)

def reconstruct_path(came_from: Dict, current: str) -> List[str]:
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]

def a_star_search(graph: TrafficGraph, start: str, end: str, mode: str = 'time') -> Tuple[Optional[List[str]], float]:
    """
    mode='time': Tìm đường nhanh nhất (xét tắc đường)
    mode='distance': Tìm đường ngắn nhất (về độ dài)
    """
    if start not in graph.nodes or end not in graph.nodes:
        return None, float('inf')

    open_set = []
    # (f_score, current_node)
    heapq.heappush(open_set, (0.0, start))
    
    came_from = {}
    
    # g_score: Chi phí thực tế từ Start -> Node hiện tại
    g_score = {node: float('inf') for node in graph.nodes}
    g_score[start] = 0.0
    
    # Lấy tọa độ đích để tính Heuristic
    end_x, end_y = graph.get_coords(end)

    while open_set:
        current_f, current = heapq.heappop(open_set)

        if current == end:
            return reconstruct_path(came_from, current), g_score[end]

        if current in graph.edges:
            for edge in graph.edges[current]:
                neighbor = edge['to']
                
                # 1. Chọn loại trọng số dựa trên mode
                if mode == 'time':
                    cost_to_neighbor = edge['weight_time']
                else: # mode == 'distance'
                    cost_to_neighbor = edge['distance']
                
                tentative_g_score = g_score[current] + cost_to_neighbor

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    
                    # 2. Tính Heuristic (Khoảng cách chim bay về đích)
                    neigh_x, neigh_y = graph.get_coords(neighbor)
                    
                    # Dùng Euclid vì là màn hình phẳng
                    dist_to_end = euclidean_distance(neigh_x, neigh_y, end_x, end_y)
                    
                    if mode == 'time':
                        # Chia cho tốc độ lý tưởng (ví dụ 100) để ra thời gian ước lượng
                        h_score = dist_to_end / 100.0
                    else:
                        h_score = dist_to_end
                    
                    f_score = tentative_g_score + h_score
                    heapq.heappush(open_set, (f_score, neighbor))

    return None, float('inf')