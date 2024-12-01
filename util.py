import numpy as np

def get_angle(a, b, c):#tinh gốc b 
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(np.degrees(radians))
    return angle


def get_distance(landmark_list):
    if len(landmark_list) < 2: #nếu không đủ 2 ngón thì không trả kết quả
        return
    (x1, y1), (x2, y2) = landmark_list[0], landmark_list[1]
    L = np.hypot(x2 - x1, y2 - y1) # khoảng cách giữa 2 tọa độ (x1,y1) và (x2,y2)
    return np.interp(L, [0, 1], [0, 1000]) #để chuẩn hóa giá trị khoảng cách từ phạm vi [0, 1] sang phạm vi [0, 1000]