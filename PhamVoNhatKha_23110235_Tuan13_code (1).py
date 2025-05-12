import pygame
import sys
import time
from collections import deque
import pyperclip
import random
import math

pygame.init()

# Các cài đặt chung
WIDTH, HEIGHT = 600, 800
TILE_SIZE = WIDTH // 4
FPS = 30

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BUTTON_COLOR = (0, 150, 255)
BUTTON_HOVER_COLOR = (30, 180, 255)
TEXT_COLOR = (255, 255, 255)

# Trạng thái đầu và đích
start_state = (
    (2, 1, 3),
    (4, 8, 7),
    (5, 0, 6)
)
goal_state = (
    (1, 2, 3),
    (4, 5, 6),
    (7, 8, 0)
)


# Xác định tính khả giải của bài toán
def is_solvable(start):
    # Đếm số nghịch thế (inversions)
    flat = [num for row in start for num in row if num != 0]
    inversions = sum(flat[i] > flat[j] for i in range(len(flat)) for j in range(i + 1, len(flat)))
    return inversions % 2 == 0


# Tìm vị trí ô trống (số 0)
def find_empty(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return (i, j)
    return None


# Lấy các trạng thái kề có thể đạt được
def get_neighbors(state):
    neighbors = []
    empty_i, empty_j = find_empty(state)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

    for di, dj in moves:
        new_i, new_j = empty_i + di, empty_j + dj
        if 0 <= new_i < 3 and 0 <= new_j < 3:
            # Tạo bản sao trạng thái hiện tại
            new_state = [list(row) for row in state]
            # Đổi chỗ ô trống với ô kề
            new_state[empty_i][empty_j], new_state[new_i][new_j] = new_state[new_i][new_j], new_state[empty_i][empty_j]
            neighbors.append(tuple(map(tuple, new_state)))

    return neighbors


# Hàm đánh giá heuristic - Số lượng ô không đúng vị trí
def misplaced_tiles(state, goal=goal_state):
    return sum(state[i][j] != goal[i][j] and state[i][j] != 0 for i in range(3) for j in range(3))


# Hàm đánh giá heuristic - Khoảng cách Manhattan
def manhattan_distance(state, goal=goal_state):
    distance = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:
                # Tìm vị trí đúng của số này trong goal state
                for gi in range(3):
                    for gj in range(3):
                        if goal[gi][gj] == state[i][j]:
                            distance += abs(i - gi) + abs(j - gj)
                            break
    return distance


# 1. Iterative Deepening Depth-First Search (IDDFS)
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


def iterative_deepening_search(start, goal):
    depth = 0
    while True:
        print(f"Thử độ sâu: {depth}")
        result = depth_limited_search(start, goal, depth, [])
        if result is not None:
            return result
        depth += 1
        # Thêm giới hạn để tránh vòng lặp vô hạn
        if depth > 50:
            print("Đạt giới hạn độ sâu tối đa")
            return None


# 2. Breadth-First Search (BFS)
def bfs(start, goal):
    visited = set()
    queue = deque([(start, [])])
    while queue:
        state, path = queue.popleft()
        if state == goal:
            return path + [state]
        visited.add(state)
        for neighbor in get_neighbors(state):
            if neighbor not in visited:
                queue.append((neighbor, path + [state]))
    return None


# 3. Depth-First Search (DFS)
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


# 4. Greedy Best-First Search
def greedy(start, goal):
    visited = set()
    queue = [(start, [], misplaced_tiles(start))]
    while queue:
        queue.sort(key=lambda x: x[2])
        state, path, _ = queue.pop(0)
        if state == goal:
            return path + [state]
        visited.add(state)
        for neighbor in get_neighbors(state):
            if neighbor not in visited:
                queue.append((neighbor, path + [state], misplaced_tiles(neighbor)))
    return None


# 5. A* Search
def a_star(start, goal):
    visited = set()
    queue = [(start, [], misplaced_tiles(start))]
    while queue:
        queue.sort(key=lambda x: len(x[1]) + x[2])
        state, path, _ = queue.pop(0)
        if state == goal:
            return path + [state]
        visited.add(state)
        for neighbor in get_neighbors(state):
            if neighbor not in visited:
                queue.append((neighbor, path + [state], misplaced_tiles(neighbor) + len(path) + 1))
    return None


# Hàm tiện ích cho thuật toán di truyền
def flatten(state):
    return [num for row in state for num in row]


def unflatten(lst):
    return tuple(tuple(lst[i * 3:(i + 1) * 3]) for i in range(3))


def fitness(state):
    flat = flatten(state)
    goal_flat = flatten(goal_state)
    return sum(flat[i] != goal_flat[i] for i in range(9))


def crossover(parent1, parent2):
    flat1 = flatten(parent1)
    flat2 = flatten(parent2)
    point = random.randint(1, 7)
    child_flat = flat1[:point] + [x for x in flat2 if x not in flat1[:point]]
    return unflatten(child_flat)


def mutate(state, mutation_rate=0.1):
    flat = flatten(state)
    if random.random() < mutation_rate:
        i, j = random.sample(range(9), 2)
        flat[i], flat[j] = flat[j], flat[i]
    return unflatten(flat)


# 6. Genetic Algorithm
def genetic_algorithm(start, goal, population_size=50, generations=200):
    population = [mutate(start) for _ in range(population_size)]
    best = None
    for _ in range(generations):
        population.sort(key=fitness)
        if fitness(population[0]) == 0:
            best = population[0]
            break
        next_gen = population[:10]  # Elitism
        while len(next_gen) < population_size:
            parents = random.sample(population[:20], 2)
            child = crossover(parents[0], parents[1])
            next_gen.append(mutate(child))
        population = next_gen
    best = population[0]
    return [start, best] if best else None


# 7. Simulated Annealing
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


# 8. Simple Hill Climbing
def simple_hill_climbing(start, goal):
    current = start
    path = [current]

    while True:
        neighbors = get_neighbors(current)
        neighbors.sort(key=lambda x: misplaced_tiles(x, goal))
        best_neighbor = neighbors[0]

        if misplaced_tiles(best_neighbor, goal) >= misplaced_tiles(current, goal):
            break

        current = best_neighbor
        path.append(current)

        if current == goal:
            return path

    return path if current == goal else None


# 9. Steepest Ascent Hill Climbing
def steepest_ascent_hill_climbing(start, goal):
    current = start
    path = [current]

    while True:
        neighbors = get_neighbors(current)
        better_neighbors = [n for n in neighbors if misplaced_tiles(n, goal) < misplaced_tiles(current, goal)]

        if not better_neighbors:
            break

        best_neighbor = min(better_neighbors, key=lambda x: misplaced_tiles(x, goal))
        current = best_neighbor
        path.append(current)

        if current == goal:
            return path

    return path if current == goal else None


# 10. Stochastic Hill Climbing
def stochastic_hill_climbing(start, goal):
    current = start
    path = [current]

    while True:
        neighbors = get_neighbors(current)
        better_neighbors = [n for n in neighbors if misplaced_tiles(n, goal) < misplaced_tiles(current, goal)]

        if not better_neighbors:
            break

        current = random.choice(better_neighbors)
        path.append(current)

        if current == goal:
            return path

    return path if current == goal else None


# 11. AND-OR Tree Search
def and_or_graph_search(state, goal):
    return or_search(state, goal, [], 0, 50)  # Bắt đầu với độ sâu 0 và giới hạn 50


def or_search(state, goal, path, depth, max_depth):
    print(f"Đang xét OR: {state}, Depth: {depth}")

    if depth > max_depth:
        print("Vượt quá độ sâu cho phép.")
        return None

    if state == goal:
        return [state]

    if state in path:  # Kiểm tra vòng lặp
        print(f"Phát hiện vòng lặp tại: {state}")
        return None

    for neighbor in get_neighbors(state):
        plan = and_search(neighbor, goal, path + [state], depth + 1, max_depth)
        if plan:
            return [state] + plan
    return None


def and_search(state, goal, path, depth, max_depth):
    print(f"Đang xét AND: {state}, Depth: {depth}")
    return or_search(state, goal, path, depth, max_depth)


# ============================
# Belief State Search
# ============================

def belief_state_search(start, goal):
    belief = {start}
    path = [start]
    visited = set()

    while belief:
        current_belief = set()

        for state in belief:
            if state == goal:
                return path

            if state not in visited:
                visited.add(state)
                neighbors = get_neighbors(state)
                for neighbor in neighbors:
                    current_belief.add(neighbor)

        if not current_belief - visited:
            break

        best_state = min(current_belief - visited,
                         key=lambda x: misplaced_tiles(x, goal),
                         default=None)

        if best_state:
            path.append(best_state)
            belief = {best_state}
        else:
            belief = current_belief - visited

    return path if path[-1] == goal else None



# Vẽ bảng 8-puzzle
def draw_board(screen, state, width=WIDTH, height=HEIGHT):
    screen.fill(WHITE)

    # Tính toán vị trí vẽ ở giữa màn hình
    offset_x = (width - TILE_SIZE * 3) // 2
    offset_y = height // 3

    # Vẽ nền cho bảng
    board_rect = pygame.Rect(offset_x - 10, offset_y - 10, TILE_SIZE * 3 + 20, TILE_SIZE * 3 + 20)
    pygame.draw.rect(screen, (230, 230, 230), board_rect, border_radius=15)

    # Vẽ từng ô
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            rect = pygame.Rect(offset_x + j * TILE_SIZE, offset_y + i * TILE_SIZE, TILE_SIZE, TILE_SIZE)

            if value != 0:  # Ô có số
                pygame.draw.rect(screen, GRAY, rect, border_radius=8)
                pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)
                font = pygame.font.Font(None, 72)
                text = font.render(str(value), True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            else:  # Ô trống
                pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, GRAY, rect, 1, border_radius=8)

    pygame.display.update()


