import pygame
import sys
from constants import *

# Инициализация Pygame
pygame.init()

# Определите размеры и создайте окно
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Pac-Man')

# Параметры спрайтов
SPRITE_SIZE = 28

# Загрузка спрайтов
def load_pacman_sprites():
    """Загружает спрайты для Пакмана."""
    spritesheet = pygame.image.load(PINKY_MOVING_PATH).convert_alpha()
    sprites = []
    
    sprite_size = 14  # Установите размер спрайтов
    sheet_width, sheet_height = 28, 56  # Установите размеры спрайтщита
    
    for y in range(0, sheet_height, sprite_size):
        for x in range(0, sheet_width, sprite_size):
            rect = pygame.Rect(x, y, sprite_size, sprite_size)
            sprite = spritesheet.subsurface(rect)
            sprite = pygame.transform.scale(sprite, (SPRITE_SIZE, SPRITE_SIZE))
            sprites.append(sprite)
    
    return sprites

# Загружаем спрайты
sprites = load_pacman_sprites()
current_sprite_index = 0
sprite_count = len(sprites)

# Основной игровой цикл
clock = pygame.time.Clock()

while True:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Логика обновления текущего спрайта
    current_sprite_index = (current_sprite_index + 1) % sprite_count

    # Отрисовка
    WINDOW.fill((0, 0, 0))  # Очистка экрана
    current_sprite = sprites[current_sprite_index]
    WINDOW.blit(current_sprite, (WINDOW_WIDTH // 2 - SPRITE_SIZE // 2, WINDOW_HEIGHT // 2 - SPRITE_SIZE // 2))
    
    pygame.display.flip()
    clock.tick(10)  # Контроль частоты обновлений (10 кадров в секунду)
