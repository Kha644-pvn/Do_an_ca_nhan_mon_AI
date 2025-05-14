import pygame
import sys
import random
import math
import heapq
import asyncio
from collections import deque
import time
import numpy as np
import platform

pygame.init()

# Cài đặt chung
WIDTH, HEIGHT = 800, 800
TILE_SIZE = 100
FPS = 60

# Bảng màu hiện đại
BACKGROUND = (245, 246, 250)
DARK_BG = (225, 230, 240)
TILE_BG = (255, 255, 255)
TILE_BORDER = (70, 130, 180)
EMPTY_TILE = (240, 240, 245)
HOVER_COLOR = (65, 105, 225)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (30, 100, 150)
TEXT_COLOR = (255, 255, 255)
DARK_TEXT = (50, 50, 70)
TITLE_COLOR = (50, 80, 120)
HIGHLIGHT_COLOR = (255, 213, 79)
STATUS_BG = (245, 246, 250, 200)

# status 3
# start_state = (
#     (1, 2, 3),
#     (4, 0, 6),
#     (7, 5, 8)
# )

# status 1 + 2
start_state = (
    (1, 2, 3),
    (4, 0, 6),
    (7, 5, 8)
)
goal_state = (
    (1, 2, 3),
    (4, 5, 6),
    (7, 8, 0)
)

# Font chữ
pygame.font.init()
title_font = pygame.font.Font(None, 48)
button_font = pygame.font.Font(None, 30)
tile_font = pygame.font.Font(None, 72)
status_font = pygame.font.Font(None, 28)

# Hàm tiện ích


def is_solvable(start):
    flat = [num for row in start for num in row if num != 0]
    inversions = sum(flat[i] > flat[j] for i in range(len(flat)) for j in range(i + 1, len(flat)))
    return inversions % 2 == 0

