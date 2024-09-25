import numpy as np
import random
from collections import defaultdict, deque
import heapq
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Define actions and their corresponding moves
actions = {
    0: (0, 1),   # Forward (right)
    1: (0, -1),  # Reverse (left)
    2: (-1, 0),  # Up
    3: (1, 0),   # Down
    4: (0, 0)    # Wait
}

commands_dict = {
    0: 'Forward',
    1: 'Reverse',
    2: 'Up',
    3: 'Down',
    4: 'Wait'
}

# Priority Queue helper for A* pathfinding
def a_star_pathfinding(start, goal, grid):
    rows, cols = len(grid), len(grid[0])
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = defaultdict(lambda: float('inf'))
    g_score[start] = 0
    f_score = defaultdict(lambda: float('inf'))
    f_score[start] = heuristic(start, goal)

    while open_set:
        current = heapq.heappop(open_set)[1]
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for action in actions.values():
            neighbor = (current[0] + action[0], current[1] + action[1])
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and grid[neighbor[0]][neighbor[1]] != 'X':
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                    if neighbor not in [item[1] for item in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return []  # Return empty if no path found

def heuristic(a, b):
    # Manhattan distance heuristic
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

# Generate a random grid with obstacles
def generate_random_grid(rows, cols, obstacle_count):
    grid = [['.' for _ in range(cols)] for _ in range(rows)]
    for _ in range(obstacle_count):
        while True:
            r, c = random.randint(0, rows - 1), random.randint(0, cols - 1)
            if grid[r][c] == '.':
                grid[r][c] = 'X'
                break
    return grid

# Read multiple grids and bot positions from files
def read_multiple_grids(file_list):
    grids = []
    bot_positions_list = []

    for filename in file_list:
        grid = []
        bot_positions = {}
        with open(filename, 'r') as file:
            for r, line in enumerate(file):
                row = line.strip().split()
                grid.append(row)
                for c, cell in enumerate(row):
                    if cell.startswith('A'):
                        bot_positions[cell] = (r, c)
                    elif cell.startswith('B'):
                        bot_positions[cell.replace('B', 'A') + "_dest"] = (r, c)

        grids.append(grid)
        bot_positions_list.append(bot_positions)
    
    return grids, bot_positions_list

# Define the enhanced Q-learning autobot class with A* integration
class AutobotQLearning:
    def __init__(self, start, dest, grid, name, alpha=0.1, gamma=0.9, epsilon=0.2, epsilon_min=0.01, epsilon_decay=0.995):
        self.pos = start
        self.dest = dest
        self.grid = grid
        self.name = name
        self.q_table = defaultdict(lambda: [0, 0, 0, 0, 0])
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.steps = 0
        self.time_taken = 0
        self.reached = False
        self.learned_path = []
        self.command_log = []
        self.command_count = 0
        self.dynamic_path = deque()
        self.visited_positions = set()  # Track visited positions to avoid revisits
        self.rows, self.cols = len(self.grid), len(self.grid[0])

    def get_state(self):
        return self.pos

    def choose_action(self):
        # Use epsilon-greedy strategy for action selection
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(list(actions.keys()))  # Explore
        else:
            return np.argmax(self.q_table[self.get_state()])  # Exploit best action from Q-table

    def update_q_value(self, state, action, reward, next_state):
        old_value = self.q_table[state][action]
        future_value = max(self.q_table[next_state])
        self.q_table[state][action] = old_value + self.alpha * (reward + self.gamma * future_value - old_value)

    def get_reward(self, new_pos):
        if new_pos == self.dest:
            return 100
        elif self.grid[new_pos[0]][new_pos[1]] == 'X':
            return -100
        elif new_pos in self.visited_positions:
            return -10  # Penalty for revisiting positions
        else:
            distance_reward = -1 * (abs(new_pos[0] - self.dest[0]) + abs(new_pos[1] - self.dest[1]))
            return -1 + distance_reward

    def is_valid_position(self, pos):
        return 0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols and self.grid[pos[0]][pos[1]] != 'X'

    def dynamic_replan(self):
        # Replan frequently if the bot seems stuck
        self.dynamic_path = deque(a_star_pathfinding(self.pos, self.dest, self.grid))

def move(self, bots, collision_cells):
    # Print the current position of the bot in the terminal
    print(f"{self.name} is at {self.pos}")

    if self.pos == self.dest:
        if not self.reached:
            self.reached = True
            self.command_log.append(f"{self.name} reached its destination in {self.steps} steps!")
        return

    state = self.get_state()

    # Use A* planning as a priority strategy for efficiency
    if self.dynamic_path:
        next_move = self.dynamic_path.popleft()
        action = self.action_from_move(self.pos, next_move)
    else:
        action = self.choose_action()

    new_pos = (self.pos[0] + actions[action][0], self.pos[1] + actions[action][1])

    # Always try to replan when blocked or in inefficient situations
    if not self.is_valid_position(new_pos) or any(bot.pos == new_pos for bot in bots if bot != self):
        self.dynamic_replan()  # Immediate replan for blocking conditions
        self.command_log.append(f"{self.name}: Replanning due to blocked/invalid position.")
        action = 4  # Default to wait

    # Move and update Q-table
    if self.is_valid_position(new_pos) and not any(bot.pos == new_pos for bot in bots if bot != self):
        reward = self.get_reward(new_pos)
        next_state = new_pos
        self.update_q_value(state, action, reward, next_state)
        self.pos = new_pos
        self.steps += 1
        self.command_count += 1
        self.learned_path.append(self.pos)
        self.visited_positions.add(self.pos)  # Track visited positions
        self.time_taken += 1
        self.command_log.append(f"{self.name}: {commands_dict[action]}")

        # Print updated information
        print(f"{self.name} moved to {self.pos} | Step: {self.steps} | Command: {commands_dict[action]}")

    else:
        reward = -20  # Higher penalty for wait situations
        self.update_q_value(state, 4, reward, state)
        collision_cells.add(self.pos)
        self.command_log.append(f"{self.name}: Wait (collision/invalid move)")
        self.command_count += 1
        self.steps += 1
        self.time_taken += 1
        
        # Print wait information and command
        print(f"{self.name} is waiting due to collision/invalid move | Current Position: {self.pos} | Step: {self.steps} | Command: Wait")

    self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)  # Faster epsilon decay

        