# Vẽ các nút lựa chọn thuật toán
def draw_buttons(screen, font, mouse_pos):
    button_rects = []
    buttons = [
        "IDDFS", "BFS", "DFS", "Greedy", "A*",
        "Genetic", "Annealing", "Hill Climbing",
        "Steepest-Ascent", "Stochastic", "AND-OR", "Belief State"
    ]

    # Hiển thị tiêu đề
    title = font.render("Chọn thuật toán:", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # Tính toán layout nút
    buttons_per_column = 6
    columns = (len(buttons) + buttons_per_column - 1) // buttons_per_column
    column_width = WIDTH // columns

    for i, text in enumerate(buttons):
        column = i // buttons_per_column
        row = i % buttons_per_column

        rect_x = column_width * column + (column_width - 200) // 2
        rect_y = 70 + row * 60

        button_rect = pygame.Rect(rect_x, rect_y, 200, 50)
        button_rects.append(button_rect)

        # Đổi màu khi hover
        color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, color, button_rect, border_radius=10)

        # Vẽ text
        button_text = font.render(text, True, TEXT_COLOR)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)

    pygame.display.update()
    return button_rects


# Sao chép lời giải vào clipboard
def copy_solution_to_clipboard(solution):
    solution_str = "\n".join([str(state) for state in solution])
    pyperclip.copy(solution_str)
    print("Lời giải đã được sao chép vào clipboard.")


