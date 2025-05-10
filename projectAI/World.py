import pygame
import time
from setup import *
from PacMac import Pac
from Ghost import Ghost
import random

pygame.font.init()

class Cell(pygame.sprite.Sprite):
    def __init__(self, row, col, length, width):
        super().__init__()
        self.width = length
        self.height = width
        self.id = (row, col)
        self.abs_x = row * self.width
        self.abs_y = col * self.height
        self.rect = pygame.Rect(self.abs_x, self.abs_y, self.width, self.height)
        self.occupying_piece = None

    def update(self, screen):
        pygame.draw.rect(screen, pygame.Color("blue2"), self.rect)

class Berry(pygame.sprite.Sprite):
    def __init__(self, row, col, size, is_power_up=False):
        super().__init__()
        self.power_up = is_power_up
        self.size = size
        self.color = pygame.Color("violetred")
        self.thickness = size
        self.abs_x = (row * CHAR_SIZE) + (CHAR_SIZE // 2)
        self.abs_y = (col * CHAR_SIZE) + (CHAR_SIZE // 2)
        self.rect = pygame.Rect(self.abs_x - self.size, self.abs_y - self.size, self.size * 2, self.size * 2)

    def update(self, screen):
        pygame.draw.circle(screen, self.color, (self.abs_x, self.abs_y), self.size, self.thickness)
        self.rect.topleft = (self.abs_x - self.size, self.abs_y - self.size)

class Display:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("timesnewroman", CHAR_SIZE)
        self.game_over_font = pygame.font.SysFont("timesnewroman", 48)
        self.text_color = pygame.Color("crimson")

    def show_life(self, life):
        img_path = "projectAI/assets/life/life.png"
        life_image = pygame.image.load(img_path)
        life_image = pygame.transform.scale(life_image, (CHAR_SIZE, CHAR_SIZE))
        life_x = CHAR_SIZE // 2
        if life != 0:
            for _ in range(life):
                self.screen.blit(life_image, (life_x, HEIGHT + (CHAR_SIZE // 2)))
                life_x += CHAR_SIZE

    def show_level(self, level):
        level_x = WIDTH // 3
        level = self.font.render(f'Level {level}', True, self.text_color)
        self.screen.blit(level, (level_x, (HEIGHT + (CHAR_SIZE // 2))))

    def show_score(self, score):
        score_x = WIDTH // 3
        score = self.font.render(f'{score}', True, self.text_color)
        self.screen.blit(score, (score_x * 2, (HEIGHT + (CHAR_SIZE // 2))))

    def game_over(self):
        message = self.game_over_font.render(f'GAME OVER!!', True, pygame.Color("chartreuse"))
        instruction = self.font.render(f'Press "R" to Restart', True, pygame.Color("aqua"))
        instruction1 = self.font.render(f'Press "ESC" to Quit', True, pygame.Color("aqua"))
        self.screen.blit(message, ((WIDTH // 4), (HEIGHT // 3)))
        self.screen.blit(instruction, ((WIDTH // 4), (HEIGHT // 2)))
        self.screen.blit(instruction1, ((WIDTH // 4), (HEIGHT // 1.5)))

class World:
    def __init__(self, screen):
        self.screen = screen
        self.player = pygame.sprite.GroupSingle()
        self.ghosts = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.berries = pygame.sprite.Group()
        self.display = Display(self.screen)
        self.score = 0
        self.game_over = False
        self.reset_pos = False
        self.player_score = 0
        self.game_level = 1
        self.ghost_spawn_delay = 1000  # 1 giây
        self.last_spawn_time = pygame.time.get_ticks()
        self.ghosts_to_spawn = []
        self.ghost_colors = ["red", "pink", "skyblue", "orange"]
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        self.ghost_update_counter = 0
        self.ghost_update_interval = 1  # Cập nhật ma mỗi 1 khung hình để mượt mà hơn
        self.ghost_pathfinding = "a_star"  # "a_star", "bfs", "q_learning", "beam", "backtrack_ac3", "sim_anneal"
        self.ghost_base_speed = 2  # Tăng tốc độ cơ bản của ghost lên 2
        self._generate_world()
        self._schedule_ghosts()

    def _dashboard(self):
        nav = pygame.Rect(0, HEIGHT, WIDTH, NAV_HEIGHT)
        pygame.draw.rect(self.screen, pygame.Color("cornsilk4"), nav)
        self.display.show_life(self.player.sprite.life)
        self.display.show_level(self.game_level)
        self.display.show_score(self.player.sprite.pac_score)

    def _generate_world(self):
        self.ghost_positions = []
        for y_index, col in enumerate(MAP):
            for x_index, char in enumerate(col):
                if char == "1":
                    self.walls.add(Cell(x_index, y_index, CHAR_SIZE, CHAR_SIZE))
                elif char == " ":
                    self.berries.add(Berry(x_index, y_index, CHAR_SIZE // 4))
                elif char == "B":
                    self.berries.add(Berry(x_index, y_index, CHAR_SIZE // 2, is_power_up=True))
                elif char == "P":
                    self.player.add(Pac(x_index, y_index))
                elif char == "s":
                    self.ghost_positions.append((x_index, y_index))

        self.walls_collide_list = [wall.rect for wall in self.walls.sprites()]

    def _schedule_ghosts(self):
        self.ghosts.empty()
        self.ghosts_to_spawn = []
        num_ghosts = min(self.game_level, 4)
        self.last_spawn_time = pygame.time.get_ticks()
        if not self.ghost_positions:
            return
        pos = self.ghost_positions[0]
        color = self.ghost_colors[0]
        ghost = Ghost(pos[0], pos[1], color)
        ghost.move_speed = min(self.ghost_base_speed + (self.game_level * 0.2), 3)  # Tăng tốc độ tối đa lên 3
        self.ghosts.add(ghost)
        for i in range(1, num_ghosts):
            pos_index = i % len(self.ghost_positions)
            color_index = i % len(self.ghost_colors)
            ghost_info = {
                'pos': self.ghost_positions[pos_index],
                'color': self.ghost_colors[color_index],
                'spawn_time': self.last_spawn_time + (i * self.ghost_spawn_delay)
            }
            self.ghosts_to_spawn.append(ghost_info)

    def generate_new_level(self):
        self.berries.empty()
        for y_index, col in enumerate(MAP):
            for x_index, char in enumerate(col):
                if char == " ":
                    self.berries.add(Berry(x_index, y_index, CHAR_SIZE // 4))
                elif char == "B":
                    self.berries.add(Berry(x_index, y_index, CHAR_SIZE // 2, is_power_up=True))
        self.ghost_positions = [
            (x, y)
            for y, row in enumerate(MAP)
            for x, char in enumerate(row)
            if char == "s"
        ]
        self._schedule_ghosts()

    def restart_level(self):
        self.game_level = 1
        self.player_score = 0
        self.score = 0
        self.berries.empty()
        self.ghosts.empty()
        self.ghosts_to_spawn = []
        self.player.sprite.life = 3
        self.player.sprite.pac_score = 0
        self._generate_world()
        self._schedule_ghosts()
        self.player.sprite.move_to_start_pos()
        self.player.sprite.direction = (0, 0)
        self.player.sprite.status = "idle"

    def reset_ghosts(self):
        self.ghosts.empty()
        self.ghosts_to_spawn = []
        self._schedule_ghosts()

    def check_game_state(self):
        if self.player.sprite.life == 0:
            self.game_over = True
        if len(self.berries) == 0 and self.player.sprite.life > 0:
            self.game_level += 1
            self.player.sprite.move_speed = min(2 + (self.game_level * 0.1), 3.5)
            for ghost in self.ghosts.sprites():
                ghost.move_to_start_pos()
                ghost.move_speed = min(self.ghost_base_speed + (self.game_level * 0.2), 3)  # Tăng tốc độ tối đa lên 3
            self.player.sprite.move_to_start_pos()
            self.player.sprite.direction = (0, 0)
            self.player.sprite.status = "idle"
            self.generate_new_level()

    def _spawn_ghosts(self, current_time):
        max_ghosts = min(self.game_level, 4)
        while self.ghosts_to_spawn and len(self.ghosts) < max_ghosts and current_time >= self.ghosts_to_spawn[0]['spawn_time']:
            ghost_info = self.ghosts_to_spawn.pop(0)
            pos = ghost_info['pos']
            color = ghost_info['color']
            ghost = Ghost(pos[0], pos[1], color)
            ghost.move_speed = min(self.ghost_base_speed + (self.game_level * 0.2), 3)  # Tăng tốc độ tối đa lên 3
            self.ghosts.add(ghost)

    def update(self):
        if not self.game_over:
            pressed_key = pygame.key.get_pressed()
            self.player.sprite.animate(pressed_key, self.walls_collide_list)

            current_time = pygame.time.get_ticks()
            self._spawn_ghosts(current_time)

            if self.player.sprite.rect.right <= 0:
                self.player.sprite.rect.x = WIDTH
            elif self.player.sprite.rect.left >= WIDTH:
                self.player.sprite.rect.x = 0

            player_rect = self.player.sprite.rect.inflate(100, 100)
            nearby_berries = [berry for berry in self.berries if player_rect.colliderect(berry.rect)]
            for berry in pygame.sprite.spritecollide(self.player.sprite, nearby_berries, False):
                if berry.power_up:
                    self.player.sprite.immune_time = 150
                    self.player.sprite.pac_score += 50
                    self.score += 50
                else:
                    self.player.sprite.pac_score += 10
                    self.score += 10
                berry.kill()

            ghost_collisions = pygame.sprite.spritecollide(self.player.sprite, self.ghosts, False)
            if ghost_collisions:
                ghost = ghost_collisions[0]
                if not self.player.sprite.immune:
                    self.player.sprite.move_to_start_pos()
                    self.player.sprite.direction = (0, 0)
                    self.player.sprite.status = "idle"
                    self.player.sprite.life -= 1
                    self.reset_ghosts()
                else:
                    ghost.move_to_start_pos()
                    self.player.sprite.pac_score += 100
                    self.score += 200

            self.ghost_update_counter += 1
            if self.ghost_update_counter >= self.ghost_update_interval:
                pac_position = self.player.sprite.get_position()
                for ghost in self.ghosts:
                    # Khởi tạo hướng nếu chưa có
                    if not hasattr(ghost, "move_direction"):
                        ghost.move_direction = (0, 0)
                    # Khi ghost đứng giữa ô lưới, cập nhật hướng mới
                    if ghost.rect.x % CHAR_SIZE == 0 and ghost.rect.y % CHAR_SIZE == 0:
                        ghost_grid = (ghost.rect.y // CHAR_SIZE, ghost.rect.x // CHAR_SIZE)
                        pac_grid = (pac_position[1] // CHAR_SIZE, pac_position[0] // CHAR_SIZE)
                        path = []
                        if self.ghost_pathfinding == "a_star":
                            path = a_star_search(MAP, ghost_grid, pac_grid)
                        elif self.ghost_pathfinding == "bfs":
                            path = bfs_search(MAP, ghost_grid, pac_grid)
                        elif self.ghost_pathfinding == "q_learning":
                            path = q_learning_search(MAP, ghost_grid, pac_grid, episodes=100)
                        elif self.ghost_pathfinding == "beam":
                            path = beam_search(MAP, ghost_grid, pac_grid, beam_width=3)
                        elif self.ghost_pathfinding == "backtrack_ac3":
                            path = backtrack_with_ac3(MAP, ghost_grid, pac_grid, max_steps=50)
                        elif self.ghost_pathfinding == "sim_anneal":
                            path = simulated_annealing_search(MAP, ghost_grid, pac_grid, max_steps=100)
                        if path and len(path) > 1:
                            next_cell = path[1]
                            dx = next_cell[1] - ghost_grid[1]
                            dy = next_cell[0] - ghost_grid[0]
                            # Kiểm tra ô tiếp theo có phải tường không
                            next_rect = ghost.rect.move(dx * CHAR_SIZE, dy * CHAR_SIZE)
                            if next_rect.collidelist(self.walls_collide_list) == -1:
                                ghost.move_direction = (dx, dy)
                            else:
                                ghost.move_direction = (0, 0)
                        else:
                            ghost.move_direction = (0, 0)
                    # Di chuyển từng bước nhỏ theo hướng hiện tại
                    dx, dy = ghost.move_direction
                    if (dx, dy) != (0, 0):
                        # Tính toán bước di chuyển nhỏ
                        move_x = int(dx * ghost.move_speed)
                        move_y = int(dy * ghost.move_speed)
                        # Kiểm tra nếu bước tiếp theo vượt quá ô lưới thì chỉ di chuyển vừa đủ để đứng giữa ô tiếp theo
                        target_x = ((ghost.rect.x // CHAR_SIZE) + dx) * CHAR_SIZE
                        target_y = ((ghost.rect.y // CHAR_SIZE) + dy) * CHAR_SIZE
                        if dx != 0:
                            if (dx > 0 and ghost.rect.x + move_x > target_x) or (dx < 0 and ghost.rect.x + move_x < target_x):
                                move_x = target_x - ghost.rect.x
                        if dy != 0:
                            if (dy > 0 and ghost.rect.y + move_y > target_y) or (dy < 0 and ghost.rect.y + move_y < target_y):
                                move_y = target_y - ghost.rect.y
                        # Tạo rect giả lập vị trí mới
                        new_rect = ghost.rect.move(move_x, move_y)
                        if new_rect.collidelist(self.walls_collide_list) == -1:
                            ghost.rect = new_rect
                        else:
                            ghost.move_direction = (0, 0)
                self.ghost_update_counter = 0

        self.check_game_state()

        screen_rect = self.screen.get_rect()
        for wall in self.walls:
            if screen_rect.colliderect(wall.rect):
                wall.update(self.screen)
        for berry in self.berries:
            if screen_rect.colliderect(berry.rect):
                berry.update(self.screen)
        self.ghosts.draw(self.screen)
        self.player.update()
        self.player.draw(self.screen)

        if self.game_over:
            self.display.game_over()
            pressed_key = pygame.key.get_pressed()
            if pressed_key[pygame.K_r]:
                self.game_over = False
                self.restart_level()

        self._dashboard()
        self.clock.tick(self.target_fps)