# GUI Setup with dynamic matrix switching
def create_gui(grids, bot_positions_list):
    root = tk.Tk()
    root.title("Autobot Warehouse Simulation")

    current_grid_idx = 0

    def select_grid(index):
        nonlocal current_grid_idx
        current_grid_idx = index
        update_grid()

    def load_bots_for_grid(grid_index):
        bot_positions = bot_positions_list[grid_index]
        bots = [
            AutobotQLearning(start=bot_positions[bot_name], dest=bot_positions[bot_name + "_dest"], grid=grids[grid_index], name=bot_name)
            for bot_name in bot_positions if not bot_name.endswith("_dest")
        ]
        return bots

    canvas = tk.Canvas(root, width=500, height=500)
    canvas.grid(row=1, column=0)

    status_label = tk.Label(root, text="", font=("Arial", 14))
    status_label.grid(row=2, column=0)

    cell_size = 100

    def update_grid():
        canvas.delete("all")
        grid = grids[current_grid_idx]
        rows, cols = len(grid), len(grid[0])

        canvas.config(width=cols * cell_size, height=rows * cell_size)

        for r in range(rows):
            for c in range(cols):
                x1 = c * cell_size
                y1 = r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                if grid[r][c] == 'X':
                    canvas.create_rectangle(x1, y1, x2, y2, fill='red', outline="black")
                else:
                    canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline="black")

        bots = load_bots_for_grid(current_grid_idx)
        update_bots(bots)

    def update_bots(bots):
        def animate_bots(bots):
            canvas.delete("bot")
            bot_statuses = []
            collision_cells = set()
            
            for bot in bots:
                bot.move(bots, collision_cells)

            for bot in bots:
                current_pos = bot.pos
                start_pos = bot.learned_path[0] if bot.learned_path else bot.pos  # Start position of the bot
                dest_pos = bot.dest  # Destination position of the bot

                if 0 <= current_pos[0] < len(grids[current_grid_idx]) and 0 <= current_pos[1] < len(grids[current_grid_idx][0]):
                    # Determine color based on the bot's state
                    if bot.reached:
                        color = 'green'  # Color for reached destination
                        bot_display_text = f"   {bot.name} \n(Reached)"
                    elif current_pos in collision_cells:
                        color = 'yellow'  # Color for collision
                        bot_display_text = bot.name
                    else:
                        color = 'lightblue'  # Regular moving color
                        bot_display_text = bot.name

                    # Draw source position in blue
                    canvas.create_rectangle(start_pos[1] * cell_size, start_pos[0] * cell_size,
                                            (start_pos[1] + 1) * cell_size, (start_pos[0] + 1) * cell_size,
                                            fill='blue', outline="black")  # Color the source

                    # Draw destination in green if reached
                    canvas.create_rectangle(dest_pos[1] * cell_size, dest_pos[0] * cell_size,
                                            (dest_pos[1] + 1) * cell_size, (dest_pos[0] + 1) * cell_size,
                                            fill='green' if bot.reached else 'white', outline="black")

                    # Show learned path as a trail
                    if bot.learned_path:
                        for pos in bot.learned_path:
                            canvas.create_rectangle(pos[1] * cell_size, pos[0] * cell_size,
                                                    (pos[1] + 1) * cell_size, (pos[0] + 1) * cell_size,
                                                    fill=color, outline="black")
                    
                    # Draw bot with its name
                    canvas.create_text(current_pos[1] * cell_size + 50, current_pos[0] * cell_size + 50,
                                       text=bot_display_text, font=("Arial", 10), tag="bot")

                # Collect bot status for display
                bot_statuses.append(f"{bot.name}: Steps: {bot.steps}, Time: {round(bot.time_taken, 2)}s")

            # Update the status label with the latest information
            status_label.config(text="\n".join(bot_statuses))
            root.update()

        def update():
            animate_bots(bots)
            root.after(1000, update)

        update()

    dropdown = tk.OptionMenu(root, tk.StringVar(value="Select Grid"), *[f"Grid {i+1}" for i in range(len(grids))], 
                             command=lambda value: select_grid(int(value.split()[-1]) - 1))
    dropdown.grid(row=0, column=0)

    update_grid()

    root.mainloop()

