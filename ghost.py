import pygame
from constants import *
import heapq
from typing import List, Tuple, Dict
import random
import math
from algorithms import *

class Ghost(pygame.sprite.Sprite):
    def __init__(self, maze, speed_multiplier=1.2, skin=BLINKY, pathfinding_method='a_star'):
        super().__init__()
        self.maze = maze
        self.radius = GRID_SIZE // 2
        self.sprites = self.load_ghost_sprites(skin)
        self.current_sprite = self.sprites[0]
        self.frame = 0
        self.time_since_last_update = 0
        self.spawn_x, self.spawn_y = self.find_spawn_point(self.maze)
        self.x = (self.spawn_x + 0.5) * GRID_SIZE
        self.y = (self.spawn_y + 0.5) * GRID_SIZE
        self.dx = 0
        self.dy = 0
        self.next_direction = None
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)
        self.speed = PACMAN_SPEED * speed_multiplier  # Увеличиваем скорость привидения
        self.is_dead = False
        self.death_sprites = self.load_ghost_death_sprites()
        self.path = []
        self.next_target = None
        self.path_update_timer = 0
        self.path_update_interval = 1  # Обновляем путь каждые 0.25 секунд
        self.stuck_timer = 0
        self.stuck_threshold = 0.5  # Считаем, что привидение застряло после 0.5 секунд
        self.last_position = (self.x, self.y)
        self.sight_range = 10  # Диапазон видимости привидения в клетках
        self.last_seen_pacman = None
        self.can_see_pacman = False
        self.pathfinding_method = pathfinding_method
        self.max_stuck_time = 1.0

    def move_towards_target(self):
        if self.next_target:
            target_x, target_y = self.next_target
            current_x, current_y = int(self.x // GRID_SIZE), int(self.y // GRID_SIZE)

            if target_x > current_x:
                self.dx, self.dy = 1, 0  # Двигаться вправо
            elif target_x < current_x:
                self.dx, self.dy = -1, 0  # Двигаться влево
            elif target_y > current_y:
                self.dx, self.dy = 0, 1  # Двигаться вниз
            elif target_y < current_y:
                self.dx, self.dy = 0, -1  # Двигаться вверх

            # Теперь двигайтесь на одну клетку в выбранном направлении
            new_x = current_x + self.dx
            new_y = current_y + self.dy

            if self.can_move(new_x, current_y):  # Проверка на движение по X
                self.x = new_x * GRID_SIZE + GRID_SIZE // 2
            if self.can_move(current_x, new_y):  # Проверка на движение по Y
                self.y = new_y * GRID_SIZE + GRID_SIZE // 2

    def update(self, dt, pacman):
        if self.is_dead:
            self.handle_death_animation(dt)
            return

        self.path_update_timer += dt
        if self.path_update_timer >= self.path_update_interval:
            self.path_update_timer = 0
            self.update_path(pacman)

        if self.path:
            self.move_along_path(dt)
        else:
            self.move_randomly(dt)

        self.handle_animation(dt)
        self.check_if_stuck(dt)
        self.rect.topleft = (self.x - self.radius, self.y - self.radius)

    def move_along_path(self, dt):
        if self.next_target:
            target_x, target_y = self.next_target
            target_px_x = (target_x + 0.5) * GRID_SIZE
            target_px_y = (target_y + 0.5) * GRID_SIZE

            dx = target_px_x - self.x
            dy = target_px_y - self.y

            distance = math.sqrt(dx**2 + dy**2)
            if distance < self.speed * dt:
                self.x = target_px_x
                self.y = target_px_y
                if self.path:
                    self.next_target = self.path.pop(0)
                else:
                    self.next_target = None
                self.stuck_counter = 0
                self.last_successful_move = (self.x, self.y)
            else:
                move_x = (dx / distance) * self.speed * dt
                move_y = (dy / distance) * self.speed * dt

                new_x = self.x + move_x
                new_y = self.y + move_y

                if self.can_move(new_x, new_y):
                    self.x = new_x
                    self.y = new_y
                    self.stuck_counter = 0
                    self.last_successful_move = (self.x, self.y)
                else:
                    self.stuck_counter += dt

            self.dx = 1 if dx > 0 else (-1 if dx < 0 else 0)
            self.dy = 1 if dy > 0 else (-1 if dy < 0 else 0)

    def can_see(self, pacman):
        """Проверяет, видит ли привидение Пакмана, по прямой линии (простая проверка видимости)"""
        ghost_x, ghost_y = int(self.x // GRID_SIZE), int(self.y // GRID_SIZE)
        pacman_x, pacman_y = int(pacman.x // GRID_SIZE), int(pacman.y // GRID_SIZE)

        if ghost_x == pacman_x or ghost_y == pacman_y:
            # Проверяем, нет ли стен между привидением и Пакманом
            if self.is_clear_path(ghost_x, ghost_y, pacman_x, pacman_y):
                return True
        return False

    def is_clear_path(self, x1, y1, x2, y2):
        """Проверяет, есть ли прямая видимость между двумя точками"""
        if x1 == x2:
            # Вертикальная проверка
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if self.maze[y][x1] == 1:  # Если есть стена
                    return False
        elif y1 == y2:
            # Горизонтальная проверка
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if self.maze[y1][x] == 1:
                    return False
        return True

    def is_line_of_sight_clear(self, start: Tuple[int, int], goal: Tuple[int, int]) -> bool:
        """Проверка, не преграждают ли стены путь от привидения к Pac-Man"""
        x1, y1 = start
        x2, y2 = goal
        line_points = self.bresenham(x1, y1, x2, y2)
        for x, y in line_points:
            if self.maze[y][x] == 1:  # Если на пути есть стена
                return False
        return True

    def bresenham(self, x1, y1, x2, y2) -> List[Tuple[int, int]]:
        """Алгоритм Брезенхема для расчета всех клеток на линии между двумя точками"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

        return points

    def distance_to(self, pacman) -> float:
        """Расчет расстояния до Pac-Man в клетках"""
        return math.sqrt((self.x - pacman.x) ** 2 + (self.y - pacman.y) ** 2) // GRID_SIZE

    def move_randomly(self, dt):
        """Патрулирует, если нет пути или цели"""
        if not self.next_target:
            self.set_random_adjacent_target()

        if self.next_target:
            self.move_along_path(dt)
        else:
            # Добавить дополнительную логику, чтобы не застревать
            self.set_random_adjacent_target()

    def recalculate_path(self):
        if self.last_successful_move:
            start = (int(self.last_successful_move[0] // GRID_SIZE), 
                     int(self.last_successful_move[1] // GRID_SIZE))
        else:
            start = (int(self.x // GRID_SIZE), int(self.y // GRID_SIZE))

        possible_targets = self.get_possible_targets()
        if possible_targets:
            goal = random.choice(possible_targets)
            if self.pathfinding_method == 'a_star':
                self.path = a_star(start, goal)
            elif self.pathfinding_method == 'greedy':
                self.path = greedy_best_first_search(start, goal)
            elif self.pathfinding_method == 'bfs':
                self.path = bfs(start, goal)
            elif self.pathfinding_method == 'dfs':
                self.path = dfs(start, goal)

            if self.path:
                self.next_target = self.path.pop(0)
            else:
                self.set_random_adjacent_target()
        else:
            self.set_random_adjacent_target()

    def set_random_adjacent_target(self):
        current_x, current_y = int(self.x // GRID_SIZE), int(self.y // GRID_SIZE)
        possible_targets = [
            (current_x + 1, current_y),
            (current_x - 1, current_y),
            (current_x, current_y + 1),
            (current_x, current_y - 1)
        ]
        valid_targets = [t for t in possible_targets if self.is_valid_position(t[0], t[1])]
        if valid_targets:
            self.next_target = random.choice(valid_targets)
            self.path = [self.next_target]  # Обновляем путь
        else:
            # Если нет валидных целей, пересчитываем путь
            self.recalculate_path()

    # Остальные методы остаются без изменений...

    def check_if_stuck(self, dt):
        if self.stuck_counter >= self.max_stuck_time:
            print("Привидение застряло, телепортируем на точку спавна.")
            self.teleport_to_spawn()
            self.stuck_counter = 0

    def teleport_to_spawn(self):
        self.x = (self.spawn_x + 0.5) * GRID_SIZE
        self.y = (self.spawn_y + 0.5) * GRID_SIZE
        self.rect.topleft = (self.x - self.radius, self.y - self.radius)
        self.set_random_adjacent_target()  # Задаем новый случайный маршрут

    def get_possible_targets(self):
        targets = []
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.is_valid_position(x, y):
                    targets.append((x, y))
        return targets

    def is_valid_position(self, x, y):
        return (0 <= x < len(self.maze[0]) and 0 <= y < len(self.maze) and
                self.maze[y][x] != 1)  # 1 представляет стены в лабиринте

    def can_move(self, x, y):
        grid_x, grid_y = int(x // GRID_SIZE), int(y // GRID_SIZE)
        return self.is_valid_position(grid_x, grid_y)


    def update_path(self, pacman):
        start = (int(self.x // GRID_SIZE), int(self.y // GRID_SIZE))
        if self.can_see(pacman):
            self.can_see_pacman = True
            self.last_seen_pacman = (int(pacman.x // GRID_SIZE), int(pacman.y // GRID_SIZE))

        if self.last_seen_pacman:
            goal = self.last_seen_pacman
            if self.pathfinding_method == 'a_star':
                self.path = a_star(start, goal)
            elif self.pathfinding_method == 'greedy':
                self.path = greedy_best_first_search(start, goal)
            elif self.pathfinding_method == 'bfs':
                self.path = bfs(start, goal)
            elif self.pathfinding_method == 'dfs':
                self.path = dfs(start, goal)

        if self.path:
            self.next_target = self.path.pop(0)
        else:
            self.set_random_adjacent_target()

    def set_random_adjacent_target(self):
        current_x, current_y = int(self.x // GRID_SIZE), int(self.y // GRID_SIZE)
        possible_targets = [
            (current_x + 1, current_y),
            (current_x - 1, current_y),
            (current_x, current_y + 1),
            (current_x, current_y - 1)
        ]
        valid_targets = [t for t in possible_targets if self.is_valid_position(t[0], t[1])]
        if valid_targets:
            self.next_target = random.choice(valid_targets)
            self.path = [self.next_target]  # Обновляем путь
        else:
            # Если нет валидных целей, попробуем найти любую свободную клетку
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    new_x, new_y = current_x + dx, current_y + dy
                    if self.is_valid_position(new_x, new_y):
                        self.next_target = (new_x, new_y)
                        self.path = [self.next_target]
                        return
            
            # Если все еще нет валидных целей, телепортируем привидение на случайную свободную клетку
            self.teleport_to_random_position()

    def is_valid_position(self, x, y):
        return (0 <= x < len(self.maze[0]) and 0 <= y < len(self.maze) and
                self.maze[y][x] != 1)  # 1 представляет стены в лабиринте

    def handle_animation(self, dt):
        self.time_since_last_update += dt
        if self.time_since_last_update > ANIMATION_SPEED:
            self.time_since_last_update = 0
            self.frame = (self.frame + 1) % 2
            if self.dx != 0 or self.dy != 0:
                if self.dx > 0:
                    direction = 0
                elif self.dx < 0:
                    direction = 2
                elif self.dy > 0:
                    direction = 1
                elif self.dy < 0:
                    direction = 3
                self.current_sprite = self.sprites[self.frame + direction * 2]

    def load_ghost_sprites(self, skin):
        spritesheet = pygame.image.load(skin).convert_alpha()
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

    def reset_after_death(self):
        self.is_dead = False
        self.death_animation_finished = False
        self.spawn_x, self.spawn_y = self.find_spawn_point(self.maze)
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

    def die(self):
        self.is_dead = True
        self.frame = 0  # Начинаем с первого кадра спрайтов смерти
        self.death_animation_finished = False  # Сброс флага при новой смерти

    def draw(self, screen):
        screen.blit(self.current_sprite, (int(self.x - SPRITE_SIZE / 2), int(self.y - SPRITE_SIZE / 2)))

class Node:
    def __init__(self, position: Tuple[int, int], g: int = 0, h: int = 0):
        self.position = position
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f
    
class Node:
    def __init__(self, position: Tuple[int, int], g: int = 0, h: int = 0):
        self.position = position
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f