import tkinter as tk
import time
from collections import deque

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

# Read grid and bot positions from the specified file
grid, bot_positions = read_grid_and_bots_from_file('matrix.txt')

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
    def __init__(self, start, dest, grid, name):
        self.pos = start  # Start position
        self.dest = dest  # Destination position
        self.grid = grid  # Warehouse grid
        self.path = []  # Store the movement path
        self.name = name  # Bot name for identification
        self.reached = False  # Check if the bot has reached its destination
        self.is_paused = False  # Bot can be paused momentarily
        self.waiting = False  # If bot is waiting due to a collision

    def move(self):
        # Get the shortest path using BFS
        self.path = bfs(self.grid, self.pos, self.dest)

    def remaining_distance(self, current_position):
        """Returns the remaining distance to destination from the current position."""
        return abs(self.dest[0] - current_position[0]) + abs(self.dest[1] - current_position[1])

# Dynamically initialize Autobots using the parsed positions
bot1 = Autobot(start=bot_positions['A1'], dest=bot_positions['B1'], grid=grid, name="Bot 1")
bot2 = Autobot(start=bot_positions['A2'], dest=bot_positions['B2'], grid=grid, name="Bot 2")

# Run the movement simulation for both bots
bot1.move()
bot2.move()

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
            elif grid[r][c].startswith('A'):
                color = 'green'  # Start point
            elif grid[r][c].startswith('B'):
                color = 'orange'  # End point
            else:
                color = 'white'  # Empty cells

            cell = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            cells[(r, c)] = cell

    # Function to animate the autobots
    def animate_bots(bots):
        bot_indexes = {bot.name: 0 for bot in bots}  # Track the path index of each bot
        collision_positions = set()  # To track positions with collisions

        while any(bot_indexes[bot.name] < len(bot.path) for bot in bots):
            for bot in bots:
                if bot_indexes[bot.name] < len(bot.path):
                    next_position = bot.path[bot_indexes[bot.name]]

                    # Check if canvas still exists
                    if not canvas.winfo_exists():
                        print("Canvas does not exist anymore, stopping animation.")
                        return

                    # Collision detection
                    is_collision = False
                    for other_bot in bots:
                        if bot != other_bot and bot_indexes[other_bot.name] < len(other_bot.path):
                            if next_position == other_bot.path[bot_indexes[other_bot.name]]:
                                is_collision = True
                                collision_positions.add(next_position)
                                
                                # Ensure canvas and cell exist before updating
                                if next_position in cells and canvas.winfo_exists():
                                    canvas.itemconfig(cells[next_position], fill="gray")  # Mark collision
                                root.update()
                                time.sleep(1)  # Pause on collision

                                # Determine which bot is closer to its destination
                                bot_remaining_distance = bot.remaining_distance(next_position)
                                other_bot_remaining_distance = other_bot.remaining_distance(other_bot.path[bot_indexes[other_bot.name]])

                                # Give priority to the bot closer to the destination
                                if bot_remaining_distance < other_bot_remaining_distance:
                                    other_bot.is_paused = True  # Pause the other bot
                                    bot.is_paused = False  # Allow the current bot to move
                                else:
                                    bot.is_paused = True
                                    other_bot.is_paused = False

                                break

                    if not is_collision:
                        collision_positions.discard(next_position)  # Clear position if no more collision
                        r, c = next_position
                        
                        # Ensure canvas and cell exist before updating
                        if canvas.winfo_exists() and (r, c) in cells:
                            canvas.itemconfig(cells[(r, c)], fill="blue" if bot.name == "Bot 1" else "purple")  # Animate bot
                        bot_indexes[bot.name] += 1

                    # Allow bots to continue moving even after a collision
                    if is_collision:
                        bot_indexes[bot.name] += 1  # Move to the next position regardless of collision

            root.update()
            time.sleep(0.5)  # Control animation speed

            # Check if bots reached their destination
            for bot in bots:
                if bot_indexes[bot.name] == len(bot.path):
                    bot.reached = True
                    if canvas.winfo_exists() and bot.dest in cells:
                        canvas.itemconfig(cells[bot.dest], fill="green")  # Destination reached
                    print(f"{bot.name} reached its destination!")

    # Start the animation
    root.after(1000, lambda: animate_bots(bots))

    root.mainloop()

# Create the GUI and start the animation
create_gui(grid, [bot1, bot2])
