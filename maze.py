import random
from constants import MAZE_DIFFICULTY

def generate_maze(width, height, diff="medium"):
    # Определяем сложность
    if diff == "hard":
        difficulty = 0.1
    elif diff == "medium":
        difficulty = 0.25
    elif diff == "easy":
        difficulty = 0.4

    # Создаем лабиринт, заполненный стенами
    maze = [[1 for _ in range(width)] for _ in range(height)]

    # Начальная точка
    start_x, start_y = 1, 1
    maze[start_y][start_x] = 0  # Начинаем с прохода

    # Функция для проверки соседей
    def get_neighbors(x, y):
        neighbors = []
        if x > 1 and maze[y][x-2] == 1:  # Сосед слева
            neighbors.append((x - 2, y))
        if x < width - 2 and maze[y][x+2] == 1:  # Сосед справа
            neighbors.append((x + 2, y))
        if y > 1 and maze[y-2][x] == 1:  # Сосед сверху
            neighbors.append((x, y - 2))
        if y < height - 2 and maze[y+2][x] == 1:  # Сосед снизу
            neighbors.append((x, y + 2))
        random.shuffle(neighbors)  # Перемешиваем для случайности
        return neighbors

    # Рекурсивная функция для генерации лабиринта (поиск в глубину)
    def carve_passages(x, y):
        for nx, ny in get_neighbors(x, y):
            if maze[ny][nx] == 1:  # Если это стена
                maze[ny][nx] = 0  # Пробиваем проход
                maze[(y + ny) // 2][(x + nx) // 2] = 0  # Пробиваем между стенами
                carve_passages(nx, ny)

    # Запускаем генерацию
    carve_passages(start_x, start_y)

    # Добавляем дополнительные проходы в зависимости от сложности
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if maze[y][x] == 1 and random.random() < difficulty:
                # Удаляем дополнительные стены для уменьшения сложности
                maze[y][x] = 0  

    return maze

# Пример использования
maze = generate_maze(27, 29, diff=MAZE_DIFFICULTY)

# Печать лабиринта
for row in maze:
    print(row)
