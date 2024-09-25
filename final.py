import tkinter as tk
import numpy as np
from collections import defaultdict
import random
from tkinter import filedialog, messagebox, simpledialog

# Function to generate a random grid with obstacles
def generate_random_grid(rows, cols, obstacle_count):
    grid = [['.' for _ in range(cols)] for _ in range(rows)]
    for _ in range(obstacle_count):
        while True:
            r, c = random.randint(0, rows - 1), random.randint(0, cols - 1)
            if grid[r][c] == '.':
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
                    if cell.startswith('A'):
                        # A represents the start position of a bot
                        bot_positions[cell] = (r, c)
                    elif cell.startswith('B'):
                        # B represents the destination of a bot
                        bot_positions[cell.replace('B', 'A') + "_dest"] = (r, c)
        
        grids.append(grid)
        bot_positions_list.append(bot_positions)
    
    return grids, bot_positions_list

# Define commands and their corresponding moves
actions = {
    0: (0, 1),   # Forward
    1: (0, -1),  # Reverse
    2: (-1, 0),  # Left
    3: (1, 0),   # Right
    4: (0, 0)    # Wait
}

commands_dict = {
    0: 'Forward',
    1: 'Reverse',
    2: 'Left',
    3: 'Right',
    4: 'Wait'
}

# Define autobot class using Q-learning
class AutobotQLearning:
    def __init__(self, start, dest, grid, name, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.pos = start
        self.dest = dest
        self.grid = grid
        self.name = name
        self.q_table = defaultdict(lambda: [0, 0, 0, 0, 0])  # Added Wait command
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.steps = 0
        self.time_taken = 0  # Track time taken in seconds
        self.reached = False
        self.learned_path = []
        self.rows, self.cols = len(self.grid), len(self.grid[0])
        self.command_log = []  # Log of each command issued to this bot
        self.command_count = 0  # Total number of commands issued

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

    def move(self, bots, collision_cells):
        if self.pos == self.dest:
            if not self.reached:
                self.reached = True
                self.command_log.append(f"{self.name} reached its destination in {self.steps} steps!")
            return

        state = self.get_state()
        action = self.choose_action()
        new_pos = (self.pos[0] + actions[action][0], self.pos[1] + actions[action][1])

        # Check if another bot is at the same position
        if self.is_valid_position(new_pos) and not any(bot.pos == new_pos for bot in bots if bot != self):
            reward = self.get_reward(new_pos)
            next_state = new_pos
            self.update_q_value(state, action, reward, next_state)
            self.pos = new_pos
            self.steps += 1
            self.command_count += 1
            self.learned_path.append(self.pos)
            self.time_taken += 1  # Increment time taken for each step (1 unit)
            self.command_log.append(f"{self.name}: {commands_dict[action]}")
        else:
            # Wait if there's a potential collision or invalid move
            reward = -10
            self.update_q_value(state, 4, reward, state)  # Use Wait command
            collision_cells.add(self.pos)
            self.command_log.append(f"{self.name}: Wait (collision/invalid move)")
            self.command_count += 1
            self.steps += 1
            self.time_taken += 1

    # Output performance metrics for each bot
    def get_performance_metrics(self):
        return f"{self.name}: Total Time: {self.time_taken}, Total Commands: {self.command_count}, Steps: {self.steps}"

# GUI Setup with dynamic matrix switching
def create_gui(grids, bot_positions_list):
    root = tk.Tk()
    root.title("Autobot Warehouse Simulation")

    current_grid_idx = 0  # Track which grid is active

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
        canvas.delete("all")  # Clear previous grid
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
            collision_cells = set()  # Track collision cells
            for bot in bots:
                bot.move(bots, collision_cells)

            for bot in bots:
                current_pos = bot.pos
                if 0 <= current_pos[0] < len(grids[current_grid_idx]) and 0 <= current_pos[1] < len(grids[current_grid_idx][0]):
                    # Check if the bot's current position is a collision cell
                    color = 'yellow' if current_pos in collision_cells else 'lightblue'

                    # Show learned path as a trail
                    if bot.learned_path:
                        for pos in bot.learned_path:
                            canvas.create_rectangle(pos[1] * cell_size, pos[0] * cell_size,
                                                    (pos[1] + 1) * cell_size, (pos[0] + 1) * cell_size,
                                                    fill=color, outline="black")
                    canvas.create_text(current_pos[1] * cell_size + 50, current_pos[0] * cell_size + 50, 
                                       text="🚗" if bot.name == "Bot 1" else "🚙", font=("Arial", 24), tags="bot")
                
                # Collect bot status for display
                bot_statuses.append(f"{bot.name}: Steps: {bot.steps}, Time: {round(bot.time_taken, 2)}s")

            # Update the status label with the latest information
            status_label.config(text="\n".join(bot_statuses))
            root.update()

        def update():
            animate_bots(bots)
            root.after(500, update)

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
