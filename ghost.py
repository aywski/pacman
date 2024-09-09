import pygame
from constants import *
import heapq
from typing import List, Tuple, Dict
import random
import math

class Ghost(pygame.sprite.Sprite):
    def __init__(self, maze, speed_multiplier=1.2, skin=BLINKY):
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
        self.path_update_interval = 1.0  # Update path every 1 second
        self.stuck_timer = 0
        self.stuck_threshold = 0.5  # Consider ghost stuck after 0.5 seconds of no movement
        self.last_position = (self.x, self.y)


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
            else:
                move_x = (dx / distance) * self.speed * dt
                move_y = (dy / distance) * self.speed * dt
                
                new_x = self.x + move_x
                new_y = self.y + move_y

                if self.can_move(new_x, self.y):
                    self.x = new_x
                if self.can_move(self.x, new_y):
                    self.y = new_y

            self.dx = 1 if dx > 0 else (-1 if dx < 0 else 0)
            self.dy = 1 if dy > 0 else (-1 if dy < 0 else 0)

    def move_randomly(self, dt):
        if not self.next_target:
            self.set_random_adjacent_target()
        
        if self.next_target:
            self.move_along_path(dt)

    def check_if_stuck(self, dt):
        current_position = (self.x, self.y)
        if current_position == self.last_position:
            self.stuck_timer += dt
            if self.stuck_timer >= self.stuck_threshold:
                self.set_random_adjacent_target()
                self.stuck_timer = 0
        else:
            self.stuck_timer = 0
        self.last_position = current_position

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

    def can_move(self, x, y):
        for dx in [-self.radius + 1, self.radius - 1]:
            for dy in [-self.radius + 1, self.radius - 1]:
                cell_x = int((x + dx) % (len(self.maze[0]) * GRID_SIZE) // GRID_SIZE)
                cell_y = int((y + dy) % (len(self.maze) * GRID_SIZE) // GRID_SIZE)
                if self.maze[cell_y][cell_x] == 1:
                    return False
        return True

    def update_path(self, pacman):
        start = (int(self.x // GRID_SIZE), int(self.y // GRID_SIZE))
        goal = (int(pacman.x // GRID_SIZE), int(pacman.y // GRID_SIZE))
        self.path = self.a_star(start, goal)
        if self.path:
            self.next_target = self.path.pop(0)
            self.stuck_timer = 0  # Сбросить таймер застревания при нахождении нового пути
        else:
            # Если путь не найден, установить случайную соседнюю клетку как следующую цель
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

    def is_valid_position(self, x, y):
        return (0 <= x < len(self.maze[0]) and 0 <= y < len(self.maze) and
                self.maze[y][x] != 1)  # 1 представляет стены в лабиринте

    def a_star(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            x, y = pos
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            return [(nx, ny) for nx, ny in neighbors if 0 <= nx < len(self.maze[0]) and 0 <= ny < len(self.maze) and self.maze[ny][nx] != 1]

        start_node = Node(start)
        start_node.h = heuristic(start, goal)
        open_list = [start_node]
        closed_set = set()
        came_from: Dict[Tuple[int, int], Node] = {}

        while open_list:
            current = heapq.heappop(open_list)

            if current.position == goal:
                path = []
                while current.position != start:
                    path.append(current.position)
                    current = came_from[current.position]
                path.reverse()
                return path

            closed_set.add(current.position)

            for neighbor_pos in get_neighbors(current.position):
                if neighbor_pos in closed_set:
                    continue

                neighbor = Node(neighbor_pos, current.g + 1)
                neighbor.h = heuristic(neighbor_pos, goal)

                if neighbor not in open_list:
                    came_from[neighbor_pos] = current
                    heapq.heappush(open_list, neighbor)
                elif neighbor.g < current.g:
                    came_from[neighbor_pos] = current
                    open_list.remove(neighbor)
                    heapq.heappush(open_list, neighbor)

        return []

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