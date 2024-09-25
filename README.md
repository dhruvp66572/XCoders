# Autobot Warehouse Simulation using Q-Learning

## Overview

This project simulates a warehouse environment where multiple autobots navigate through grids, avoiding obstacles and reaching their designated destinations. The autobots use Q-Learning to learn optimal navigation strategies based on their environment.

## Key Components

### 1. **AutobotQLearning Class**
This class defines the behavior of an autobot using Q-Learning. The main features include:
- **State**: Current position of the bot.
- **Action**: Defined as `Forward`, `Reverse`, `Left`, `Right`, and `Wait`.
- **Q-Table**: Stores Q-values for different states and actions.
- **Learning Parameters**:
  - `alpha`: Learning rate.
  - `gamma`: Discount factor.
  - `epsilon`: Exploration rate.

#### Methods:
- `choose_action()`: Selects an action based on exploration/exploitation.
- `update_q_value()`: Updates the Q-value based on the reward received after taking an action.
- `get_reward()`: Calculates the reward for moving to a new position.
- `move()`: Executes the bot's move, updating its state and Q-values accordingly.
- `get_performance_metrics()`: Provides performance metrics of the bot, including time taken, steps, and commands issued.

### 2. **Grid Generation**
- **`generate_random_grid(rows, cols, obstacle_count)`**: Generates a random grid of size `rows x cols` with `obstacle_count` obstacles marked as `'X'`.
- **`read_multiple_grids(file_list)`**: Reads grids and autobot positions from text files. Each file contains grid data, where:
  - `'A'`: Start position of a bot.
  - `'B'`: Destination of a bot.

### 3. **Bot Commands and Actions**
Commands are defined using integers corresponding to specific moves:
- `0`: Forward
- `1`: Reverse
- `2`: Left
- `3`: Right
- `4`: Wait

The bot chooses an action based on the Q-Learning policy and updates its Q-Table accordingly.

### 4. **GUI Implementation**
- **Tkinter** is used to create a graphical user interface to display the grid and visualize bot movements.
- The canvas is dynamically updated with the position of each bot and their learned path.
- Bots move autonomously and avoid collisions based on the Q-learning model.

### 5. **User Interaction**
The user can either:
- **Load grid files**: Select pre-defined grid files using the file dialog.
- **Generate new grids**: Enter parameters for generating a random grid and define bot start and destination positions.

### 6. **File Operations**
- The user can select multiple grid files, which will be processed and displayed in the GUI.
- Grids are loaded from text files and displayed with obstacles and autobot positions.

## How to Use

1. Run the Python script.
2. Choose whether to load grids from files or generate new ones.
3. If loading from files, select the text files containing grid data.
4. If generating new grids, specify the grid dimensions, number of obstacles, and autobot start/destination positions.
5. Watch the simulation in the GUI, with real-time autobot navigation using Q-learning.

## Dependencies

- Python 3.10+
- Tkinter: For GUI handling.
- Numpy: For numerical operations.
- Collections: For defaultdict used in the Q-table.

Install the required dependencies using:
```bash
pip install numpy
