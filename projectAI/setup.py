from collections import deque
import heapq
import numpy as np

MAP = [
    ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
    ['1',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','1'],
    ['1','B','1','1',' ','1','1','1',' ','1',' ','1','1','1',' ','1','1','B','1'],
    ['1',' ',' ',' ',' ','1',' ',' ',' ','1',' ',' ',' ','1',' ',' ',' ',' ','1'],
    ['1','1',' ','1',' ','1',' ','1',' ','1',' ','1',' ','1',' ','1',' ','1','1'],
    ['1',' ',' ','1',' ',' ',' ','1',' ',' ',' ','1',' ',' ',' ','1',' ',' ','1'],
    ['1',' ','1','1','1','1',' ','1','1','1','1','1',' ','1','1','1','1',' ','1'],
    ['1',' ',' ',' ',' ',' ',' ',' ',' ','r',' ',' ',' ',' ',' ',' ',' ',' ','1'],
    ['1','1',' ','1','1','1',' ','1','1','-','1','1',' ','1','1','1',' ','1','1'],
    ['1',' ',' ',' ',' ','1',' ','1','s','p','o','1',' ','1',' ',' ',' ',' ','1'],
    ['1','1',' ','1',' ','1',' ','1','1','1','1','1',' ','1',' ','1',' ','1','1'],
    ['1',' ',' ','1',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','1',' ',' ','1'],
    ['1',' ','1','1','1','1',' ','1','1','1','1','1',' ','1','1','1','1',' ','1'],
    ['1',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','1'],
    ['1','1','1',' ','1','1','1',' ','1','1','1',' ','1','1','1',' ','1','1','1'],
    ['1',' ',' ',' ','1',' ',' ',' ',' ','P',' ',' ',' ',' ','1',' ',' ',' ','1'],
    ['1','B','1',' ','1',' ','1',' ','1','1','1',' ','1',' ','1',' ','1','B','1'],
    ['1',' ','1',' ',' ',' ','1',' ',' ',' ',' ',' ','1',' ',' ',' ','1',' ','1'],
    ['1',' ','1','1','1',' ','1','1','1',' ','1','1','1',' ','1','1','1',' ','1'],
    ['1',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','1'],
    ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1']
]
BOARD_RATIO = (len(MAP[0]), len(MAP))
CHAR_SIZE = 32
WIDTH, HEIGHT = (BOARD_RATIO[0] * CHAR_SIZE, BOARD_RATIO[1] * CHAR_SIZE)
NAV_HEIGHT = 64
PLAYER_SPEED = CHAR_SIZE // 8
GHOST_SPEED = 2 



def bfs_search(grid, start, destination):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start, [start])]) #dùng queue
    visited = set()
    visited.add(tuple(start))


    directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
    while queue:
        (current, path) = queue.popleft()  

        # Kiểm tra nếu đã đến đích
        if current == destination:
            return path

        # Thử di chuyển đến các hướng kế tiếp
        for direction in directions:
            next_row, next_col = current[0] + direction[0], current[1] + direction[1]

            # Kiểm tra nếu tọa độ tiếp theo nằm trong phạm vi và không phải là tường
            if 0 <= next_row < rows and 0 <= next_col < cols and grid[next_row][next_col] != '1':
                next_position = (next_row, next_col)
                if next_position not in visited:
                    visited.add(next_position)  # Đánh dấu là đã thăm
                    queue.append((next_position, path + [next_position]))  # Thêm vào hàng đợi với đường đi mới

    return []


def heuristic(a, b):
    # Khoảng cách Manhattan : |x1 - x2| + |y1 - y2|
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(grid, start, destination):
    rows, cols = len(grid), len(grid[0])
    open_list = []
    heapq.heappush(open_list, (0, start))  # (f_score, node)
    g_scores = {start: 0}  # Chi phí từ start đến mỗi node
    f_scores = {start: heuristic(start, destination)}  # f_score = g_score + h_score
    came_from = {}

    '''
    grid: Lưới (grid) đại diện cho bản đồ, với các ô có thể là "0" (trống) hoặc "1" (chướng ngại vật).
    start: Vị trí bắt đầu (start node), là một tuple (x, y) chỉ tọa độ của điểm bắt đầu.
    destination: Vị trí đích (destination node), là một tuple (x, y) chỉ tọa độ của điểm đích.
    open_list: Một danh sách ưu tiên (sử dụng heapq để quản lý) chứa các ô sẽ được khám phá. Các phần tử là tuple (f_score, node) trong đó f_score = g_score + h_score.
    g_scores: Một từ điển (dictionary) lưu chi phí từ điểm bắt đầu đến mỗi điểm (node). Khởi tạo với điểm bắt đầu có g_score = 0.
    f_scores: Một từ điển lưu giá trị f_score cho mỗi điểm (node), tính bằng g_score + h_score.
    came_from: Một từ điển lưu trữ điểm đến của mỗi điểm (node) trong quá trình tìm kiếm. Dùng để xây dựng lại đường đi khi tìm thấy đích.
    
    '''
    # Các hướng di chuyển: lên, trái, xuống, phải
    directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]

    while open_list:
        _, current = heapq.heappop(open_list)

        if current == destination:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]  # Đảo ngược lại để có đường đi từ start đến destination
        '''
        Thuật toán tiếp tục lặp qua các điểm trong open_list, chọn điểm có f_score nhỏ nhất (sử dụng heapq).
        Nếu điểm current là điểm đích (destination), thuật toán sẽ xây dựng lại đường đi từ điểm đích về điểm bắt đầu, sử dụng từ điển came_from.
        Đường đi sẽ được đảo ngược ([::-1]) để có đường đi từ điểm bắt đầu đến điểm đích.
        '''
        for direction in directions:
            next_row, next_col = current[0] + direction[0], current[1] + direction[1]

            if 0 <= next_row < rows and 0 <= next_col < cols and grid[next_row][next_col] != '1':
                next_position = (next_row, next_col)
                tentative_g_score = g_scores[current] + 1

                if next_position not in g_scores or tentative_g_score < g_scores[next_position]:
                    came_from[next_position] = current
                    g_scores[next_position] = tentative_g_score
                    f_scores[next_position] = tentative_g_score + heuristic(next_position, destination)
                    heapq.heappush(open_list, (f_scores[next_position], next_position))

        '''
        Đối với mỗi điểm lân cận của current, thuật toán tính toán chi phí tạm thời tentative_g_score là chi phí từ điểm bắt đầu đến điểm lân cận này.
        Nếu điểm lân cận chưa được khám phá hoặc có chi phí g_score nhỏ hơn chi phí hiện tại, thuật toán cập nhật lại came_from, g_scores, và f_scores, sau đó thêm điểm này vào open_list.
        '''

    return []


