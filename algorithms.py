from typing import List, Tuple, Dict
import heapq
from maze import maze 

def a_star(start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = pos
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [(nx, ny) for nx, ny in neighbors if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] != 1]

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

def greedy_best_first_search(start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Манхэттенское расстояние

    def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = pos
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [(nx, ny) for nx, ny in neighbors if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] != 1]

    open_list = []
    closed_set = set()
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}

    heapq.heappush(open_list, (heuristic(start, goal), start))

    while open_list:
        _, current = heapq.heappop(open_list)

        if current == goal:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        closed_set.add(current)

        for neighbor in get_neighbors(current):
            if neighbor in closed_set:
                continue

            if neighbor not in [item[1] for item in open_list]:
                came_from[neighbor] = current
                heapq.heappush(open_list, (heuristic(neighbor, goal), neighbor))

    return []

def bfs(start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    from collections import deque

    def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = pos
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [(nx, ny) for nx, ny in neighbors if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] != 1]

    queue = deque([start])
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for neighbor in get_neighbors(current):
            if neighbor not in came_from:  # Изменено на проверку только в came_from
                queue.append(neighbor)
                came_from[neighbor] = current

    return []

def dfs(start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = pos
        neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        return [(nx, ny) for nx, ny in neighbors if 0 <= nx < len(maze[0]) and 0 <= ny < len(maze) and maze[ny][nx] != 1]

    stack = [(start, [start])]
    visited = set()

    while stack:
        current, path = stack.pop()

        if current == goal:
            return path

        if current not in visited:
            visited.add(current)

            for neighbor in get_neighbors(current):
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))

    return []

class Node:
    def __init__(self, position: Tuple[int, int], g: int = 0, h: int = 0):
        self.position = position
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f