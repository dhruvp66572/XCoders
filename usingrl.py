import tkinter as tk
import time
import numpy as np
import heapq  # For priority queue implementation
from collections import defaultdict

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
    (0, -1): 'left',  # Left
    (0, 1): 'right',  # Right
    (-1, 0): 'up',    # Up
    (1, 0): 'down'    # Down
}

# Pathfinding function using Dijkstra's algorithm
def dijkstra(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    priority_queue = []
    heapq.heappush(priority_queue, (0, start))  # (cost, position)
    came_from = {}
    cost_so_far = defaultdict(lambda: float('inf'))
    cost_so_far[start] = 0

    while priority_queue:
        current_cost, current = heapq.heappop(priority_queue)

        if current == goal:
            break
        
        for action in actions.keys():
            new_pos = (current[0] + action[0], current[1] + action[1])
            
            # Check bounds and obstacles
            if 0 <= new_pos[0] < rows and 0 <= new_pos[1] < cols and grid[new_pos[0]][new_pos[1]] != 'X':
                new_cost = current_cost + 1  # Assuming all moves cost 1
                if new_cost < cost_so_far[new_pos]:
                    cost_so_far[new_pos] = new_cost
                    priority_queue.append((new_cost, new_pos))
                    came_from[new_pos] = current
                    heapq.heapify(priority_queue)  # Reorganize the heap

    # Reconstruct path from start to goal
    path = []
    current = goal
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()  # Reverse the path to get from start to goal

    return path

# Define autobot class
class Autobot:
    def __init__(self, start, dest, grid, name):
        self.pos = start  # Start position
        self.dest = dest  # Destination position
        self.grid = grid  # Warehouse grid
        self.path = self.find_path()  # Find the path using Dijkstra
        self.name = name  # Bot name for identification
        self.index = 0  # Index to track current position in path
        self.waiting = False  # Flag to indicate if the bot is waiting

    def find_path(self):
        return dijkstra(self.grid, self.pos, self.dest)

    def move(self, bots):
        if self.index < len(self.path):
            next_pos = self.path[self.index]
            # Check for collision
            if not any(bot.pos == next_pos for bot in bots if bot != self):
                self.pos = next_pos  # Move to the next position
                self.index += 1
                self.waiting = False  # Not waiting anymore
            else:
                self.waiting = True  # Mark as waiting if the position is occupied
        else:
            self.waiting = False  # If path is complete, not waiting

# Read grid and bot positions from the specified file
grid, bot_positions = read_grid_and_bots_from_file('matrix.txt')

# Dynamically initialize Autobots using the parsed positions
bot1 = Autobot(start=bot_positions['A1'], dest=bot_positions['B1'], grid=grid, name="Bot 1")
bot2 = Autobot(start=bot_positions['A2'], dest=bot_positions['B2'], grid=grid, name="Bot 2")

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
create_gui(grid, [bot1, bot2])
