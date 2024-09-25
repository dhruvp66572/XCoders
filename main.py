import tkinter as tk
import time
from collections import deque

# Function to read the grid from a file
def read_grid_from_file(filename):
    with open(filename, 'r') as file:
        grid = [line.strip().split() for line in file]
    return grid

# Read grid from the specified file
grid = read_grid_from_file('matrix.txt')

# Directions: North (Up), East (Right), South (Down), West (Left)
DIRECTIONS = {
    'N': (-1, 0),  # Move up
    'E': (0, 1),   # Move right
    'S': (1, 0),   # Move down
    'W': (0, -1)   # Move left
}

# BFS for shortest path
def bfs(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start, 'N')])  # Queue stores position and direction (facing North initially)
    visited = set([start])  # Track visited cells
    parent_map = {}  # Track the path
    
    while queue:
        (r, c), _ = queue.popleft()
        
        # If goal is reached
        if (r, c) == goal:
            return reconstruct_path(parent_map, start, goal)

        # Explore neighbors in 4 possible directions (N, E, S, W)
        for d in DIRECTIONS:
            nr, nc = r + DIRECTIONS[d][0], c + DIRECTIONS[d][1]
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 'X' and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), d))
                parent_map[(nr, nc)] = (r, c)

    return []

# Reconstruct the path from goal to start
def reconstruct_path(parent_map, start, goal):
    path = []
    current = goal
    
    while current != start:
        prev = parent_map[current]
        path.append(prev)  # Store the movement position
        current = prev
    
    path.reverse()  # Reverse the path to get from start to goal
    return path

# Define autobot class
class Autobot:
    def __init__(self, start, dest, grid):
        self.pos = start  # Start position
        self.dest = dest  # Destination position
        self.grid = grid  # Warehouse grid
        self.path = []  # Store the movement path
        self.is_stopped = False  # Track if the bot is stopped

    def move(self):
        # Get the shortest path using BFS
        self.path = bfs(self.grid, self.pos, self.dest)

# Initialize Autobots with start and destination positions
bot1 = Autobot(start=(0, 0), dest=(0, 4), grid=grid)  # Bot A1 to B1
bot2 = Autobot(start=(4, 0), dest=(4, 4), grid=grid)  # Bot A2 to B2

# Run the movement simulation for both bots
bot1.move()
bot2.move()

# GUI Setup
def create_gui(grid, bot_paths):
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
            elif grid[r][c] == 'A1' or grid[r][c] == 'A2':
                color = 'green'  # Start point
            elif grid[r][c] == 'B1' or grid[r][c] == 'B2':
                color = 'yellow'  # End point
            else:
                color = 'white'  # Empty cells

            cell = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            cells[(r, c)] = cell

    # Function to animate the autobots
    def animate_bots(bot_paths):
        bot1_index = 0
        bot2_index = 0
        
        while bot1_index < len(bot_paths[0]) or bot2_index < len(bot_paths[1]):
            # Check for collisions
            if bot1_index < len(bot_paths[0]) and bot2_index < len(bot_paths[1]):
                if bot_paths[0][bot1_index] == bot_paths[1][bot2_index]:
                    # If they collide, change their colors
                    canvas.itemconfig(cells[bot_paths[0][bot1_index]], fill="gray")  # Change to gray on collision
                    root.update()
                    time.sleep(1)  # Pause for collision

                    # Prioritize the bot with the shorter path to continue
                    if len(bot_paths[0]) < len(bot_paths[1]):
                        bot1_index += 1  # Move bot1
                    else:
                        bot2_index += 1  # Move bot2
                else:
                    # Animate both bots
                    if bot1_index < len(bot_paths[0]):
                        r, c = bot_paths[0][bot1_index]
                        canvas.itemconfig(cells[(r, c)], fill="blue")  # Animate Bot 1
                        bot1_index += 1

                    if bot2_index < len(bot_paths[1]):
                        r, c = bot_paths[1][bot2_index]
                        canvas.itemconfig(cells[(r, c)], fill="purple")  # Animate Bot 2
                        bot2_index += 1
            else:
                # Move remaining bots if one has finished
                if bot1_index < len(bot_paths[0]):
                    r, c = bot_paths[0][bot1_index]
                    canvas.itemconfig(cells[(r, c)], fill="blue")  # Animate Bot 1
                    bot1_index += 1

                if bot2_index < len(bot_paths[1]):
                    r, c = bot_paths[1][bot2_index]
                    canvas.itemconfig(cells[(r, c)], fill="purple")  # Animate Bot 2
                    bot2_index += 1

            # Check if bots reached their destinations
            if bot1_index >= len(bot_paths[0]) and bot2_index >= len(bot_paths[1]):
                break  # Exit if both are done

            # Change the end cell color to green if the destination is reached
            if bot1_index == len(bot_paths[0]) and bot_paths[0][-1] == bot1.dest:
                canvas.itemconfig(cells[bot1.dest], fill="green")  # Change to green for Bot 1
            if bot2_index == len(bot_paths[1]) and bot_paths[1][-1] == bot2.dest:
                canvas.itemconfig(cells[bot2.dest], fill="green")  # Change to green for Bot 2
            
            root.update()
            time.sleep(0.5)  # Control animation speed

    # Animate both bots
    root.after(1000, lambda: animate_bots([bot1.path, bot2.path]))

    root.mainloop()

# Create the GUI and start the animation
create_gui(grid, [bot1.path, bot2.path])