# Hiển thị thông báo
def draw_message(screen, message, y_pos=HEIGHT - 100):
    font = pygame.font.Font(None, 30)
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, y_pos))

    # Vẽ nền cho thông báo
    bg_rect = pygame.Rect(text_rect.x - 10, text_rect.y - 5, text_rect.width + 20, text_rect.height + 10)
    pygame.draw.rect(screen, (240, 240, 240), bg_rect, border_radius=5)
    pygame.draw.rect(screen, GRAY, bg_rect, 1, border_radius=5)

    screen.blit(text, text_rect)
    pygame.display.update()


def backtracking(start, goal):
    """
    Thuật toán Backtracking đơn giản cho 8-puzzle
    """
    print("Đang giải bằng Backtracking...")
    visited = set()
    path = []
    return backtrack_search(start, goal, visited, path)


def backtrack_search(state, goal, visited, path):
    """
    Hàm đệ quy cho backtracking
    """
    # Nếu đã tìm thấy trạng thái đích
    if state == goal:
        return path + [state]

    # Kiểm tra nếu trạng thái này đã được thăm
    if state in visited:
        return None

    # Đánh dấu trạng thái này đã được thăm
    visited.add(state)
    path.append(state)

    # Lấy danh sách các trạng thái kề
    neighbors = get_neighbors(state)
    # Sắp xếp các trạng thái kề theo heuristic để cải thiện hiệu suất
    neighbors.sort(key=lambda x: misplaced_tiles(x, goal))

    # Thử từng trạng thái kề
    for neighbor in neighbors:
        result = backtrack_search(neighbor, goal, visited, path[:])
        if result:
            return result

    # Nếu không tìm thấy giải pháp từ trạng thái này
    return None


# 14. Forward Checking
def forward_checking(start, goal):
    """
    Thuật toán Forward Checking cho 8-puzzle

    Ý tưởng chính: Mỗi khi chọn một trạng thái, kiểm tra xem các trạng thái tiếp theo
    có khả năng dẫn đến giải pháp hay không trước khi đi sâu hơn
    """
    print("Đang giải bằng Forward Checking...")
    visited = set()
    path = []
    return forward_check_search(start, goal, visited, path)


