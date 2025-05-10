import pygame
import math
from setup import *
from World import World

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + NAV_HEIGHT))
pygame.display.set_caption("Pacman Game")

# Load images
try:
    pacman_image = pygame.image.load('projectAI/assets/picture/PacMan.png')
    # Scale image to 80% of window width
    new_width = int(WIDTH * 0.8)
    image_scale = new_width / pacman_image.get_width()
    new_height = int(pacman_image.get_height() * image_scale)
    pacman_image = pygame.transform.scale(pacman_image, (new_width, new_height))

    # Load and scale logo
    logo_image = pygame.image.load('projectAI/assets/picture/Pac-Man-Logo-1a.png')
    logo_width = 500  # Set desired width for logo
    logo_scale = logo_width / logo_image.get_width()
    logo_height = int(logo_image.get_height() * logo_scale)
    logo_image = pygame.transform.scale(logo_image, (logo_width, logo_height))
except:
    pacman_image = None
    logo_image = None

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

font_title = pygame.font.SysFont("Times New Roman", 50, bold=True)
font_button = pygame.font.SysFont("Times New Roman", 30)
font_names = pygame.font.SysFont("Times New Roman", 20)

# Game states
MENU = 0
GAME = 1
RANKING = 2
GAME_OVER = 3

def draw_button(sc, text, x, y, width, height, color = BLUE):
    pygame.draw.rect(sc, color, (x, y, width, height))
    pygame.draw.rect(sc, BLACK, (x, y, width, height), 2)

    text_surface = font_button.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    sc.blit(text_surface, text_rect)

def load_scores():
    scores = []
    try:
        with open('projectAI/assets/scores.txt', 'r', encoding='utf-8') as file:
            for line in file:
                name, score = line.strip().split(',')
                scores.append((name, int(score)))
    except FileNotFoundError:
        return []
    return sorted(scores, key=lambda x: x[1], reverse=True)

def save_score(name, score):
    with open('projectAI/assets/scores.txt', 'a', encoding='utf-8') as file:
        file.write(f"{name},{score}\n")

def draw_ranking(sc):
    scores = load_scores()
    y = 100
    title = font_title.render("Bảng xếp hạng", True, BLUE)
    sc.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
    
    for name, score in scores[:10]:  # Show top 10
        text = font_names.render(f"{name}: {score}", True, BLACK)
        sc.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
        y += 40
    
    draw_button(sc, "Quay lại", WIDTH//2 - 100, HEIGHT - 100, 200, 50)

def main():
    clock = pygame.time.Clock()
    running = True
    game_state = MENU
    world = None
    player_name = ""
    input_active = False
    
    while running:
        screen.fill(WHITE)
        
        if game_state == MENU:
            # Logo
            if logo_image:
                logo_rect = logo_image.get_rect(center=(WIDTH // 2, 100))
                screen.blit(logo_image, logo_rect)
            
            # Draw Pacman image
            if pacman_image:
                image_rect = pacman_image.get_rect()
                # Position image 180 pixels from top instead of 120
                image_rect.centerx = WIDTH // 2
                image_rect.top = 200
                screen.blit(pacman_image, image_rect)
            
            # Adjust button positions to be below the image
            draw_button(screen, "Chơi game", WIDTH//2 - 100, 400, 200, 50)
            draw_button(screen, "Xếp hạng", WIDTH//2 - 100, 500, 200, 50)
            draw_button(screen, "Thoát", WIDTH//2 - 100, 600, 200, 50)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if WIDTH//2 - 100 <= mouse_pos[0] <= WIDTH//2 + 100:
                        if 400 <= mouse_pos[1] <= 450:  # Chơi game
                            game_state = GAME
                            world = World(screen)
                        elif 500 <= mouse_pos[1] <= 550:  # Xếp hạng
                            game_state = RANKING
                        elif 600 <= mouse_pos[1] <= 650:  # Thoát
                            running = False
                            
        elif game_state == GAME:
            if world.game_over:
                game_state = GAME_OVER
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                world.update()
                
        elif game_state == RANKING:
            draw_ranking(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if WIDTH//2 - 100 <= mouse_pos[0] <= WIDTH//2 + 100:
                        if HEIGHT - 100 <= mouse_pos[1] <= HEIGHT - 50:
                            game_state = MENU
                            
        elif game_state == GAME_OVER:
            title = font_title.render("Game Over", True, BLUE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
            
            score_text = font_names.render(f"Điểm: {world.score}", True, BLACK)
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 100))
            
            name_text = font_names.render(f"Tên: {player_name}", True, BLACK)
            screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 150))
            
            draw_button(screen, "Lưu điểm", WIDTH//2 - 100, 250, 200, 50)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if player_name:
                            save_score(player_name, world.score)
                            game_state = MENU
                            player_name = ""
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        player_name += event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if WIDTH//2 - 100 <= mouse_pos[0] <= WIDTH//2 + 100:
                        if 250 <= mouse_pos[1] <= 300 and player_name:
                            save_score(player_name, world.score)
                            game_state = MENU
                            player_name = ""
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()