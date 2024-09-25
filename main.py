import tkinter as tk
import time
from collections import deque

# Grid Layout with Start (A1, B2), End (B1, B2), and Obstacles ('X')
grid = [
    ['A1', '.', '.', 'X', 'B1'],
    ['.',  'X', '.', '.', '.'],
    ['.',  '.', 'X', '.', '.'],
    ['.',  '.', '.', '.', '.'],
    ['B2', 'X', '.', '.', 'B2']
]

# Directions: North (Up), East (Right), South (Down), West (Left)
DIRECTIONS = {
    'N': (-1, 0),  # Move up
    'E': (0, 1),   # Move right
    'S': (1, 0),   # Move down
    'W': (0, -1)   # Move left
}

# Command mappings based on direction change
commands = {
    ('N', 'N'): 'Forward()',
    ('N', 'E'): 'Right(), Forward()',
    ('N', 'S'): 'Right(), Right(), Forward()',
    ('N', 'W'): 'Left(), Forward()',
    ('E', 'N'): 'Left(), Forward()',
    ('E', 'E'): 'Forward()',
    ('E', 'S'): 'Right(), Forward()',
    ('E', 'W'): 'Right(), Right(), Forward()',
    ('S', 'N'): 'Right(), Right(), Forward()',
    ('S', 'E'): 'Left(), Forward()',
    ('S', 'S'): 'Forward()',
    ('S', 'W'): 'Right(), Forward()',
    ('W', 'N'): 'Right(), Forward()',
    ('W', 'E'): 'Right(), Right(), Forward()',
    ('W', 'S'): 'Left(), Forward()',
    ('W', 'W'): 'Forward()'
}

# BFS for shortest path
def bfs(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start, 'N')])  # Queue stores position and direction (facing North initially)
    visited = set([start])  # Track visited cells
    parent_map = {}  # Track the path
    direction_map = {start: 'N'}  # Start facing North
    
    while queue:
        (r, c), direction = queue.popleft()
        
        # If goal is reached
        if (r, c) == goal:
            return reconstruct_path(parent_map, direction_map, start, goal)

        # Explore neighbors in 4 possible directions (N, E, S, W)
        for d in DIRECTIONS:
            nr, nc = r + DIRECTIONS[d][0], c + DIRECTIONS[d][1]
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 'X' and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), d))
                parent_map[(nr, nc)] = (r, c)
                direction_map[(nr, nc)] = d

    return []

# Reconstruct the path from goal to start
def reconstruct_path(parent_map, direction_map, start, goal):
    path = []
    current = goal
    direction = direction_map[goal]
    
    while current != start:
        prev = parent_map[current]
        prev_direction = direction_map[prev]
        path.append((prev, direction))  # Store the movement command and position
        current = prev
        direction = prev_direction
    
    path.reverse()  # Reverse the path to get from start to goal
    return path

# Define autobot class
class Autobot:
    def __init__(self, start, dest, grid):
        self.pos = start  # Start position
        self.dest = dest  # Destination position
        self.grid = grid  # Warehouse grid
        self.path = []  # Store the movement path

    def move(self):
        # Get the shortest path using BFS
        self.path = bfs(self.grid, self.pos, self.dest)

# Initialize Autobots with start and destination positions
bot1 = Autobot(start=(0, 0), dest=(0, 4), grid=grid)  # Bot A1 to top-right B1
bot2 = Autobot(start=(4, 0), dest=(4, 4), grid=grid)  # Bot B2 to bottom-right B2

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
            elif grid[r][c] == 'A1' or grid[r][c] == 'B2':
                color = 'green'  # Start point
            elif grid[r][c] == 'B1' or grid[r][c] == 'B2':
                color = 'yellow'  # End point
            else:
                color = 'white'  # Empty cells

            cell = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            cells[(r, c)] = cell

    # Function to animate the autobots
    def animate_bot(bot_path, color):
        for (pos, _) in bot_path:
            time.sleep(0.5)
            r, c = pos
            canvas.itemconfig(cells[(r, c)], fill=color)
            root.update_idletasks()
    
    # Animate Bot1
    root.after(1000, lambda: animate_bot(bot1.path, "blue"))
    # Animate Bot2
    root.after(2000, lambda: animate_bot(bot2.path, "blue"))

    root.mainloop()

# Create the GUI and start the animation
create_gui(grid, [bot1.path, bot2.path])
