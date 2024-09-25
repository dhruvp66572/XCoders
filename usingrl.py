import tkinter as tk
import time
import numpy as np
import heapq  # For priority queue implementation
from collections import defaultdict
import random

# Function to read the grid from a file and extract bot positions
def read_grid_and_bots_from_file(filename):
    grid = []
    bot_positions = {}  # Dictionary to store autobot start and destination positions
    
    with open(filename, 'r') as file:
        for r, line in enumerate(file):
            row = line.strip().split()
            grid.append(row)
            for c, cell in enumerate(row):
                if cell.startswith('A') or cell.startswith('B'):
                    bot_positions[cell] = (r, c)
    
    return grid, bot_positions

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
        self.pos = start  # Start position
        self.dest = dest  # Destination position
        self.grid = grid  # Warehouse grid
        self.name = name  # Bot name for identification
        self.q_table = defaultdict(lambda: [0, 0, 0, 0])  # Initialize Q-table with zeros
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.index = 0  # Index to track current position in path
        self.waiting = False  # Flag to indicate if the bot is waiting
        self.learned_path = []  # To store the learned path
    
    def get_state(self):
        return self.pos

    def choose_action(self):
        # Epsilon-greedy strategy to choose the action
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(list(actions.keys()))  # Explore
        else:
            return np.argmax(self.q_table[self.get_state()])  # Exploit best action from Q-table

    def update_q_value(self, state, action, reward, next_state):
        old_value = self.q_table[state][action]
        future_value = max(self.q_table[next_state])  # Max Q-value for the next state
        # Q-Learning formula: Q(s, a) = (1 - alpha) * Q(s, a) + alpha * [reward + gamma * max(Q(s', a'))]
        self.q_table[state][action] = old_value + self.alpha * (reward + self.gamma * future_value - old_value)

    def get_reward(self, new_pos):
        if new_pos == self.dest:
            return 100  # Large positive reward for reaching the destination
        elif self.grid[new_pos[0]][new_pos[1]] == 'X':  # Obstacle
            return -100  # Large negative reward for hitting an obstacle
        else:
            return -1  # Small negative reward for each step taken
    
    def move(self, bots):
        if self.pos == self.dest:
            return  # Stop if the bot has reached its destination
        
        state = self.get_state()
        action = self.choose_action()
        new_pos = (self.pos[0] + actions[action][0], self.pos[1] + actions[action][1])
        
        # Check bounds and obstacles
        rows, cols = len(self.grid), len(self.grid[0])
        if 0 <= new_pos[0] < rows and 0 <= new_pos[1] < cols and self.grid[new_pos[0]][new_pos[1]] != 'X':
            # Check for collision with other bots
            if not any(bot.pos == new_pos for bot in bots if bot != self):
                reward = self.get_reward(new_pos)
                next_state = new_pos
                # Update Q-table
                self.update_q_value(state, action, reward, next_state)
                
                # Move the bot
                self.pos = new_pos
                self.learned_path.append(self.pos)  # Keep track of the learned path
            else:
                reward = -10  # Penalty for collision
                self.update_q_value(state, action, reward, state)
        else:
            reward = -10  # Penalty for out-of-bounds or obstacle move
            self.update_q_value(state, action, reward, state)

# Read grid and bot positions from the specified file
grid, bot_positions = read_grid_and_bots_from_file('matrix.txt')

# Dynamically initialize Autobots using the parsed positions
bot1 = AutobotQLearning(start=bot_positions['A1'], dest=bot_positions['B1'], grid=grid, name="Bot 1")
bot2 = AutobotQLearning(start=bot_positions['A2'], dest=bot_positions['B2'], grid=grid, name="Bot 2")
bot3 = AutobotQLearning(start=bot_positions['A3'], dest=bot_positions['B3'], grid=grid, name="Bot 3")

# GUI Setup
def create_gui(grid, bots):
    root = tk.Tk()
    root.title("Autobot Warehouse Simulation")

    # Grid canvas
    canvas = tk.Canvas(root, width=500, height=500)
    canvas.grid(row=0, column=0)

    cell_size = 100
    rows, cols = len(grid), len(grid[0])

    # Create grid cells
    cells = {}
    for r in range(rows):
        for c in range(cols):
            x1 = c * cell_size
            y1 = r * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            if grid[r][c] == 'X':
                color = 'red'  # Obstacle
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            else:
                canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                cells[(r, c)] = (x1, y1, x2, y2)

    # Function to animate the autobots
    def animate_bots(bots):
        canvas.delete("bot")  # Clear previous bot positions
        for bot in bots:
            current_pos = bot.pos
            
            # Draw the bot emoji
            if canvas.winfo_exists() and current_pos in cells:
                canvas.create_text((cells[current_pos][0] + 50, cells[current_pos][1] + 50), 
                                   text="🚗" if bot.name == "Bot 1" else "🚙", 
                                   font=("Arial", 24), tags="bot")

            if bot.pos == bot.dest:
                r, c = bot.dest
                canvas.create_text((cells[(r, c)][0] + 50, cells[(r, c)][1] + 50), text="🏁", font=("Arial", 24))  # Destination reached
                print(f"{bot.name} reached its destination!")

        root.update()
        time.sleep(0.5)  # Control animation speed

    # Start the animation
    def update():
        for bot in bots:
            bot.move(bots)
        animate_bots(bots)
        root.after(1000, update)  # Update every second

    update()  # Start the update loop
    root.mainloop()

# Create the GUI and start the animation
create_gui(grid, [bot1, bot2, bot3])