def find_empty(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return (i, j)
    return None

def get_neighbors(state):
    neighbors = []
    empty_i, empty_j = find_empty(state)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for di, dj in moves:
        new_i, new_j = empty_i + di, empty_j + dj
        if 0 <= new_i < 3 and 0 <= new_j < 3:
            new_state = [list(row) for row in state]
            new_state[empty_i][empty_j], new_state[new_i][new_j] = new_state[new_i][new_j], new_state[empty_i][empty_j]
            neighbors.append(tuple(map(tuple, new_state)))
    return neighbors

def misplaced_tiles(state, goal=goal_state):
    return sum(state[i][j] != goal[i][j] and state[i][j] != 0 for i in range(3) for j in range(3))

def manhattan_distance(state, goal=goal_state):
    distance = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:
                for gi in range(3):
                    for gj in range(3):
                        if goal[gi][gj] == state[i][j]:
                            distance += abs(i - gi) + abs(j - gj)
                            break
    return distance

# Các thuật toán tìm kiếm
def bfs(start, goal):
    visited = set()
    queue = deque([(start, [])])
    while queue:
        state, path = queue.popleft()
        if state == goal:
            return path + [state]
        if state not in visited:
            visited.add(state)
            for neighbor in get_neighbors(state):
                queue.append((neighbor, path + [state]))
    return None

def dfs(start, goal):
    visited = set()
    stack = [(start, [])]
    while stack:
        state, path = stack.pop()
        if state == goal:
            return path + [state]
        if state not in visited:
            visited.add(state)
            for neighbor in reversed(get_neighbors(state)):
                stack.append((neighbor, path + [state]))
    return None

def iterative_deepening_search(start, goal):
    depth = 0
    while depth <= 50:
        result = depth_limited_search(start, goal, depth, [])
        if result is not None:
            return result
        depth += 1
    return None

def depth_limited_search(state, goal, depth, path):
    if state == goal:
        return path + [state]
    if depth == 0:
        return None
    for neighbor in get_neighbors(state):
        if neighbor not in path:
            result = depth_limited_search(neighbor, goal, depth - 1, path + [state])
            if result:
                return result
    return None

def uniform_cost_search(start, goal):
    frontier = [(0, start, [])]
    visited = set()
    while frontier:
        cost, current, path = heapq.heappop(frontier)
        if current == goal:
            return path + [current]
        if current not in visited:
            visited.add(current)
            for neighbor in get_neighbors(current):
                if neighbor not in visited:
                    heapq.heappush(frontier, (cost + 1, neighbor, path + [current]))
    return None

def a_star(start, goal):
    visited = set()
    queue = [(manhattan_distance(start, goal), 0, start, [])]
    while queue:
        _, cost, state, path = heapq.heappop(queue)
        if state == goal:
            return path + [state]
        if state not in visited:
            visited.add(state)
            for neighbor in get_neighbors(state):
                new_cost = cost + 1
                priority = new_cost + manhattan_distance(neighbor, goal)
                heapq.heappush(queue, (priority, new_cost, neighbor, path + [state]))
    return None

def greedy_search(start, goal):
    visited = set()
    queue = [(manhattan_distance(start, goal), start, [])]
    while queue:
        _, state, path = heapq.heappop(queue)
        if state == goal:
            return path + [state]
        if state not in visited:
            visited.add(state)
            for neighbor in get_neighbors(state):
                heapq.heappush(queue, (manhattan_distance(neighbor, goal), neighbor, path + [state]))
    return None

def ida_star(start, goal):
    def search(path, g, bound):
        node = path[-1]
        f = g + manhattan_distance(node, goal)
        if f > bound:
            return f
        if node == goal:
            return "FOUND"
        min_cost = float('inf')
        for neighbor in get_neighbors(node):
            if neighbor not in path:
                path.append(neighbor)
                t = search(path, g + 1, bound)
                if t == "FOUND":
                    return "FOUND"
                if t < min_cost:
                    min_cost = t
                path.pop()
        return min_cost

    bound = manhattan_distance(start, goal)
    path = [start]
    while True:
        t = search(path, 0, bound)
        if t == "FOUND":
            return path
        if t == float('inf'):
            return None
        bound = t

# def flatten(state):
#     return [tile for row in state for tile in row]
#
# def unflatten(state):
#     return [state[i:i + 3] for i in range(0, 9, 3)]
def flatten(state):
    return [num for row in state for num in row]

# Chuyển list 1 chiều thành ma trận 3x3
def unflatten(lst):
    return tuple(tuple(lst[i*3:(i+1)*3]) for i in range(3))

def fitness(state, goal):
    return -manhattan_distance(state, goal)
def genetic_algorithm(start, goal, population_size=50, generations=200):
    population = [start for _ in range(population_size)]

    for _ in range(generations):
        population.sort(key=lambda state: fitness(state, goal), reverse=True)

        # Nếu tìm thấy trạng thái đúng thì trả kết quả luôn
        if fitness(population[0], goal) == 0:
            return [population[0]]

        next_gen = population[:10]  # chọn elite
        while len(next_gen) < population_size:
            parent1, parent2 = random.sample(population[:20], 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            next_gen.append(child)

        population = next_gen

    best = population[0]
    return bfs(start, best) if best != goal else [best]

def crossover(state1, state2):
    flat1 = flatten(state1)
    flat2 = flatten(state2)
    point = random.randint(1, 7)
    child_flat = flat1[:point] + [x for x in flat2 if x not in flat1[:point]]
    return unflatten(child_flat)

def mutate(state, mutation_rate=0.1):
    flat = flatten(state)
    if random.random() < mutation_rate:
        i, j = random.sample(range(9), 2)
        flat[i], flat[j] = flat[j], flat[i]
    return unflatten(flat)

def local_beam_search(start, goal, beam_width=3):
    beam = [start]
    path = [[start]]
    while beam:
        new_beam = []
        new_path = []
        for state, p in zip(beam, path):
            if state == goal:
                return p
            neighbors = get_neighbors(state)
            for neighbor in neighbors:
                if neighbor not in p:
                    new_beam.append(neighbor)
                    new_path.append(p + [neighbor])
        if not new_beam:
            break
        sorted_beam = sorted(zip(new_beam, new_path), key=lambda x: manhattan_distance(x[0], goal))
        beam = [state for state, _ in sorted_beam[:beam_width]]
        path = [p for _, p in sorted_beam[:beam_width]]
    return None

def simple_hill_climbing(start, goal):
    current = start
    path = [current]
    while True:
        neighbors = get_neighbors(current)
        best_neighbor = min(neighbors, key=lambda x: misplaced_tiles(x, goal))
        if misplaced_tiles(best_neighbor, goal) >= misplaced_tiles(current, goal):
            break
        current = best_neighbor
        path.append(current)
        if current == goal:
            return path
    return path if current == goal else None

def stochastic_hill_climbing(start, goal, max_iterations=1000):
    current = start
    path = [current]
    for _ in range(max_iterations):
        if current == goal:
            return path
        neighbors = get_neighbors(current)
        better_neighbors = [n for n in neighbors if misplaced_tiles(n, goal) < misplaced_tiles(current, goal)]
        if better_neighbors:
            next_state = random.choice(better_neighbors)
        else:
            next_state = random.choice(neighbors)
        current = next_state
        path.append(current)
    return path if current == goal else None

def simulated_annealing(start, goal, initial_temp=1000, cooling_rate=0.995, min_temp=0.1):
    current = start
    temp = initial_temp
    path = [current]
    while temp > min_temp:
        neighbors = get_neighbors(current)
        next_state = random.choice(neighbors)
        delta = misplaced_tiles(current, goal) - misplaced_tiles(next_state, goal)
        if delta > 0 or random.random() < math.exp(delta / temp):
            current = next_state
            path.append(current)
        if current == goal:
            return path
        temp *= cooling_rate
    return path if current == goal else None

def steepest_ascent_hill_climbing(start, goal):
    current = start
    path = [current]
    while True:
        neighbors = get_neighbors(current)
        best_neighbor = min(neighbors, key=lambda x: misplaced_tiles(x, goal))
        if misplaced_tiles(best_neighbor, goal) >= misplaced_tiles(current, goal):
            break
        current = best_neighbor
        path.append(current)
        if current == goal:
            return path
    return path if current == goal else None

def q_learning_solve(start, goal, max_steps=10000, alpha=0.1, gamma=0.9, epsilon=0.1):
    q_table = {}  #ánh xạ từ trạng thái đến danh sachs 4 giá trị hành động
    state = start
    path = [state]
    for step in range(max_steps):
        if state not in q_table:    # khởi tạo q-table cho trạng thái chưa thấy
            q_table[state] = [0.0] * 4
        if random.random() < epsilon:
            action = random.choice(range(4))
        else:
            action = max(range(4), key=lambda a: q_table[state][a])
        neighbors = get_neighbors(state)
        if action < len(neighbors):   # nếu hành động nằm trong chỉ số danh sách thì hơ lệ
            next_state = neighbors[action]
        else:
            next_state = state    # hànhdđộng ko hợp lệ thì giữu nguyên vị trí
        reward = 0 if next_state == goal else -1    # tính phần thuưởng
        if next_state not in q_table:  # đảm bảo trạng thái tiếp theo có mặt trong q_table, nếu chưa có thì khởi tạo 1 ds gồm 4 q value
            q_table[next_state] = [0.0] * 4
        q_table[state][action] = q_table[state][action] + alpha * (reward + gamma * max(q_table[next_state]) - q_table[state][action])
        state = next_state
        path.append(state)
        if state == goal:
            return path
    return None

def sarsa_solve(start, goal, max_steps=10000, alpha=0.1, gamma=0.9, epsilon=0.1):
    q_table = {}
    state = start
    path = [state]
    if state not in q_table:
        q_table[state] = [0.0] * 4
    action = random.choice(range(4)) if random.random() < epsilon else max(range(4), key=lambda a: q_table[state][a])
    for step in range(max_steps):
        neighbors = get_neighbors(state)
        if action < len(neighbors):
            next_state = neighbors[action]
        else:
            next_state = state
        reward = 0 if next_state == goal else -1
        if next_state not in q_table:
            q_table[next_state] = [0.0] * 4
        next_action = random.choice(range(4)) if random.random() < epsilon else max(range(4), key=lambda a: q_table[next_state][a])
        q_table[state][action] = q_table[state][action] + alpha * (reward + gamma * q_table[next_state][next_action] - q_table[state][action])
        state = next_state
        action = next_action
        path.append(state)
        if state == goal:
            return path
    return None

def deep_q_network(start, goal, episodes=1000, alpha=0.1, gamma=0.9, epsilon=0.1):
    # Placeholder: DQN requires neural network, simplified here using Q-table
    return q_learning_solve(start, goal)  # Thay thế thực tế cần thư viện như TensorFlow

def policy_gradient(start, goal, episodes=1000, alpha=0.01, gamma=0.9):
    # Placeholder: Policy Gradient cần mô hình học tăng cường, đơn giản hóa bằng cách ngẫu nhiên
    current = start
    path = [current]
    for _ in range(episodes):
        if current == goal:
            return path
        neighbors = get_neighbors(current)
        current = random.choice(neighbors)
        path.append(current)
    return None

def backtracking(start, goal):
    def backtrack(state, path):
        if state == goal:
            return path + [state]
        for neighbor in get_neighbors(state):
            if neighbor not in path:
                result = backtrack(neighbor, path + [state])
                if result:
                    return result
        return None
    return backtrack(start, [])

def min_conflicts(start, goal, max_steps=1000):
    current = start
    path = [current]
    for _ in range(max_steps):
        if current == goal:
            return path
        neighbors = get_neighbors(current)
        min_conflict_neighbor = min(neighbors, key=lambda x: misplaced_tiles(x, goal))
        if misplaced_tiles(min_conflict_neighbor, goal) < misplaced_tiles(current, goal):
            current = min_conflict_neighbor
            path.append(current)
        else:
            break
    return path if current == goal else None

def forward_checking(start, goal):
    def forward_check(state, path, remaining):
        if state == goal:
            return path + [state]
        neighbors = get_neighbors(state)
        for neighbor in neighbors:
            if neighbor not in path:
                new_remaining = remaining - {neighbor}
                if new_remaining:
                    result = forward_check(neighbor, path + [state], new_remaining)
                    if result:
                        return result
        return None
    all_states = set(get_neighbors(start))
    return forward_check(start, [], all_states) or bfs(start, goal)

def and_or_search(start, goal):
    def and_or(state, path, visited):
        if state == goal:
            return path + [state]
        if state in visited:
            return None
        visited.add(state)
        neighbors = get_neighbors(state)
        results = []
        for neighbor in neighbors:
            if neighbor not in path:
                result = and_or(neighbor, path + [state], visited.copy())
                if result:
                    results.append(result)
        return results[0] if results else None
    return and_or(start, [], set()) or bfs(start, goal)

def belief_state_search(start, goal):
    # Placeholder: Belief State Search cần mô hình xác suất, đơn giản hóa bằng BFS
    return bfs(start, goal)

def search_with_partial_observation(start, goal):
    # Placeholder: Partial Observation cần mô hình quan sát, đơn giản hóa bằng BFS
    return bfs(start, goal)

# Thành phần giao diện
class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER, text_color=TEXT_COLOR, border_radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.is_hovered = False
        self.animation = 0

    def draw(self, screen):
        hover_effect = self.animation / 100
        current_color = tuple(int(c1 + (c2 - c1) * hover_effect) for c1, c2 in zip(self.color, self.hover_color))
        grow = 2 * hover_effect
        effect_rect = pygame.Rect(self.rect.x - grow, self.rect.y - grow, self.rect.width + grow * 2, self.rect.height + grow * 2)
        pygame.draw.rect(screen, current_color, effect_rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, (255, 255, 255, 50), effect_rect, 1, border_radius=self.border_radius)
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.is_hovered and self.animation < 100:
            self.animation += 10
        elif not self.is_hovered and self.animation > 0:
            self.animation -= 10
        self.animation = max(0, min(100, self.animation))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_board(screen, state, animation_progress=1.0, prev_state=None):
    board_size = TILE_SIZE * 3
    offset_x = (WIDTH - board_size) // 2
    offset_y = (HEIGHT - board_size) // 2 - 30
    board_rect = pygame.Rect(offset_x - 15, offset_y - 15, board_size + 30, board_size + 30)
    shadow_rect = pygame.Rect(board_rect.x + 5, board_rect.y + 5, board_rect.width, board_rect.height)
    pygame.draw.rect(screen, (220, 220, 230), shadow_rect, border_radius=15)
    pygame.draw.rect(screen, DARK_BG, board_rect, border_radius=15)
    moved_tile = None
    if prev_state:
        for i in range(3):
            for j in range(3):
                if prev_state[i][j] != 0 and prev_state[i][j] != state[i][j]:
                    moved_tile = prev_state[i][j]
                    break
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            rect_x = offset_x + j * TILE_SIZE
            rect_y = offset_y + i * TILE_SIZE
            if prev_state and animation_progress < 1.0 and value != 0:
                for pi in range(3):
                    for pj in range(3):
                        if prev_state[pi][pj] == value:
                            old_x = offset_x + pj * TILE_SIZE
                            old_y = offset_y + pi * TILE_SIZE
                            rect_x = old_x + (rect_x - old_x) * animation_progress
                            rect_y = old_y + (rect_y - old_y) * animation_progress
                            break
            rect = pygame.Rect(rect_x, rect_y, TILE_SIZE, TILE_SIZE)
            if value != 0:
                shadow = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
                pygame.draw.rect(screen, (210, 210, 220), shadow, border_radius=10)
                tile_color = HIGHLIGHT_COLOR if value == moved_tile else TILE_BG
                pygame.draw.rect(screen, tile_color, rect, border_radius=10)
                pygame.draw.rect(screen, TILE_BORDER, rect, 2, border_radius=10)
                text = tile_font.render(str(value), True, DARK_TEXT)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            else:
                pygame.draw.rect(screen, EMPTY_TILE, rect, border_radius=10)
                pygame.draw.rect(screen, (200, 200, 220), rect, 1, border_radius=10)

def draw_message(screen, message, y_pos=HEIGHT - 100, color=DARK_TEXT, bg_alpha=200):
    text = status_font.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH // 2, y_pos))
    bg_rect = pygame.Rect(text_rect.x - 20, text_rect.y - 10, text_rect.width + 40, text_rect.height + 20)
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surface.fill((245, 246, 250, bg_alpha))
    pygame.draw.rect(bg_surface, (245, 246, 250, bg_alpha), pygame.Rect(0, 0, bg_rect.width, bg_rect.height), border_radius=10)
    pygame.draw.rect(bg_surface, (200, 210, 220, bg_alpha), pygame.Rect(0, 0, bg_rect.width, bg_rect.height), 1, border_radius=10)
    screen.blit(bg_surface, (bg_rect.x, bg_rect.y))
    screen.blit(text, text_rect)

def draw_algorithm_status(screen, algorithm_name, steps=None, elapsed_time=None):
    status_surface = pygame.Surface((300, 100), pygame.SRCALPHA)
    status_surface.fill((245, 246, 250, 200))
    pygame.draw.rect(status_surface, (220, 230, 240, 200), (0, 0, 300, 100), 1, border_radius=10)
    title_text = status_font.render(f"Algorithm: {algorithm_name}", True, TITLE_COLOR)
    status_surface.blit(title_text, (15, 15))
    if steps is not None:
        steps_text = status_font.render(f"Step: {steps}", True, DARK_TEXT)
        status_surface.blit(steps_text, (15, 45))
    if elapsed_time is not None:
        time_text = status_font.render(f"Time: {elapsed_time:.2f}s", True, DARK_TEXT)
        status_surface.blit(time_text, (15, 70))
    screen.blit(status_surface, (20, 20))

def draw_spinner(screen, center_x, center_y, radius=20, angle=0):
    num_dots = 12
    for i in range(num_dots):
        dot_angle = angle - i * (360 / num_dots)
        dot_rad = math.radians(dot_angle)
        x = center_x + int(radius * math.cos(dot_rad))
        y = center_y + int(radius * math.sin(dot_rad))
        alpha = 255 - int(255 * (i / num_dots))
        color = (70, 130, 180, alpha)
        pygame.draw.circle(screen, color, (x, y), 4)
    return (angle + 5) % 360

def handle_tile_click(state, x, y):
    board_size = TILE_SIZE * 3
    offset_x = (WIDTH - board_size) // 2
    offset_y = (HEIGHT - board_size) // 2 - 30
    grid_j = (x - offset_x) // TILE_SIZE
    grid_i = (y - offset_y) // TILE_SIZE
    if 0 <= grid_i < 3 and 0 <= grid_j < 3:
        empty_i, empty_j = find_empty(state)
        if (abs(grid_i - empty_i) == 1 and grid_j == empty_j) or (abs(grid_j - empty_j) == 1 and grid_i == empty_i):
            new_state = [list(row) for row in state]
            new_state[empty_i][empty_j], new_state[grid_i][grid_j] = new_state[grid_i][grid_j], new_state[empty_i][empty_j]
            return tuple(tuple(row) for row in new_state), True
    return state, False

def generate_random_state():
    state = list(list(row) for row in goal_state)
    for _ in range(100):
        empty_i, empty_j = find_empty(state)
        moves = [(empty_i + di, empty_j + dj) for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)] if 0 <= empty_i + di < 3 and 0 <= empty_j + dj < 3]
        if moves:
            move_i, move_j = random.choice(moves)
            state[empty_i][empty_j], state[move_i][move_j] = state[move_i][move_j], state[empty_i][empty_j]
    return tuple(tuple(row) for row in state)

