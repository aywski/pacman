import pygame
import sys
from maze import maze
from constants import *
from pacman import PacMan
from ghost import Ghost

pygame.init()

def draw_maze(screen):
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 1:
                pygame.draw.rect(screen, BLUE, (int(x * GRID_SIZE), int(y * GRID_SIZE), GRID_SIZE, GRID_SIZE))
            elif cell == 2:
                pygame.draw.circle(screen, WHITE, (int(x * GRID_SIZE + GRID_SIZE // 2), int(y * GRID_SIZE + GRID_SIZE // 2)), int(3 * SCALE_FACTOR))

def draw_points(screen, points):
    font = pygame.font.Font(FONT, int(36 * SCALE_FACTOR))
    points_text = font.render(f"Points: {points}", True, WHITE)

    text_rect = points_text.get_rect()

    screen_width, screen_height = screen.get_size()
    x = screen_width - text_rect.width - int(10 * SCALE_FACTOR)
    y = screen_height - text_rect.height - int(10 * SCALE_FACTOR)

    screen.blit(points_text, (x, y))

def game_over(screen, won):
    # Выбор шрифта и цвета текста
    font_large = pygame.font.Font(FONT, int(50 * SCALE_FACTOR))  # Шрифт для основного сообщения
    font_small = pygame.font.Font(FONT, int(20 * SCALE_FACTOR))  # Шрифт для сообщения о выходе
    
    if won:
        # Если игра выиграна
        game_over_text = font_large.render("You Win!", True, WHITE)
    else:
        # Если игра проиграна
        game_over_text = font_large.render("Game Over", True, WHITE)
    
    exit_text = font_small.render("Press SPACE to exit", True, WHITE)
    
    # Получаем размеры текста
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    # Основной игровой цикл для отображения сообщения
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.quit()
                    sys.exit()
        
        # Отображаем фон и сообщение
        screen.fill(BLACK)
        screen.blit(game_over_text, game_over_rect)
        screen.blit(exit_text, exit_rect)
        pygame.display.flip()


def start_game_timer(pacman, clock, screen, time):
    def draw_timer(screen, time_left):
        font = pygame.font.Font(FONT, int(72 * SCALE_FACTOR))  # Большой шрифт для таймера
        timer_text = font.render(str(time_left), True, WHITE)
        text_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))  # Центрируем текст
        screen.blit(timer_text, text_rect)
        
    # Таймер перед началом игры
    countdown = time  # 5 секунд отсчета
    countdown_start_time = pygame.time.get_ticks()
    pygame.mixer.Sound(STARTSOUND).play().set_volume(0.2)

    # Основной игровой цикл с обратным отсчётом и заморозкой игры
    pacman.set_direction(PACMAN_SPEED, 0)
    while countdown > -1:

        # Отрисовка всех элементов игры (но они заморожены)
        screen.fill(BLACK)
        draw_maze(screen)
        pacman.draw(screen)  # Пакмен уже виден на экране
        draw_points(screen, pacman.points)

        # Обратный отсчёт
        time_passed = (pygame.time.get_ticks() - countdown_start_time) // 1000  # Время в секундах
        countdown = max(-1, time - time_passed)  # Оставшееся время
        draw_timer(screen, countdown)  # Отображаем таймер поверх игры

        pygame.display.flip()  # Обновляем экран

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def draw_lives(screen, lives):
    for i in range(lives):
        x = int(30 * SCALE_FACTOR + i * (GRID_SIZE + 20))  # Отступ между жизнями
        y = int(SCREEN_HEIGHT - 30 * SCALE_FACTOR)  # Расположение в нижнем левом углу
        pygame.draw.circle(screen, YELLOW, (x, y), int(GRID_SIZE // 1.5))

def main():
    pygame.display.set_caption("pacman by aywski")
    pygame.display.set_icon(pygame.image.load("sprites/pacman.ico"))
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    pacman = PacMan(maze)
    ghost = Ghost(maze, 60, CLYDE)
    ghost2 = Ghost(maze, 60, INKY)

    deathSound = pygame.mixer.Sound(DEATHSOUND)
    deathSound.set_volume(0.2)

    # Размещение точек
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 0:
                maze[y][x] = 2

    # Основной игровой цикл после завершения отсчёта
    soundPlayed = False

    start_game_timer(pacman, clock, screen, 3)

    while True:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pacman.set_direction(-PACMAN_SPEED, 0)
                elif event.key == pygame.K_RIGHT:
                    pacman.set_direction(PACMAN_SPEED, 0)
                elif event.key == pygame.K_UP:
                    pacman.set_direction(0, -PACMAN_SPEED)
                elif event.key == pygame.K_DOWN:
                    pacman.set_direction(0, PACMAN_SPEED)
                    
        if pacman.is_dead:
            if not soundPlayed:
                deathSound.play()
                soundPlayed = True
            pacman.update(dt)
            ghost.update(dt, pacman)
            screen.fill(BLACK)
            draw_maze(screen)
            pacman.draw(screen)
            ghost.draw(screen)
            draw_points(screen, pacman.points)
            draw_lives(screen, pacman.lives)  # Отображаем оставшиеся жизни
            pygame.display.flip()

            if pacman.death_animation_finished:
                deathSound.stop()
                if pacman.lives < 1:
                    game_over(screen, False)
                else:
                    pacman.reset_after_death()
                    ghost.reset_after_death()
                    soundPlayed = False

        else:
            pacman.update(dt)
            ghost.update(dt, pacman)

            # Проверка на касание Пакмана и привидения
            if pygame.sprite.collide_circle(pacman, ghost):
                pacman.die()
                ghost.die()
                pacman.lives -= 1

            if (pacman.points == pacman.total_dot):
                game_over(screen, True)

        screen.fill(BLACK)
        draw_maze(screen)
        pacman.draw(screen)
        ghost.draw(screen)
        draw_points(screen, pacman.points)
        draw_lives(screen, pacman.lives)  # Отображаем оставшиеся жизни
        pygame.display.flip()

if __name__ == "__main__":
    main()