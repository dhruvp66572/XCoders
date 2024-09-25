import tkinter as tk
import time
import heapq
from tkinter import messagebox

# Dijkstra Algorithm for Pathfinding with real-time simulation
def dijkstra(grid, start, end, buttons):
    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    distances = [[float('inf')] * cols for _ in range(rows)]
    distances[start[0]][start[1]] = 0
    pq = [(0, start)]  # Priority queue, starting with the start node
    path = {}  # To store the path
    
    while pq:
        curr_dist, (r, c) = heapq.heappop(pq)
        
        # Highlight the current cell
        buttons[r][c].config(bg="yellow")
        root.update()
        time.sleep(0.2)
        
        if (r, c) == end:
            return trace_path(path, end, start, buttons)  # Return the final path
        
        if visited[r][c]:
            continue
        visited[r][c] = True
        
        # Explore neighbors (up, down, left, right)
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] != 'X':
                new_dist = curr_dist + 1
                if new_dist < distances[nr][nc]:
                    distances[nr][nc] = new_dist
                    heapq.heappush(pq, (new_dist, (nr, nc)))
                    path[(nr, nc)] = (r, c)  # Keep track of the path
    
    return None  # Return None if no path is found

# Function to trace and visualize the final path
def trace_path(path, end, start, buttons):
    current = end
    while current != start:
        r, c = current
        buttons[r][c].config(bg="green")  # Mark the path in green
        root.update()
        time.sleep(0.2)
        current = path[current]
    buttons[start[0]][start[1]].config(bg="blue")  # Mark the start in blue
    buttons[end[0]][end[1]].config(bg="red")  # Mark the end in red
    messagebox.showinfo("Success", "Path found!")
    return True

# GUI Setup using Tkinter with a beautiful design
def create_grid(rows, cols):
    grid = [['.' for _ in range(cols)] for _ in range(rows)]
    
    def set_cell(event, mode):
        row, col = event.widget.grid_info()["row"], event.widget.grid_info()["column"]
        if mode == 'start':
            grid[row][col] = 'A'
            buttons[row][col].config(text='A', bg="blue", fg="white")
        elif mode == 'end':
            grid[row][col] = 'B'
            buttons[row][col].config(text='B', bg="red", fg="white")
        elif mode == 'obstacle':
            grid[row][col] = 'X'
            buttons[row][col].config(text='X', bg="black", fg="white")
        else:
            grid[row][col] = '.'
            buttons[row][col].config(text='.', bg="white", fg="black")

    global root
    root = tk.Tk()
    root.title("Warehouse Autobot Pathfinding")

    buttons = [[None for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            button = tk.Button(root, text=".", width=5, height=2, font=("Helvetica", 12), bg="white")
            button.grid(row=r, column=c, padx=2, pady=2)
            button.bind('<Button-1>', lambda event, m='start': set_cell(event, mode_var.get()))
            buttons[r][c] = button

    # Radio buttons for selecting mode
    mode_var = tk.StringVar(value="start")
    modes = ["start", "end", "obstacle", "clear"]
    mode_frame = tk.Frame(root)
    mode_frame.grid(row=rows, column=0, columnspan=cols)
    for mode in modes:
        radio = tk.Radiobutton(mode_frame, text=mode.capitalize(), variable=mode_var, value=mode, font=("Helvetica", 10))
        radio.pack(side=tk.LEFT, padx=5, pady=5)

    # Start button for running the algorithm
    start_button = tk.Button(root, text="Run Algorithm", command=lambda: run_algorithm(grid, buttons), font=("Helvetica", 12), bg="green", fg="white")
    start_button.grid(row=rows+1, column=0, columnspan=cols, pady=10)

    root.mainloop()

# Function to run the algorithm after grid setup
def run_algorithm(grid, buttons):
    start = None
    end = None
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 'A':
                start = (r, c)
            if grid[r][c] == 'B':
                end = (r, c)

    if start and end:
        result = dijkstra(grid, start, end, buttons)
        if result is None:
            messagebox.showerror("Error", "No path found!")
    else:
        messagebox.showwarning("Warning", "Please set both start and end points.")

# Example usage
create_grid(5, 5)