def solve_puzzle(algorithm, start_state, goal_state):
    start_time = time.time()
    if algorithm == "BFS":
        solution = bfs(start_state, goal_state)
        algorithm_name = "BFS"
    elif algorithm == "DFS":
        solution = dfs(start_state, goal_state)
        algorithm_name = "DFS"
    elif algorithm == "Iterative Deepening":
        solution = iterative_deepening_search(start_state, goal_state)
        algorithm_name = "Iterative Deepening Search"
    elif algorithm == "Uniform Cost":
        solution = uniform_cost_search(start_state, goal_state)
        algorithm_name = "Uniform Cost Search"
    elif algorithm == "A*":
        solution = a_star(start_state, goal_state)
        algorithm_name = " A* Algorithm"
    elif algorithm == "Greedy":
        solution = greedy_search(start_state, goal_state)
        algorithm_name = "Greedy Algorithm"
    elif algorithm == "IDA*":
        solution = ida_star(start_state, goal_state)
        algorithm_name = "Iterative Deepening Search"
    elif algorithm == "Genetic":
        solution = genetic_algorithm(start_state, goal_state)
        algorithm_name = "Genetic Algorithm"
    elif algorithm == "Local Beam":
        solution = local_beam_search(start_state, goal_state)
        algorithm_name = "Local Beam Search"
    elif algorithm == "Simple Hill Climbing":
        solution = simple_hill_climbing(start_state, goal_state)
        algorithm_name = "Leo đồi đơn giản"
    elif algorithm == "Stochastic Hill Climbing":
        solution = stochastic_hill_climbing(start_state, goal_state)
        algorithm_name = "Stochastic Hill Climbing"
    elif algorithm == "Simulated Annealing":
        solution = simulated_annealing(start_state, goal_state)
        algorithm_name = "Simulated Annealing Algorithm"
    elif algorithm == "Steepest Ascent Hill Climbing":
        solution = steepest_ascent_hill_climbing(start_state, goal_state)
        algorithm_name = "Steepest Ascent Hill Climbing "
    elif algorithm == "Q-Learning":
        solution = q_learning_solve(start_state, goal_state)
        algorithm_name = "Q-learning"
    elif algorithm == "SARSA":
        solution = sarsa_solve(start_state, goal_state)
        algorithm_name = "SARSA"
    elif algorithm == "Deep Q-Network":
        solution = deep_q_network(start_state, goal_state)
        algorithm_name = "Mạng Q sâu"
    elif algorithm == "Policy Gradient":
        solution = policy_gradient(start_state, goal_state)
        algorithm_name = "Policy Gradient Algorithm"
    elif algorithm == "Backtracking":
        solution = backtracking(start_state, goal_state)
        algorithm_name = "BackTracking Algorithm"
    elif algorithm == "Min-Conflicts":
        solution = min_conflicts(start_state, goal_state)
        algorithm_name = "Min-Conflicts Algorithm"
    elif algorithm == "Forward Checking":
        solution = forward_checking(start_state, goal_state)
        algorithm_name = "Forward Checking Algorithm"
    elif algorithm == "AND-OR":
        solution = and_or_search(start_state, goal_state)
        algorithm_name = "AND-OR search"
    elif algorithm == "Belief State":
        solution = belief_state_search(start_state, goal_state)
        algorithm_name = "Belief State search"
    elif algorithm == "Partial Observation":
        solution = search_with_partial_observation(start_state, goal_state)
        algorithm_name = "Partial Observation search"
    else:
        return None, "Unknown Search", 0
    elapsed_time = time.time() - start_time
    return solution, algorithm_name, elapsed_time

