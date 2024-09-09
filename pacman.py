import pygame
from constants import *

class PacMan(pygame.sprite.Sprite):
    def __init__(self, maze):
        self.maze = maze
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
        self.is_dead = False
        self.death_animation_finished = False
        self.lives = LIVES
        self.total_dot = self.count_food(maze)

        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)

    def load_pacman_sprites(self):
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
        self.spawn_x, self.spawn_y = self.find_spawn_point(self.maze, self.vertical_point)
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
                cell_x = int((x + dx) % (len(self.maze[0]) * GRID_SIZE) // GRID_SIZE)
                cell_y = int((y + dy) % (len(self.maze) * GRID_SIZE) // GRID_SIZE)
                if self.maze[cell_y][cell_x] == 1:
                    return False
        return True

    def handle_tunnel(self):
        # Ширина и высота лабиринта
        maze_width = len(self.maze[0]) * GRID_SIZE
        maze_height = len(self.maze) * GRID_SIZE
        
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
        if self.maze[cell_y][cell_x] == 2:
            self.maze[cell_y][cell_x] = 0
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