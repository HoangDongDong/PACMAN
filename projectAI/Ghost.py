import pygame
from collections import deque
import time
from setup import *
import random
# Định nghĩa màu sắc và tên tương ứng
COLOR_NAMES = {
    (255, 0, 0): "Red",
    (135, 206, 235): "Sky Blue",
    (255, 192, 203): "Pink",
    (255, 165, 0): "Orange"
}

# Cache cho các đường đi đã tính toán
path_cache = {}
# Thời gian tính lại đường đi (giây)
PATH_RECALCULATION_TIME = 0.1  # Giảm xuống để cập nhật đường đi thường xuyên hơn
# Hệ số làm mượt chuyển động
MOVEMENT_SMOOTHING = 1  # Giá trị từ 0 đến 1, càng nhỏ càng mượt

class Ghost(pygame.sprite.Sprite):
    def __init__(self, row, col, color):
        super().__init__()
        self.grid_row = row
        self.grid_col = col
        self.abs_x = col * CHAR_SIZE
        self.abs_y = row * CHAR_SIZE
        self.move_speed = GHOST_SPEED * MOVEMENT_SMOOTHING   # Giảm tốc độ xuống
        
        # Chuyển đổi màu thành tuple RGB
        self.color = pygame.Color(color)[:3]
        self.color_name = COLOR_NAMES.get(self.color, "Unknown Color")
        
        if self.color_name == "Unknown Color":
            print(f"Unknown color for Ghost: {self.color}")
        
        # Đường dẫn hình ảnh dựa trên tên màu
        self.img_path = f'D:/projectAI/assets/ghosts/{color}/'
        
        # Load và cache các hình ảnh một lần
        self.images = {
            'up': pygame.transform.scale(pygame.image.load(self.img_path + 'up.png'), (CHAR_SIZE, CHAR_SIZE)),
            'down': pygame.transform.scale(pygame.image.load(self.img_path + 'down.png'), (CHAR_SIZE, CHAR_SIZE)),
            'left': pygame.transform.scale(pygame.image.load(self.img_path + 'left.png'), (CHAR_SIZE, CHAR_SIZE)),
            'right': pygame.transform.scale(pygame.image.load(self.img_path + 'right.png'), (CHAR_SIZE, CHAR_SIZE)),
        }
        
        self.image = self.images['up']
        self.rect = self.image.get_rect(topleft=(self.abs_x, self.abs_y))
        self.mask = pygame.mask.from_surface(self.image)
        
        self.previous_position = (self.grid_row, self.grid_col)
        self.current_position = (self.grid_row, self.grid_col)
        self.moving_dir = 'up'
        
        # Thuộc tính cho tìm đường
        self.last_pathfinding_time = 0
        self.current_path = []
        
        # Thêm thuộc tính để di chuyển mượt mà
        self.target_x = self.abs_x
        self.target_y = self.abs_y
        self.next_grid_pos = None
        self.is_at_grid_center = True

        # Thuộc tính để xử lý khi bị kẹt
        self.stuck_counter = 0
        self.max_stuck = 10  # Số lần tối đa bị kẹt trước khi reset đường đi

        # Thuộc tính snap vị trí
        self.snap_tolerance = 4  # Cho phép lệch tối đa 4 pixel, sẽ snap lại nếu lệch

        # Vị trí spawn
        self.spawn_row = row
        self.spawn_col = col
        self.rect.x, self.rect.y = self.grid_to_pixel(row, col)
    
    def _animate(self):
        """Cập nhật hình ảnh dựa trên hướng di chuyển"""
        self.image = self.images[self.moving_dir]
    
    def calculate_path(self, map_data, start, destination):
        """Tính toán đường đi dựa trên loại ma"""
        # Tạo khóa cache dựa trên vị trí hiện tại và đích
        cache_key = (start, destination, self.color_name)
        
        # Kiểm tra xem đường đi đã được tính toán trước đó chưa
        if cache_key in path_cache:
            return path_cache[cache_key]
            
        # Tính toán đường đi dựa trên màu sắc của ma
        if self.color_name == "Red":
            path = bfs_search(map_data, start, destination)
        elif self.color_name == "Pink":
            path = a_star_search(map_data, start, destination)
        elif self.color_name == "Orange":
            # Orange ghost dùng thuật toán Partially Observable
            path = partially_observable_search(map_data, start, destination, vision_radius=5)
        else:
            path = bfs_search(map_data, start, destination)  # Mặc định
            
        # Lưu vào cache
        path_cache[cache_key] = path
        return path
    
    def grid_to_pixel(self, row, col):
        """Chuyển vị trí lưới (row, col) sang pixel (x, y) cho sprite"""
        x = col * CHAR_SIZE + CHAR_SIZE // 2 - self.rect.width // 2
        y = row * CHAR_SIZE + CHAR_SIZE // 2 - self.rect.height // 2
        return x, y

    def pixel_to_grid(self, x, y):
        """Chuyển vị trí pixel sang lưới (row, col)"""
        col = int((x + self.rect.width // 2) // CHAR_SIZE)
        row = int((y + self.rect.height // 2) // CHAR_SIZE)
        return row, col

    def is_near(self, x1, y1, x2, y2, tolerance=2):
        return abs(x1 - x2) <= tolerance and abs(y1 - y2) <= tolerance

    def is_at_grid_position(self):
        """Kiểm tra ghost có ở giữa ô lưới không (snap nếu cần)"""
        grid_x = round((self.rect.x + self.rect.width // 2) / CHAR_SIZE)
        grid_y = round((self.rect.y + self.rect.height // 2) / CHAR_SIZE)
        grid_center_x = grid_x * CHAR_SIZE + CHAR_SIZE // 2 - self.rect.width // 2
        grid_center_y = grid_y * CHAR_SIZE + CHAR_SIZE // 2 - self.rect.height // 2
        if abs(self.rect.x - grid_center_x) <= 2 and abs(self.rect.y - grid_center_y) <= 2:
            self.rect.x = grid_center_x
            self.rect.y = grid_center_y
            return True
        return False

    def get_next_grid_position(self):
        """Lấy ô lưới tiếp theo từ đường đi"""
        if len(self.current_path) > 1:
            return self.current_path[1]  # Ô tiếp theo trong đường đi
        return None
    
    def update(self, walls_collide_list, pacman_position, ghost_speed=None):
        if ghost_speed is not None:
            self.move_speed = ghost_speed
        else:
            self.move_speed = GHOST_SPEED

        cur_row, cur_col = self.pixel_to_grid(self.rect.x, self.rect.y)
        pac_row = int(pacman_position[1] // CHAR_SIZE)
        pac_col = int(pacman_position[0] // CHAR_SIZE)

        # Luôn cập nhật lại path mỗi frame để tối ưu hóa đường đi
        self.current_path = self.calculate_path(MAP, (cur_row, cur_col), (pac_row, pac_col))
        self.last_pathfinding_time = time.time()
        if len(path_cache) > 100:
            path_cache.clear()

        # Nếu không có path hợp lệ, snap về đúng tâm node lưới hiện tại và thử lại
        if not self.current_path or len(self.current_path) < 2:
            # Snap về tâm node lưới gần nhất
            grid_x = cur_col * CHAR_SIZE + CHAR_SIZE // 2 - self.rect.width // 2
            grid_y = cur_row * CHAR_SIZE + CHAR_SIZE // 2 - self.rect.height // 2
            self.rect.x = grid_x
            self.rect.y = grid_y
            self._animate()
            return

        # Node tiếp theo trên path
        next_row, next_col = self.current_path[1]
        target_x, target_y = self.grid_to_pixel(next_row, next_col)

        # Nếu đã gần node tiếp theo, snap vào đúng tâm node và pop node
        snap_tolerance = 6
        if abs(self.rect.x - target_x) <= snap_tolerance and abs(self.rect.y - target_y) <= snap_tolerance:
            self.rect.x = target_x
            self.rect.y = target_y
            self.current_path.pop(0)
            self._animate()
            return

        # Di chuyển đúng hướng về node tiếp theo (chỉ từng bước đúng lưới)
        dx = dy = 0
        if self.rect.x < target_x:
            dx = min(self.move_speed, target_x - self.rect.x)
            self.moving_dir = 'right'
        elif self.rect.x > target_x:
            dx = -min(self.move_speed, self.rect.x - target_x)
            self.moving_dir = 'left'
        elif self.rect.y < target_y:
            dy = min(self.move_speed, target_y - self.rect.y)
            self.moving_dir = 'down'
        elif self.rect.y > target_y:
            dy = -min(self.move_speed, self.rect.y - target_y)
            self.moving_dir = 'up'

        # Nếu di chuyển vượt quá node tiếp theo, snap lại
        if abs(dx) > abs(target_x - self.rect.x):
            dx = target_x - self.rect.x
        if abs(dy) > abs(target_y - self.rect.y):
            dy = target_y - self.rect.y

        # Nếu bị kẹt do va chạm, snap về tâm node hiện tại
        if not self.is_collide(dx, dy, walls_collide_list):
            self.rect.x += dx
            self.rect.y += dy
        else:
            grid_x = cur_col * CHAR_SIZE + CHAR_SIZE // 2 - self.rect.width // 2
            grid_y = cur_row * CHAR_SIZE + CHAR_SIZE // 2 - self.rect.height // 2
            self.rect.x = grid_x
            self.rect.y = grid_y

        self._animate()
        self.current_position = self.pixel_to_grid(self.rect.x, self.rect.y)
        if self.current_position != self.previous_position:
            self.previous_position = self.current_position
    
    def is_collide(self, dx, dy, walls_collide_list):
        """Kiểm tra va chạm với tường"""
        tmp_rect = self.rect.move(dx, dy)
        return tmp_rect.collidelist(walls_collide_list) != -1
    
    def move_to_start_pos(self):
        """Đưa ma về vị trí ban đầu"""
        self.rect.x, self.rect.y = self.grid_to_pixel(self.spawn_row, self.spawn_col)
        self.previous_position = (self.spawn_row, self.spawn_col)
        self.current_position = (self.spawn_row, self.spawn_col)
        self.current_path = []
        self.next_grid_pos = None
        self.target_x = self.rect.x
        self.target_y = self.rect.y
    
    def get_position(self):
        """Lấy vị trí hiện tại"""
        return self.current_position