def is_promising(state, goal, visited):
    """
    Kiểm tra xem một trạng thái có triển vọng dẫn đến trạng thái đích hay không
    bằng cách kiểm tra xem có ít nhất một lối đi tiếp theo chưa được thăm
    """
    # Nếu khoảng cách Manhattan quá lớn, có thể coi là không triển vọng
    if manhattan_distance(state, goal) > 30:
        return False

    # Kiểm tra xem có ít nhất một lối đi tiếp theo chưa được thăm
    neighbors = get_neighbors(state)
    return any(neighbor not in visited for neighbor in neighbors)


def forward_check_search(state, goal, visited, path):
    """
    Hàm đệ quy cho forward checking
    """
    # Nếu đã tìm thấy trạng thái đích
    if state == goal:
        return path + [state]

    # Kiểm tra nếu trạng thái này đã được thăm
    if state in visited:
        return None

    # Đánh dấu trạng thái này đã được thăm
    visited.add(state)
    path.append(state)

    # Lấy danh sách các trạng thái kề và sắp xếp theo heuristic
    neighbors = get_neighbors(state)
    neighbors.sort(key=lambda x: misplaced_tiles(x, goal))

    # Lọc các trạng thái triển vọng trước khi đệ quy
    promising_neighbors = [n for n in neighbors if n not in visited and is_promising(n, goal, visited)]

    # Nếu không có trạng thái triển vọng, quay lui sớm
    if not promising_neighbors:
        return None

    # Thử từng trạng thái triển vọng
    for neighbor in promising_neighbors:
        result = forward_check_search(neighbor, goal, visited.copy(), path[:])
        if result:
            return result

    # Nếu không tìm thấy giải pháp từ trạng thái này
    return None


# 15. Min-Conflicts
def min_conflicts(start, goal, max_steps=1000):
    """
    Thuật toán Min-Conflicts cho 8-puzzle

    Ý tưởng: Bắt đầu từ một trạng thái ngẫu nhiên và lặp đi lặp lại
    việc chọn biến (vị trí) có xung đột và gán giá trị mới cho nó
    để giảm thiểu số lượng xung đột
    """
    print("Đang giải bằng Min-Conflicts...")

    # Đối với 8-puzzle, ta sẽ coi mỗi ô là một biến
    # và giá trị của biến là số trên ô đó
    current = start
    path = [current]

    for _ in range(max_steps):
        # Nếu đã đạt đến trạng thái đích
        if current == goal:
            return path

        # Tìm các ô có thể di chuyển (các ô kề với ô trống)
        empty_i, empty_j = find_empty(current)
        movable_positions = []

        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Up, Down, Left, Right
            new_i, new_j = empty_i + di, empty_j + dj
            if 0 <= new_i < 3 and 0 <= new_j < 3:
                movable_positions.append((new_i, new_j))

        # Nếu không có vị trí nào có thể di chuyển (không thể xảy ra với 8-puzzle)
        if not movable_positions:
            break

        # Tính số xung đột cho mỗi vị trí có thể di chuyển
        min_conflicts_pos = None
        min_conflicts_value = float('inf')

        for pos_i, pos_j in movable_positions:
            # Tạo trạng thái mới bằng cách di chuyển ô này đến ô trống
            new_state = [list(row) for row in current]
            new_state[empty_i][empty_j], new_state[pos_i][pos_j] = new_state[pos_i][pos_j], new_state[empty_i][empty_j]
            new_state = tuple(tuple(row) for row in new_state)

            # Tính số xung đột (số ô không đúng vị trí)
            conflicts = misplaced_tiles(new_state, goal)

            # Cập nhật nếu tìm thấy trạng thái có ít xung đột hơn
            if conflicts < min_conflicts_value:
                min_conflicts_value = conflicts
                min_conflicts_pos = (pos_i, pos_j)

        # Di chuyển ô có ít xung đột nhất
        if min_conflicts_pos:
            pos_i, pos_j = min_conflicts_pos
            new_state = [list(row) for row in current]
            new_state[empty_i][empty_j], new_state[pos_i][pos_j] = new_state[pos_i][pos_j], new_state[empty_i][empty_j]
            current = tuple(tuple(row) for row in new_state)
            path.append(current)
        else:
            # Không có vị trí nào giảm xung đột, thoát
            break

    # Trả về đường đi tìm được nếu đã đạt đến mục tiêu
    return path if current == goal else None


