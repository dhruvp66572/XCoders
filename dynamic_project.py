import tkinter as tk
import numpy as np
from collections import defaultdict
import random
from tkinter import filedialog, messagebox, simpledialog

# Function to generate a random grid with obstacles
def generate_random_grid(rows, cols, obstacle_count):
    grid = [[' ' for _ in range(cols)] for _ in range(rows)]
    # Place obstacles
    for _ in range(obstacle_count):
        while True:
            r, c = random.randint(0, rows - 1), random.randint(0, cols - 1)
            if grid[r][c] == ' ':
                grid[r][c] = 'X'
                break
    return grid

# Function to read grid and bot positions from multiple files
def read_multiple_grids(file_list):
    grids = []  # List to store grids
    bot_positions_list = []  # List to store bot positions for each grid

    for filename in file_list:
        grid = []
        bot_positions = {}  # Dictionary to store autobot start and destination positions
        with open(filename, 'r') as file:
            for r, line in enumerate(file):
                row = line.strip().split()
                grid.append(row)
                for c, cell in enumerate(row):
                    if cell.startswith('A') or cell.startswith('B'):
                        bot_positions[cell] = (r, c)
        
        grids.append(grid)
        bot_positions_list.append(bot_positions)
    
    return grids, bot_positions_list

# Define actions and their corresponding moves
actions = {
    0: (0, -1),  # Left
    1: (0, 1),   # Right
    2: (-1, 0),  # Up
    3: (1, 0)    # Down
}

# Define autobot class using Q-learning
class AutobotQLearning:
    def __init__(self, start, dest, grid, name, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.pos = start
        self.dest = dest
        self.grid = grid
        self.name = name
        self.q_table = defaultdict(lambda: [0, 0, 0, 0])
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.steps = 0
        self.time_taken = None
        self.reached = False
        self.learned_path = []
        self.rows, self.cols = len(self.grid), len(self.grid[0])
    
    def get_state(self):
        return self.pos

    def choose_action(self):
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
        else:
            return -1
    
    def is_valid_position(self, pos):
        return 0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols and self.grid[pos[0]][pos[1]] != 'X'

    def move(self, bots):
        if self.pos == self.dest:
            if not self.reached:
                self.reached = True
                self.time_taken = self.steps
            return

        state = self.get_state()
        action = self.choose_action()
        new_pos = (self.pos[0] + actions[action][0], self.pos[1] + actions[action][1])
        
        if self.is_valid_position(new_pos) and not any(bot.pos == new_pos for bot in bots if bot != self):
            reward = self.get_reward(new_pos)
            next_state = new_pos
            self.update_q_value(state, action, reward, next_state)
            self.pos = new_pos
            self.steps += 1
            self.learned_path.append(self.pos)
        else:
            reward = -10
            self.update_q_value(state, action, reward, state)

# GUI Setup with dynamic matrix switching
def create_gui(grids, bot_positions_list):
    root = tk.Tk()
    root.title("Autobot Warehouse Simulation")

    # Initial grid setup
    current_grid_idx = 0  # Track which grid is active

    # Dropdown for selecting a grid
    def select_grid(index):
        nonlocal current_grid_idx
        current_grid_idx = index
        update_grid()

    # Load Autobots dynamically based on selected grid
    def load_bots_for_grid(grid_index):
        bot_positions = bot_positions_list[grid_index]
        bots = []
        for bot_name, positions in bot_positions.items():
            start, dest = positions
            print(f"Bot {bot_name}: Start={start}, Dest={dest}")  # Debug print
            bots.append(AutobotQLearning(start=start, dest=dest, grid=grids[grid_index], name=bot_name))
        return bots

    # Canvas for drawing grid
    canvas = tk.Canvas(root, width=500, height=500)
    canvas.grid(row=1, column=0)

    cell_size = 100

    def update_grid():
        canvas.delete("all")  # Clear previous grid
        grid = grids[current_grid_idx]
        rows, cols = len(grid), len(grid[0])

        # Dynamically adjust canvas size based on grid dimensions
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

    # Animate bots for each grid
    def update_bots(bots):
        def animate_bots(bots):
            canvas.delete("bot")
            for bot in bots:
                current_pos = bot.pos
                if 0 <= current_pos[0] < len(grids[current_grid_idx]) and 0 <= current_pos[1] < len(grids[current_grid_idx][0]):
                    canvas.create_text(current_pos[1] * cell_size + 50, current_pos[0] * cell_size + 50, 
                                       text="🚗" if bot.name == "Bot 1" else "🚙", font=("Arial", 24), tags="bot")
                if bot.pos == bot.dest:
                    print(f"{bot.name} reached its destination in {bot.time_taken} steps!")
            root.update()

        def update():
            for bot in bots:
                bot.move(bots)
            animate_bots(bots)
            root.after(500, update)

        update()

    # Dropdown for grid selection
    dropdown = tk.OptionMenu(root, tk.StringVar(value="Select Grid"), *[f"Grid {i+1}" for i in range(len(grids))], command=lambda value: select_grid(int(value.split()[-1]) - 1))
    dropdown.grid(row=0, column=0)

    # Initial grid and bots
    update_grid()

    root.mainloop()

# File dialog to select multiple grid files or generate new grids
def open_files():
    # Ask user if they want to load from files or generate a grid
    choice = messagebox.askquestion("Load Grids", "Do you want to load grid files? (Yes for loading, No for generating new grid)")
    if choice == 'yes':
        file_paths = filedialog.askopenfilenames(title="Select Matrix Files", filetypes=[("Text files", "*.txt")])
        if file_paths:
            grids, bot_positions_list = read_multiple_grids(file_paths)
            create_gui(grids, bot_positions_list)
        else:
            messagebox.showwarning("No files selected", "Please select at least one file!")
    else:
        # Prompt user for grid dimensions and obstacle count
        rows = simpledialog.askinteger("Input", "Enter number of rows:")
        cols = simpledialog.askinteger("Input", "Enter number of columns:")
        obstacle_count = simpledialog.askinteger("Input", "Enter number of obstacles:")
        grid = generate_random_grid(rows, cols, obstacle_count)

        # Get bot starting and ending positions
        bot_positions = {}
        while True:
            bot_name = simpledialog.askstring("Input", "Enter bot name (or leave blank to finish):")
            if not bot_name:
                break
            start = simpledialog.askstring("Input", f"Enter start position for {bot_name} (format: row,column):")
            dest = simpledialog.askstring("Input", f"Enter destination position for {bot_name} (format: row,column):")
            if start and dest:
                start = tuple(map(int, start.split(',')))
                dest = tuple(map(int, dest.split(',')))
                bot_positions[bot_name] = (start, dest)

        grids = [grid]
        bot_positions_list = [bot_positions]
        create_gui(grids, bot_positions_list)

# Main entry point to start the program
if __name__ == "__main__":
    open_files()
