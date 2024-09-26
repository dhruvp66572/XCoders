from collections import deque
from datetime import datetime
import heapq
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# Define colors for each bot //DP
BOT_COLORS = {
    "Bot 1 Start": "blue",
    "Bot 2 Start": "green",
    "Bot 3 Start": "orange",
    "Bot 4 Start": "purple"
}

# Global variables
grid = []  # The grid representation
bot_data = {}  # Store bot data with start and end points
blocked_positions = {}  # Track positions occupied by bots

# Track commands and time
command_count = {}
time_taken = {}
impossible_scenario_flag = False

# Movement Commands for Bots
def forward(r, c, direction):
    if direction == 'up':
        return r - 1, c
    elif direction == 'down':
        return r + 1, c
    elif direction == 'left':
        return r, c - 1
    else:  # right
        return r, c + 1

def reverse(r, c, direction):
    if direction == 'up':
        return r + 1, c
    elif direction == 'down':
        return r - 1, c
    elif direction == 'left':
        return r, c + 1
    else:  # right
        return r, c - 1

def turn_left(direction):
    directions = ['up', 'left', 'down', 'right']
    return directions[(directions.index(direction) + 1) % 4]

def turn_right(direction):
    directions = ['up', 'right', 'down', 'left']
    return directions[(directions.index(direction) - 1) % 4]

# A* Algorithm to Find the Shortest Path
def heuristic(a, b):
    # Manhattan distance as the heuristic function
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(grid, start, end):
    rows, cols = len(grid), len(grid[0])
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end:
            return reconstruct_path(came_from, current, start)

        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = current[0] + dr, current[1] + dc
            neighbor = (nr, nc)

            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 'X':
                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # No path found

# Reconstruct the Path from A* Algorithm
def reconstruct_path(came_from, current, start):
    steps = []
    while current != start:
        steps.append(current)
        current = came_from[current]
    steps.reverse()
    return steps
# Function to log the movement command based on the direction change
def get_command(prev_pos, curr_pos):
    prev_r, prev_c = prev_pos
    curr_r, curr_c = curr_pos

    if curr_r < prev_r:
        return "Forward (up)"
    elif curr_r > prev_r:
        return "Forward (down)"
    elif curr_c < prev_c:
        return "Forward (left)"
    elif curr_c > prev_c:
        return "Forward (right)"
    else:
        return "Wait"

# Function to Schedule Bots in Parallel and Avoid Collisions
def schedule_bots(bot_paths, buttons, step_delay, log_text):
    max_steps = max(len(steps) for steps in bot_paths.values())
    total_commands = 0  # To track the total number of commands for all bots
    impossible_case_detected = False  # Track if an impossible case is detected

    for step_idx in range(max_steps):
        next_positions = {}
        for bot_id, path in bot_paths.items():
            if step_idx < len(path):
                r, c = path[step_idx]
                
                # Determine the previous position (for command logging)
                if step_idx > 0:
                    prev_r, prev_c = path[step_idx - 1]
                    command = get_command((prev_r, prev_c), (r, c))  # Get the movement command
                else:
                    command = "Starting Position"

                # Log the movement command along with the coordinates
                log_text.insert(tk.END, f"{bot_id} moving to ({r}, {c}) - Command: {command}\n")

                if (r, c) in next_positions:
                    # Collision detected, choose one bot to wait or reverse
                    if command_count[bot_id] % 2 == 0:
                        log_text.insert(tk.END, f"{bot_id} is waiting to avoid collision at ({r}, {c}).\n")
                        bot_paths[bot_id].insert(step_idx, path[step_idx - 1])  # Bot waits
                    else:
                        # Reverse and recalculate the path using A*
                        log_text.insert(tk.END, f"{bot_id} is reversing and recalculating path from ({r}, {c}).\n")
                        r, c = reverse(r, c, 'up')  # Example reverse, update this based on direction
                        new_path = a_star(grid, (r, c), bot_data[bot_id]['end'])
                        if new_path:
                            bot_paths[bot_id] = new_path
                            log_text.insert(tk.END, f"{bot_id} found new path starting from ({r}, {c}).\n")
                        else:
                            log_text.insert(tk.END, f"{bot_id} has encountered an impossible scenario at ({r}, {c}).\n")
                            impossible_case_detected = True
                            break  # Exit as soon as impossible scenario is detected
                else:
                    next_positions[(r, c)] = bot_id
                    # Move the bot to the next step
                    buttons[r][c].config(bg=BOT_COLORS.get(bot_id, "black"))
                    blocked_positions[(r, c)] = bot_id
                    root.update()
                    command_count[bot_id] += 1
                    total_commands += 1
                    time_taken[bot_id] += 1
                    log_text.insert(tk.END, f"{bot_id} successfully moved to ({r}, {c}).\n")

        root.after(step_delay)  # Introduce delay for visual purposes
        root.update()

        # Stop if an impossible case is detected
        if impossible_case_detected:
            break

    # Display total time and steps for each bot
    for bot_id in bot_paths.keys():
        total_steps = command_count[bot_id]
        total_time = time_taken[bot_id]
        log_text.insert(tk.END, f"{bot_id} reached destination in {total_steps} steps and took {total_time} seconds.\n")

    # Calculate average commands
    num_bots = len(bot_paths)
    avg_commands = total_commands / num_bots if num_bots > 0 else 0
    max_commands = max(command_count.values(), default=0)

    log_text.insert(tk.END, f"\nAverage commands: {avg_commands:.2f}\n")
    log_text.insert(tk.END, f"Maximum commands: {max_commands}\n")

    if impossible_case_detected:
        log_text.insert(tk.END, f"Impossible scenario detected after {total_commands} commands.\n")

