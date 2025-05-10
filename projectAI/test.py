import pygame
color = "Sky Blue"
COLOR_NAMES = {
    (255, 0, 0): "Red",
    (135, 206, 235): "Sky Blue",
    (255, 192, 203): "Pink",
    (255, 165, 0): "Orange"
}
color = pygame.Color(color)[:3]
color_name = COLOR_NAMES.get(color, "Unknown Color")


print(color)

print(color_name)