async def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Solve 8-Puzzle")
    clock = pygame.time.Clock()

    current_state = start_state
    prev_state = None
    animation_progress = 1.0
    animation_speed = 0.1
    solution = None
    solution_index = 0
    solution_timer = 0
    solution_step_delay = 0.5
    algorithm_name = ""
    elapsed_time = None
    solving = False
    spinner_angle = 0
    message = "Press button to solve or remove"
    message_timer = 0
    tiles_movable = True
    show_algorithm_menu = False

    menu_buttons = [
        Button(WIDTH // 2 - 150, HEIGHT - 60, 100, 40, "Reset"),
        Button(WIDTH // 2 - 40, HEIGHT - 60, 100, 40, "Random"),
        Button(WIDTH // 2 + 70, HEIGHT - 60, 80, 40, "Solve", (40, 180, 99))
    ]
    algorithm_buttons = [
        Button(20, 150, 200, 35, "BFS"),
        Button(20, 190, 200, 35, "DFS"),
        Button(20, 230, 200, 35, "Iterative Deepening"),
        Button(20, 270, 200, 35, "Uniform Cost"),
        Button(20, 310, 200, 35, "A*"),
        Button(20, 350, 200, 35, "Greedy"),
        Button(20, 390, 200, 35, "IDA*"),
        Button(20, 430, 200, 35, "Genetic"),
        Button(20, 470, 200, 35, "Local Beam"),
        Button(20, 510, 200, 35, "Simple Hill Climbing"),
        Button(20, 550, 200, 35, "Stochastic Hill Climbing"),
        Button(20, 590, 200, 35, "Simulated Annealing"),
        Button(20, 630, 200, 35, "Steepest Ascent Hill Climbing"),
        Button(20, 670, 200, 35, "Q-Learning"),
        Button(20, 710, 200, 35, "SARSA"),
        Button(WIDTH - 220, 150, 200, 35, "Deep Q-Network"),
        Button(WIDTH - 220, 190, 200, 35, "Policy Gradient"),
        Button(WIDTH - 220, 230, 200, 35, "Backtracking"),
        Button(WIDTH - 220, 270, 200, 35, "Min-Conflicts"),
        Button(WIDTH - 220, 310, 200, 35, "Forward Checking"),
        Button(WIDTH - 220, 350, 200, 35, "AND-OR"),
        Button(WIDTH - 220, 390, 200, 35, "Belief State"),
        Button(WIDTH - 220, 430, 200, 35, "Partial Observation"),
        Button(WIDTH - 220, 470, 200, 35, "Thủ công", (40, 180, 99))
    ]
    close_button = Button(WIDTH // 2 - 40, HEIGHT - 60, 80, 40, "Close", (180, 70, 70))
    buttons = menu_buttons

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.is_clicked(event.pos):
                        if button.text == "Reset":
                            current_state = start_state
                            prev_state = None
                            solution = None
                            message = "Status start"
                            message_timer = 3
                            tiles_movable = True
                        elif button.text == "Random":
                            current_state = generate_random_state()
                            prev_state = None
                            solution = None
                            message = "Status random"
                            message_timer = 3
                            tiles_movable = True
                        elif button.text == "Solve":
                            show_algorithm_menu = True
                            buttons = algorithm_buttons + [close_button]
                        elif button.text == "Close":
                            show_algorithm_menu = False
                            buttons = menu_buttons
                        elif button.text == "Thủ công":
                            show_algorithm_menu = False
                            buttons = menu_buttons
                            tiles_movable = True
                            solution = None
                            message = "Solve puzzle thủ công"
                            message_timer = 3
                        elif not solving and button.text in ["BFS", "DFS", "Iterative Deepening", "Uniform Cost", "A*", "Greedy", "IDA*", "Genetic", "Local Beam", "Simple Hill Climbing", "Stochastic Hill Climbing", "Simulated Annealing", "Steepest Ascent Hill Climbing", "Q-Learning", "SARSA", "Deep Q-Network", "Policy Gradient", "Backtracking", "Min-Conflicts", "Forward Checking", "AND-OR", "Belief State", "Partial Observation"]:
                            if not is_solvable(current_state):
                                message = "Trạng thái không giải được!"
                                message_timer = 3
                            else:
                                solving = True
                                show_algorithm_menu = False
                                buttons = menu_buttons
                                tiles_movable = False
                                algorithm = button.text
                                message = f" Waiting {algorithm}..."
                                solution, algorithm_name, elapsed_time = solve_puzzle(algorithm, current_state, goal_state)
                                solving = False
                                solution_index = 0
                                solution_timer = 0
                                message = "Find the method!" if solution else "No find the method"
                                message_timer = 3
                if tiles_movable and not show_algorithm_menu:
                    new_state, moved = handle_tile_click(current_state, event.pos[0], event.pos[1])
                    if moved:
                        prev_state = current_state
                        current_state = new_state
                        animation_progress = 0.0
                        if current_state == goal_state:
                            message = "Congratulate!"
                            message_timer = 5

        if animation_progress < 1.0:
            animation_progress += animation_speed
            if animation_progress >= 1.0:
                animation_progress = 1.0

        if solution and solution_index < len(solution) - 1 and not solving:
            solution_timer += 1 / FPS
            if solution_timer >= solution_step_delay:
                solution_timer = 0
                prev_state = current_state
                solution_index += 1
                current_state = solution[solution_index]
                animation_progress = 0.0
                if solution_index == len(solution) - 1:
                    message = "Success !"
                    message_timer = 5

        if message_timer > 0:
            message_timer -= 1 / FPS

        for button in buttons:
            button.update(mouse_pos)

        screen.fill(BACKGROUND)
        title_text = title_font.render("Solve 8-Puzzle", True, TITLE_COLOR)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        draw_board(screen, current_state, animation_progress, prev_state)
        if solution and not solving:
            draw_algorithm_status(screen, algorithm_name, len(solution) - 1, elapsed_time)
        if solving:
            spinner_angle = draw_spinner(screen, WIDTH // 2, HEIGHT // 2 + 220, 15, spinner_angle)
        if message_timer > 0 or solving:
            draw_message(screen, message)
        for button in buttons:
            button.draw(screen)
        if show_algorithm_menu:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            menu_title = title_font.render("Choose Algorithms", True, (255, 255, 255))
            screen.blit(menu_title, (WIDTH // 2 - menu_title.get_width() // 2, 90))
            for button in buttons:
                button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if __name__ == "__main__" and platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    asyncio.run(main())
