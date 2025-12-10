#chứa các hàm chuyển đổi ( đổi ma trận sang danh sách kề, ngược lại )

import math

# Hàm này quan trọng nhất: Tính khoảng cách trên màn hình phẳng (Pixel)
def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Hàm tính thời gian dự kiến
def calculate_eta_hours(distance_km, speed_kmh):
    if speed_kmh <= 0: 
        return float('inf')
    return distance_km / speed_kmh