# File dialog to select multiple grid files or generate new grids
def open_files():
    choice = messagebox.askquestion("Load Grids", "Do you want to load grid files? (Yes for loading, No for generating new grid)")
    if choice == 'yes':
        file_paths = filedialog.askopenfilenames(title="Select Matrix Files", filetypes=[("Text files", "*.txt")])
        if file_paths:
            grids, bot_positions_list = read_multiple_grids(file_paths)
            create_gui(grids, bot_positions_list)
        else:
            messagebox.showwarning("No files selected", "Please select at least one file!")
    else:
        try:
            rows = simpledialog.askinteger("Input", "Enter number of rows:", minvalue=1)
            cols = simpledialog.askinteger("Input", "Enter number of columns:", minvalue=1)
            obstacle_count = simpledialog.askinteger("Input", "Enter number of obstacles:", minvalue=0)
            
            if rows is None or cols is None or obstacle_count is None:
                raise ValueError("Invalid input.")
                
            grid = generate_random_grid(rows, cols, obstacle_count)

            bot_positions = {}
            while True:
                bot_name = simpledialog.askstring("Input", "Enter bot name (or 'done' to finish):")
                if bot_name == "done":
                    break
                start_row = simpledialog.askinteger("Input", f"Enter start row for {bot_name}:", minvalue=0, maxvalue=rows - 1)
                start_col = simpledialog.askinteger("Input", f"Enter start column for {bot_name}:", minvalue=0, maxvalue=cols - 1)
                dest_row = simpledialog.askinteger("Input", f"Enter destination row for {bot_name}:", minvalue=0, maxvalue=rows - 1)
                dest_col = simpledialog.askinteger("Input", f"Enter destination column for {bot_name}:", minvalue=0, maxvalue=cols - 1)

                bot_positions[bot_name] = (start_row, start_col)
                bot_positions[bot_name + "_dest"] = (dest_row, dest_col)

            grids = [grid]
            bot_positions_list = [bot_positions]

            create_gui(grids, bot_positions_list)

        except Exception as e:
            messagebox.showerror("Error", str(e))

# Start the application
if __name__ == "__main__":
    open_files()