# Start pathfinding for all bots
def start_pathfinding(bot_starts, bot_destinations, buttons, blocked_positions, log_text):
    step_delay = 1000  # Delay in milliseconds
    bot_paths = {}

    # Initialize command count and time taken for each bot
    for bot_id in bot_starts:
        command_count[bot_id] = 0  # Initialize command count for each bot
        time_taken[bot_id] = 0  # Initialize time taken for each bot

    # Calculate the shortest path for each bot using A* algorithm
    for bot_id, start in bot_starts.items():
        end = bot_destinations.get(bot_id)
        if end:
            bot_data[bot_id] = {'start': start, 'end': end}
            path = a_star(grid, start, end)
            if path:
                bot_paths[bot_id] = path
                log_text.insert(tk.END, f"{bot_id} path calculated.\n")
            else:
                log_text.insert(tk.END, f"Path not found for {bot_id}\n")

    # Schedule and move the bots in parallel with dynamic collision handling
    schedule_bots(bot_paths, buttons, step_delay, log_text)

# The rest of the code remains unchanged...

# Start pathfinding for all bots
def start_pathfinding(bot_starts, bot_destinations, buttons, blocked_positions, log_text):
    step_delay = 1000  # Delay in milliseconds
    bot_paths = {}

    # Initialize command count and time taken for each bot
    for bot_id in bot_starts:
        command_count[bot_id] = 0  # Initialize command count for each bot
        time_taken[bot_id] = 0  # Initialize time taken for each bot

    # Calculate the shortest path for each bot using A* algorithm
    for bot_id, start in bot_starts.items():
        end = bot_destinations.get(bot_id)
        if end:
            bot_data[bot_id] = {'start': start, 'end': end}
            path = a_star(grid, start, end)
            if path:
                bot_paths[bot_id] = path
                log_text.insert(tk.END, f"{bot_id} path calculated.\n")
            else:
                log_text.insert(tk.END, f"Path not found for {bot_id}\n")

    # Schedule and move the bots in parallel with dynamic collision handling
    schedule_bots(bot_paths, buttons, step_delay, log_text)

# Reset selected cell
def reset_selected_cell():
    selected_bot = combobox.get()
    if selected_bot and selected_bot != "Select Bot":
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c] == selected_bot or grid[r][c] == 'B':
                    grid[r][c] = '.'
                    buttons[r][c].config(text=".", bg="white", fg="black")
        combobox.set("Select Bot")
    else:
        messagebox.showwarning("Warning", "Please select a bot to reset the cell.")

