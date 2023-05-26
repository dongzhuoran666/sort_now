import uuid
from math import sqrt

array = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
         "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
         "w", "x", "y", "z",
         "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
         "W", "X", "Y", "Z"

         ]

def get_short_id():
    id = str(uuid.uuid4()).replace("-", '')  # 注意这里需要用uuid4
    buffer = []
    for i in range(0, 8):
        start = i * 4
        end = i * 4 + 4
        val = int(id[start:end], 16)
        buffer.append(array[val % 62])
    return "".join(buffer)

def calculate_dis(x1,x2,y1,y2):
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def search_enemy_plane(enemy_planes,enemy_plane_id):
    for enemy_plane in enemy_planes:
        # print(enemy_plane.target_id)
        if enemy_plane_id == enemy_plane.target_id:
            return enemy_plane

def search_area(areas,area_id):
    for area in areas:
        # print(enemy_plane.target_id)
        if area.area_id == area_id:
            return area

def search_zhang_plane(self_planes):
    for plane in self_planes:
        # print(enemy_plane.target_id)
        if plane.is_zhang == 1:
            return plane