# Cập nhật danh sách thuật toán trong hàm main
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("8-Puzzle Solver")
    clock = pygame.time.Clock()

    # Kiểm tra tính khả thi của bài toán
    if not is_solvable(start_state):
        print("Bài toán không có lời giải!")
        draw_message(screen, "Bài toán không có lời giải!")
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    font = pygame.font.Font(None, 30)
    selected_algorithm = None

    # Màn hình chọn thuật toán
    while selected_algorithm is None:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(WHITE)
        button_rects = draw_buttons(screen, font, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        selected_algorithm = i + 1
        clock.tick(FPS)

    # Danh sách các thuật toán (đã cập nhật)
    algorithms = [
        iterative_deepening_search, bfs, dfs, greedy, a_star,
        genetic_algorithm, simulated_annealing,
        simple_hill_climbing, steepest_ascent_hill_climbing, stochastic_hill_climbing,
        and_or_graph_search, belief_state_search,
        backtracking, forward_checking, min_conflicts  # Thêm 3 thuật toán mới
    ]

    algorithm_names = [
        "IDDFS", "BFS", "DFS", "Greedy", "A*",
        "Genetic Algorithm", "Simulated Annealing",
        "Hill Climbing", "Steepest-Ascent Hill Climbing", "Stochastic Hill Climbing",
        "AND-OR Tree Search", "Belief State Search",
        "Backtracking", "Forward Checking", "Min-Conflicts"  # Thêm tên thuật toán mới
    ]

    # Hiển thị trạng thái đầu
    screen.fill(WHITE)
    draw_board(screen, start_state)
    draw_message(screen, f"Đang giải bằng thuật toán: {algorithm_names[selected_algorithm - 1]}")
    pygame.display.update()

    # Giải bài toán
    start_time = time.time()
    solution = algorithms[selected_algorithm - 1](start_state, goal_state)
    end_time = time.time()

    execution_time = end_time - start_time
    print(f"Thời gian thực thi: {execution_time:.4f} giây")

    # Hiển thị lời giải
    if solution:
        print(f"Số bước giải: {len(solution)}")
        for state in solution:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill(WHITE)
            draw_board(screen, state)
            draw_message(screen,
                         f"Bước {solution.index(state) + 1}/{len(solution)} - {algorithm_names[selected_algorithm - 1]}")
            draw_message(screen, f"Thời gian: {execution_time:.4f} giây", y_pos=HEIGHT - 60)
            pygame.display.update()
            pygame.time.wait(500)  # Đợi 0.5 giây giữa các bước

        copy_solution_to_clipboard(solution)

        # Hiển thị thông báo hoàn thành
        draw_message(screen, " Hoàn thành! Lời giải đã được sao chép vào clipboard.", y_pos=HEIGHT - 30)
        pygame.display.update()

        # Đợi để người dùng xem kết quả
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    waiting = False
    else:
        print("Không tìm thấy lời giải!")
        draw_message(screen, "Không tìm thấy lời giải!")
        pygame.time.wait(3000)

    pygame.quit()


# Cập nhật hàm vẽ nút chọn thuật toán
def draw_buttons(screen, font, mouse_pos):
    button_rects = []
    buttons = [
        "IDDFS", "BFS", "DFS", "Greedy", "A*",
        "Genetic", "Annealing", "Hill Climbing",
        "Steepest-Ascent", "Stochastic", "AND-OR", "Belief State",
        "Backtracking", "Forward Checking", "Min-Conflicts"  # Thêm 3 nút mới
    ]

    # Hiển thị tiêu đề
    title = font.render("Chọn thuật toán:", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

    # Tính toán layout nút
    buttons_per_column = 5
    columns = (len(buttons) + buttons_per_column - 1) // buttons_per_column
    column_width = WIDTH // columns

    for i, text in enumerate(buttons):
        column = i // buttons_per_column
        row = i % buttons_per_column

        rect_x = column_width * column + (column_width - 200) // 2
        rect_y = 70 + row * 60

        button_rect = pygame.Rect(rect_x, rect_y, 200, 50)
        button_rects.append(button_rect)

        # Đổi màu khi hover
        color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, color, button_rect, border_radius=10)

        # Vẽ text
        button_text = font.render(text, True, TEXT_COLOR)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)

    pygame.display.update()
    return button_rects


if __name__ == "__main__":
    main()