# Clear entire grid
def clear_grid():
    global bot_data, blocked_positions

    # Reset grid
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            grid[r][c] = '.'
            buttons[r][c].config(text=".", bg="white", fg="black")

    # Clear stored data
    bot_data.clear()
    blocked_positions.clear()
    command_count.clear()
    time_taken.clear()

    # Clear combobox
    combobox.set("Select Bot")
    combobox['values'] = []

# Create the Grid and Set Up the GUI
def create_grid():
    global grid, buttons  # Declare grid and buttons as global
    rows = int(simpledialog.askstring("Input", "Enter number of rows"))
    cols = int(simpledialog.askstring("Input", "Enter number of columns"))
    grid = [['.' for _ in range(cols)] for _ in range(rows)]  # Initialize global grid

    bot_starts = {}
    bot_destinations = {}

    def update_combobox():
        combobox['values'] = list(bot_starts.keys())

    def set_cell(event, mode):
        row, col = event.widget.grid_info()["row"], event.widget.grid_info()["column"]
        selected_bot = combobox.get()

        if mode == 'start':
            bot_id = f"Bot {len(bot_starts) + 1} Start"
            grid[row][col] = bot_id
            buttons[row][col].config(text=bot_id, bg=BOT_COLORS.get(bot_id, "blue"), fg="white")
            bot_starts[bot_id] = (row, col)
            update_combobox()
        elif mode == 'end' and selected_bot != "Select Bot":
            if selected_bot in bot_starts:
                grid[row][col] = 'B'
                buttons[row][col].config(text='B', bg="red", fg="white")
                bot_destinations[selected_bot] = (row, col)
            else:
                messagebox.showwarning("Warning", "Please set a start point for this bot first.")
        elif mode == 'obstacle':
            grid[row][col] = 'X'
            buttons[row][col].config(text='X', bg="black", fg="white")
        else:
            grid[row][col] = '.'
            buttons[row][col].config(text='.', bg="white", fg="black")

    global root
    root = tk.Tk()
    root.title("Warehouse Autobot Pathfinding")

    grid_frame = tk.Frame(root)
    grid_frame.grid(row=0, column=0)

    buttons = [[None for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            button = tk.Button(grid_frame, text=".", width=5, height=2, font=("Helvetica", 12), bg="white")
            button.grid(row=r, column=c, padx=2, pady=2)
            button.bind('<Button-1>', lambda event, m='start': set_cell(event, mode_var.get()))
            buttons[r][c] = button

    log_frame = tk.Frame(root)
    log_frame.grid(row=0, column=1, padx=20, pady=20)

    log_label = tk.Label(log_frame, text="Command Log", font=("Helvetica", 12))
    log_label.pack()

    log_text = tk.Text(log_frame, width=40, height=20)
    log_text.pack()

    mode_var = tk.StringVar(value='start')
    modes = ['start', 'end', 'obstacle']

    mode_frame = tk.Frame(root)
    mode_frame.grid(row=1, column=0, columnspan=cols)

    for mode in modes:
        radio = tk.Radiobutton(mode_frame, text=mode.capitalize(), variable=mode_var, value=mode, font=("Helvetica", 10))
        radio.pack(side=tk.LEFT)

    global combobox
    combobox = ttk.Combobox(root, state="readonly")
    combobox.set("Select Bot")
    combobox.grid(row=1, column=0)

    start_button = tk.Button(root, text="Start", command=lambda: start_pathfinding(bot_starts, bot_destinations, buttons, blocked_positions, log_text))
    start_button.grid(row=2, column=0, padx=10, pady=10)

    reset_button = tk.Button(root, text="Reset Cell", command=reset_selected_cell)
    reset_button.grid(row=3, column=0, padx=10, pady=10)

    clear_button = tk.Button(root, text="Clear Grid", command=clear_grid)
    clear_button.grid(row=4, column=0, padx=10, pady=10)

    root.mainloop()

# Main
if __name__ == "__main__":
    create_grid()