def manhattan_distance(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

# ----------------- Q-Learning & Beam Search -----------------

def q_learning_search(grid, start, destination, episodes=500, alpha=0.7, gamma=0.9, epsilon=0.1, max_steps=200):
    """
    Q-learning tìm đường đi từ start đến destination trên grid.
    Trả về đường đi tốt nhất tìm được.
    """
    rows, cols = len(grid), len(grid[0])
    state_space = [(r, c) for r in range(rows) for c in range(cols) if grid[r][c] != '1']
    state_to_idx = {s: i for i, s in enumerate(state_space)}
    n_states = len(state_space)
    n_actions = 4
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

    Q = np.zeros((n_states, n_actions))

    for _ in range(episodes):
        state = start
        for _ in range(max_steps):
            s_idx = state_to_idx[state]
            if np.random.rand() < epsilon:
                action_idx = np.random.randint(n_actions)
            else:
                action_idx = np.argmax(Q[s_idx])
            dr, dc = actions[action_idx]
            next_state = (state[0] + dr, state[1] + dc)
            if 0 <= next_state[0] < rows and 0 <= next_state[1] < cols and grid[next_state[0]][next_state[1]] != '1':
                reward = 100 if next_state == destination else -1
                ns_idx = state_to_idx[next_state]
                Q[s_idx, action_idx] += alpha * (reward + gamma * np.max(Q[ns_idx]) - Q[s_idx, action_idx])
                state = next_state
                if state == destination:
                    break
            else:
                Q[s_idx, action_idx] += alpha * (-10 - Q[s_idx, action_idx])  # phạt va vào tường

    # Truy vết đường đi tốt nhất
    path = [start]
    state = start
    for _ in range(max_steps):
        if state == destination:
            break
        s_idx = state_to_idx[state]
        action_idx = np.argmax(Q[s_idx])
        dr, dc = actions[action_idx]
        next_state = (state[0] + dr, state[1] + dc)
        if next_state not in state_to_idx or next_state in path:
            break
        path.append(next_state)
        state = next_state
    if path[-1] != destination:
        return []
    return path

def beam_search(grid, start, destination, beam_width=3, max_steps=200):
    """
    Beam search tìm đường đi từ start đến destination trên grid.
    """
    rows, cols = len(grid), len(grid[0])
    from heapq import heappush, heappop

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    queue = [ (heuristic(start, destination), [start]) ]
    for _ in range(max_steps):
        next_queue = []
        for _, path in queue:
            current = path[-1]
            if current == destination:
                return path
            for dr, dc in actions:
                nr, nc = current[0] + dr, current[1] + dc
                next_state = (nr, nc)
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '1' and next_state not in path:
                    heappush(next_queue, (heuristic(next_state, destination), path + [next_state]))
        # Giữ lại beam_width đường đi tốt nhất
        queue = [heappop(next_queue) for _ in range(min(beam_width, len(next_queue)))] if next_queue else []
        if not queue:
            break
    return []

def simulated_annealing_search(grid, start, destination, max_steps=500, initial_temp=100.0, cooling_rate=0.99):
    """
    Tìm đường đi bằng simulated annealing từ start đến destination trên grid.
    """
    import random
    import math
    rows, cols = len(grid), len(grid[0])
    def neighbors(pos):
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = pos[0]+dr, pos[1]+dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '1':
                yield (nr, nc)
    current = start
    path = [current]
    temp = initial_temp
    for _ in range(max_steps):
        if current == destination:
            return path
        nexts = list(neighbors(current))
        if not nexts:
            break
        next_pos = random.choice(nexts)
        delta_e = heuristic(current, destination) - heuristic(next_pos, destination)
        if delta_e > 0 or random.random() < math.exp(delta_e / max(temp, 1e-6)):
            current = next_pos
            path.append(current)
        temp *= cooling_rate
    return path if path and path[-1] == destination else []

def ac3(grid, variables, domains, constraints):
    """
    AC-3 algorithm for arc consistency.
    """
    from collections import deque
    queue = deque([(xi, xj) for xi in variables for xj in constraints[xi]])
    while queue:
        xi, xj = queue.popleft()
        revised = False
        for x in set(domains[xi]):
            if not any(abs(x[0]-y[0])+abs(x[1]-y[1])==1 for y in domains[xj]):
                domains[xi].remove(x)
                revised = True
        if revised:
            if not domains[xi]:
                return False
            for xk in constraints[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True

def backtrack_with_ac3(grid, start, destination, max_steps=500):
    """
    Backtracking kết hợp AC-3 để tìm đường đi từ start đến destination.
    """
    rows, cols = len(grid), len(grid[0])
    variables = []
    domains = {}
    constraints = {}
    for step in range(max_steps):
        variables.append(step)
        domains[step] = []
        constraints[step] = []
    for step in range(max_steps):
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != '1':
                    domains[step].append((r, c))
    for step in range(max_steps-1):
        constraints[step].append(step+1)
        constraints[step+1].append(step)
    domains[0] = [start]
    domains[max_steps-1] = [destination]
    def is_consistent(assignment, step, value):
        if step > 0 and abs(value[0]-assignment[step-1][0])+abs(value[1]-assignment[step-1][1]) != 1:
            return False
        if value in assignment.values():
            return False
        return True
    def backtrack(assignment, step):
        if step == max_steps:
            if assignment[step-1] == destination:
                return [assignment[i] for i in range(max_steps)]
            return None
        for value in domains[step]:
            if is_consistent(assignment, step, value):
                assignment[step] = value
                if ac3(grid, variables, domains, constraints):
                    result = backtrack(assignment, step+1)
                    if result:
                        return result
                del assignment[step]
        return None
    result = backtrack({}, 0)
    if result:
        # Cắt bỏ các bước dư thừa (dừng ở destination)
        path = []
        for pos in result:
            path.append(pos)
            if pos == destination:
                break
        return path
    return []