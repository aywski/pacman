import random
import pygame
import sys
from maze import maze
from constants import *

# Инициализация Pygame
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

    # Получаем размеры текста
    text_rect = points_text.get_rect()

    # Вычисляем координаты для нижнего правого угла
    screen_width, screen_height = screen.get_size()
    x = screen_width - text_rect.width - int(10 * SCALE_FACTOR)  # 10 - отступ от правого края
    y = screen_height - text_rect.height - int(10 * SCALE_FACTOR)  # 10 - отступ от нижнего края

    screen.blit(points_text, (x, y))

class PacMan(pygame.sprite.Sprite):
    def __init__(self):
        self.radius = GRID_SIZE // 2
        self.dx = 0
        self.evenAndOdd = True
        self.dy = 0
        self.next_direction = None
        self.sprites = self.load_pacman_sprites()
        self.death_sprites = self.load_pacman_death_sprites()
        self.current_sprite = self.sprites[0]
        self.frame = 0
        self.time_since_last_update = 0
        self.points = 0
        self.vertical_point = 4
        self.spawn_x, self.spawn_y = self.find_spawn_point(maze, self.vertical_point)
        self.x = (self.spawn_x + 0.5) * GRID_SIZE
        self.y = (self.spawn_y + 0.5) * GRID_SIZE
        self.is_dead = False  # Новый флаг для отслеживания смерти
        self.death_animation_finished = False
        self.lives = LIVES
        self.total_dot = self.count_food(maze)

        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)

    def load_pacman_sprites(self):
        """Загружает спрайты для Пакмана."""
        spritesheet = pygame.image.load(PACMAN_MOVING_PATH).convert_alpha()
        sprites = []
        
        sprite_size = 13  # Установите размер спрайтов
        sheet_width, sheet_height = 52, 52  # Установите размеры спрайтщита
        
        for y in range(0, sheet_height, sprite_size):
            for x in range(0, sheet_width, sprite_size):
                rect = pygame.Rect(x, y, sprite_size, sprite_size)
                sprite = spritesheet.subsurface(rect)
                sprite = pygame.transform.scale(sprite, (SPRITE_SIZE, SPRITE_SIZE))
                sprites.append(sprite)
        
        return sprites
    
    
    def load_pacman_death_sprites(self):
        """Загружает спрайты для смерти Пакмана."""
        spritesheet = pygame.image.load(PACMAN_DEATH_PATH).convert_alpha()
        sprites = []
        
        sprite_size = 15  # Установите размер спрайтов
        sheet_width, sheet_height = 180, 15  # Установите размеры спрайтщита
        
        for y in range(0, sheet_height, sprite_size):
            for x in range(0, sheet_width, sprite_size):
                rect = pygame.Rect(x, y, sprite_size, sprite_size)
                sprite = spritesheet.subsurface(rect)
                sprite = pygame.transform.scale(sprite, (SPRITE_SIZE, SPRITE_SIZE))
                sprites.append(sprite)
        
        return sprites
        

    def find_spawn_point(self, maze, vertical_point):
        height = len(maze)
        width = len(maze[0])
        center_x = width // 2
        
        # Определяем предпредпредпоследнюю строку
        spawn_y = max(height - vertical_point, 0)
        
        # Проверяем, есть ли свободная ячейка в центре на этой строке
        if maze[spawn_y][center_x] == 0:
            return center_x, spawn_y
        
        # Если в этом месте нет свободной ячейки, ищем выше
        for y in range(spawn_y, -1, -1):
            if maze[y][center_x] == 0:  # Если клетка в центре свободна
                return center_x, y
        
        # Если не найдено подходящее место, возвращаем центр maze
        return center_x, height

    def count_food(self, maze):
        return sum(row.count(0) for row in maze)

    def update(self, dt):
        if self.is_dead:
            self.handle_death_animation(dt)
            return
        
        if self.next_direction:
            self.try_change_direction()
        
        new_x = self.x + self.dx
        new_y = self.y + self.dy

        if self.can_move(new_x, new_y):
            self.x = new_x
            self.y = new_y
        else:
            if self.dx != 0:
                if self.can_move(self.x, new_y):
                    self.y = new_y
            elif self.dy != 0:
                if self.can_move(new_x, self.y):
                    self.x = new_x

        self.handle_tunnel()
        self.collect_dot()

        self.time_since_last_update += dt
        if self.time_since_last_update > ANIMATION_SPEED:
            self.time_since_last_update = 0
            self.frame = (self.frame + 1) % 4
            if self.dx != 0 or self.dy != 0:
                if self.dx > 0:
                    direction = 0
                elif self.dx < 0:
                    direction = 2
                elif self.dy > 0:
                    direction = 1
                elif self.dy < 0:
                    direction = 3
                self.current_sprite = self.sprites[self.frame + direction * 4]

        self.rect.topleft = (self.x - self.radius, self.y - self.radius)

    def reset_after_death(self):
        self.is_dead = False
        self.death_animation_finished = False
        self.spawn_x, self.spawn_y = self.find_spawn_point(maze, self.vertical_point)
        self.x = (self.spawn_x + 0.5) * GRID_SIZE
        self.y = (self.spawn_y + 0.5) * GRID_SIZE
        self.rect.topleft = (self.x - self.radius, self.y - self.radius)
        self.frame = 0
        self.current_sprite = self.sprites[0]

    
    def handle_death_animation(self, dt):
        self.time_since_last_update += dt
        if self.time_since_last_update > 0.25:
            self.time_since_last_update = 0
            self.frame = (self.frame + 1) % len(self.death_sprites)
            self.current_sprite = self.death_sprites[self.frame]

            if self.frame == len(self.death_sprites) - 1:
                self.death_animation_finished = True
                pygame.mixer.Sound(RESTARTSOUND).play().set_volume(0.4)

    def can_move(self, x, y):
        # Проверка коллизий для всех четырех углов Pac-Man'а
        for dx in [-self.radius + int(SCALE_FACTOR), self.radius - int(SCALE_FACTOR)]:
            for dy in [-self.radius + int(SCALE_FACTOR), self.radius - int(SCALE_FACTOR)]:
                cell_x = int((x + dx) % (len(maze[0]) * GRID_SIZE) // GRID_SIZE)
                cell_y = int((y + dy) % (len(maze) * GRID_SIZE) // GRID_SIZE)
                if maze[cell_y][cell_x] == 1:
                    return False
        return True

    def handle_tunnel(self):
        # Ширина и высота лабиринта
        maze_width = len(maze[0]) * GRID_SIZE
        maze_height = len(maze) * GRID_SIZE
        
        # Переход через левый или правый край лабиринта
        if self.x < -GRID_SIZE / 2:
            self.x = maze_width - GRID_SIZE / 2 - PACMAN_SPEED
        elif self.x > maze_width - GRID_SIZE / 2:
            self.x = PACMAN_SPEED
        
        # Переход через верх или низ лабиринта (если требуется)
        if self.y < -GRID_SIZE / 2:
            self.y = maze_height - GRID_SIZE / 2 - PACMAN_SPEED
        elif self.y > maze_height - GRID_SIZE / 2:
            self.y = PACMAN_SPEED

    def try_change_direction(self):
        new_x = self.x + self.next_direction[0] * PACMAN_SPEED
        new_y = self.y + self.next_direction[1] * PACMAN_SPEED
        
        if self.can_move(new_x, new_y):
            self.dx, self.dy = self.next_direction
            self.next_direction = None

    def set_direction(self, dx, dy):
        self.next_direction = (dx, dy)

    def collect_dot(self):
        cell_x = int(self.x // GRID_SIZE)
        cell_y = int(self.y // GRID_SIZE)
        if maze[cell_y][cell_x] == 2:
            maze[cell_y][cell_x] = 0
            self.points += 1
            if (self.evenAndOdd):
                pygame.mixer.Sound(EAT_DOT_1).play().set_volume(0.1)
                self.evenAndOdd = False
            else:
                pygame.mixer.Sound(EAT_DOT_0).play().set_volume(0.1)
                self.evenAndOdd = True

    def draw(self, screen):
        screen.blit(self.current_sprite, (int(self.x - SPRITE_SIZE / 2), int(self.y - SPRITE_SIZE / 2)))

    def die(self):
        self.is_dead = True
        self.frame = 0  # Начинаем с первого кадра спрайтов смерти
        self.death_animation_finished = False  # Сброс флага при новой смерти

class Ghost(pygame.sprite.Sprite):
    def __init__(self):
        self.radius = GRID_SIZE // 2
        self.sprites = self.load_ghost_sprites(PINKY_MOVING_PATH)
        self.current_sprite = self.sprites[0]
        self.frame = 0
        self.time_since_last_update = 0
        self.spawn_x, self.spawn_y = self.find_spawn_point(maze)
        self.x = (self.spawn_x + 0.5) * GRID_SIZE
        self.y = (self.spawn_y + 0.5) * GRID_SIZE
        self.dx = 0
        self.dy = 0
        self.next_direction = None  # Для смены направления
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)
        self.speed = PACMAN_SPEED
        self.is_dead = False
        self.death_sprites = self.load_ghost_death_sprites()

    def load_ghost_sprites(self, PATH):
        spritesheet = pygame.image.load(PATH).convert_alpha()
        sprites = []
        sprite_size = 14
        sheet_width, sheet_height = 28, 56
        for y in range(0, sheet_height, sprite_size):
            for x in range(0, sheet_width, sprite_size):
                rect = pygame.Rect(x, y, sprite_size, sprite_size)
                sprite = spritesheet.subsurface(rect)
                sprite = pygame.transform.scale(sprite, (SPRITE_SIZE, SPRITE_SIZE))
                sprites.append(sprite)
        return sprites

    def find_spawn_point(self, maze):
        height = len(maze)
        width = len(maze[0])
        center_x = width // 2
        center_y = height // 2

        # Определяем максимальное расстояние до краев
        max_distance = max(center_x, width - center_x, center_y, height - center_y)

        # Ищем ближайшую свободную клетку к центру
        for distance in range(max_distance + 1):
            for x in range(center_x - distance, center_x + distance + 1):
                for y in range(center_y - distance, center_y + distance + 1):
                    if 0 <= x < width and 0 <= y < height:
                        if maze[y][x] in (0, 2):  # Считаем клетки со значениями 0 и 2 как свободные
                            return x, y

        # Если не найдено подходящее место, возвращаем центр maze
        return center_x, center_y

    def update(self, dt):
        if self.is_dead:
            self.handle_death_animation(dt)
            return
        
        if self.next_direction:
            self.try_change_direction()
        
        new_x = self.x + self.dx
        new_y = self.y + self.dy

        if self.can_move(new_x, new_y):
            self.x = new_x
            self.y = new_y
        else:
            if self.dx != 0:
                if self.can_move(self.x, new_y):
                    self.y = new_y
            elif self.dy != 0:
                if self.can_move(new_x, self.y):
                    self.x = new_x

        self.handle_tunnel()

        self.time_since_last_update += dt
        if self.time_since_last_update > ANIMATION_SPEED:
            self.time_since_last_update = 0
            self.frame = (self.frame + 1) % 2  # Учитываем, что у нас 2 спрайта на направление
            if self.dx != 0 or self.dy != 0:
                if self.dx > 0:
                    direction = 0
                elif self.dx < 0:
                    direction = 2
                elif self.dy > 0:
                    direction = 1
                elif self.dy < 0:
                    direction = 3
                self.current_sprite = self.sprites[self.frame + direction * 2]  # Умножаем на 2, так как 2 спрайта на направление

        self.rect.topleft = (self.x - self.radius, self.y - self.radius)

    def load_ghost_death_sprites(self):
        spritesheet = pygame.image.load(GHOST_DEATH_PATH).convert_alpha()
        sprites = []
        
        sprite_size = 14  # Установите размер спрайтов
        sheet_width, sheet_height = 28, 14  # Установите размеры спрайтщита
        
        for y in range(0, sheet_height, sprite_size):
            for x in range(0, sheet_width, sprite_size):
                rect = pygame.Rect(x, y, sprite_size, sprite_size)
                sprite = spritesheet.subsurface(rect)
                sprite = pygame.transform.scale(sprite, (SPRITE_SIZE, SPRITE_SIZE))
                sprites.append(sprite)
        
        return sprites

    def try_change_direction(self):
        new_x = self.x + self.next_direction[0] * self.speed
        new_y = self.y + self.next_direction[1] * self.speed

        if self.can_move(new_x, new_y):
            self.dx, self.dy = self.next_direction
            self.next_direction = None

    def set_direction(self, dx, dy):
        self.next_direction = (dx, dy)

    def handle_tunnel(self):
        maze_width = len(maze[0]) * GRID_SIZE
        if self.x < 0:
            self.x = maze_width - GRID_SIZE
        elif self.x > maze_width - GRID_SIZE:
            self.x = 0
    def reset_after_death(self):
        self.is_dead = False
        self.death_animation_finished = False
        self.spawn_x, self.spawn_y = self.find_spawn_point(maze)
        self.x = (self.spawn_x + 0.5) * GRID_SIZE
        self.y = (self.spawn_y + 0.5) * GRID_SIZE
        self.rect.topleft = (self.x - self.radius, self.y - self.radius)
        self.frame = 0
        self.current_sprite = self.sprites[0]

    def can_move(self, x, y):
        for dx in [-self.radius + int(SCALE_FACTOR), self.radius - int(SCALE_FACTOR)]:
            for dy in [-self.radius + int(SCALE_FACTOR), self.radius - int(SCALE_FACTOR)]:
                cell_x = int((x + dx) % (len(maze[0]) * GRID_SIZE) // GRID_SIZE)
                cell_y = int((y + dy) % (len(maze) * GRID_SIZE) // GRID_SIZE)
                if maze[cell_y][cell_x] == 1:
                    return False
        return True

    def handle_death_animation(self, dt):
        self.time_since_last_update += dt
        if self.time_since_last_update > 0.25:
            self.time_since_last_update = 0
            self.frame = (self.frame + 1) % len(self.death_sprites)
            self.current_sprite = self.death_sprites[self.frame]

    def die(self):
        self.is_dead = True
        self.frame = 0  # Начинаем с первого кадра спрайтов смерти
        self.death_animation_finished = False  # Сброс флага при новой смерти

    def draw(self, screen):
        screen.blit(self.current_sprite, (int(self.x - SPRITE_SIZE / 2), int(self.y - SPRITE_SIZE / 2)))

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
        """Отображает таймер на фоне."""
        font = pygame.font.Font(FONT, int(72 * SCALE_FACTOR))  # Большой шрифт для таймера
        timer_text = font.render(str(time_left), True, WHITE)
        text_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))  # Центрируем текст
        screen.blit(timer_text, text_rect)
        
    # Таймер перед началом игры
    countdown = time  # 5 секунд отсчета
    countdown_start_time = pygame.time.get_ticks()
    pygame.mixer.Sound(STARTSOUND).set_volume(0.2)

    # Основной игровой цикл с обратным отсчётом и заморозкой игры
    pacman.set_direction(PACMAN_SPEED, 0)
    while countdown > -1:
        dt = clock.tick(FPS) / 1000

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
    pacman = PacMan()
    ghost = Ghost()

    deathSound = pygame.mixer.Sound(DEATHSOUND)
    deathSound.set_volume(0.2)

    # Размещение точек
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 0:
                maze[y][x] = 2

    # Основной игровой цикл после завершения отсчёта
    soundPlayed = False
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

                # Управление привидением на клавиши WASD
                elif event.key == pygame.K_w:
                    ghost.set_direction(0, -PACMAN_SPEED)
                elif event.key == pygame.K_a:
                    ghost.set_direction(-PACMAN_SPEED, 0)
                elif event.key == pygame.K_s:
                    ghost.set_direction(0, PACMAN_SPEED)
                elif event.key == pygame.K_d:
                    ghost.set_direction(PACMAN_SPEED, 0)
                    
        if pacman.is_dead:
            if not soundPlayed:
                deathSound.play()
                soundPlayed = True
            pacman.update(dt)
            ghost.update(dt)
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
            ghost.update(dt)

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