*This project has been created as part of the 42 curriculum by crappo and cobussie*

# Pacman - Ghosts! More ghosts!

## Description
This project is a modern recreation of the classic arcade game **Pacman**, developed in Python using the **Raylib** library (via `pyray`). It features procedural maze generation, advanced ghost AI, and unique combat mechanics.

## Features
- **Procedural Maze Generation**: Every level is unique, generated dynamically using a dedicated maze algorithm.
- **Advanced Gameplay**: 
    - Smooth movement and precise collision detection using Circle and Rectangle boxes.
    - **Super-pacgums**: Grants invincibility and the power to freeze or eliminate ghosts.
    - **AK-47 Mechanic**: A special weapon system allowing Pacman to fire projectiles at enemies.
- **Dynamic UI**: Includes a Main Menu, Level Selection, Instructions, and a comprehensive Pause Menu.
- **Cheat Mode**: Integrated GUI within the pause menu to toggle invincibility, skip levels, and modify game physics in real-time.
- **Highscore System**: Persistent leaderboard that tracks and saves player performances.

## Instruction

### Prerequisites
- Python 3.8+
- Raylib dependencies
- `uv` (Python package manager)

## Configuration
The game's behavior and progression are entirely driven by a `config.json` file located in the root directory. This allows for fine-tuning the gameplay balance without recompiling the source code.

### Configuration Structure
The configuration is structured as a JSON object containing the following key parameters:
- **`highscore_filename`**: String defining the name of the file where scores are saved (default: `"scores.json"`).
- **`levels`**: An array of level objects. Each level defines:
  - `name`: The display name in the selection menu.
  - `width` & `height`: Dimensions used by the maze generator.
- **`lives`**: The starting number of lives for Pacman (default: `3`).
- **`points_per_pacgum`**: Score awarded for eating a standard pacgum (default: `10`).
- **`points_per_super_pacgum`**: Score awarded for super-pacgums (default: `50`).
- **`points_per_ghost`**: Score awarded for defeating a ghost (default: `200`).
- **`seed`**: Integer used to initialize the random generator for consistent or randomized mazes.
- **`level_max_time`**: The time limit in seconds to complete a level (default: `160`).

### Faulty Config Handling
To ensure the game is "bulletproof," the `Parser` class implements robust error handling:
1. **File Missing**: If `config.json` is not found, the game loads a set of hardcoded default values.
2. **Invalid JSON**: If the file contains syntax errors, the parser catches the exception and falls back to a safe state.
3. **Missing Keys**: If a specific field (like `lives`) is missing, the code uses a logical default value instead of crashing, ensuring a seamless user experience.

## Highscore System
We implemented a persistent highscore system to increase replayability and competition.

**How it works:**
- **Storage**: Scores are stored in a `scores.json` file.
- **Data Structure**: Each entry contains the player's `pseudo` and the `score`,.
- **Logic**: At the end of a game (Win or Game Over), the current score is compared against the top 10. It is inserted and the list is re-sorted.

**Implementation Choice:**
We chose a JSON format over a simple text file because it allows for easy expansion (e.g., adding level-specific leaderboards) and provides a structured way to handle data using Python's native `json` library, ensuring data integrity.

## Maze Generation
This project integrates the **A-Maze-ing** package to provide a unique challenge every time a level starts.

**Integration:**
- **Dynamic Creation**: Upon entering a new level, the `GameManager` instantiates a `MazeGenerator` with dimensions retrieved from the configuration.
- **Seed Management**: We use `time.time()` as a seed to ensure true randomness for every session.
- **Grid Mapping**: The generator produces a binary/integer matrix where each value represents walls and paths. Our `GameLogic` parses this grid to spawn walls, pacgums, and valid starting positions for both Pacman and the ghosts.

## Implementation Summary
The game is built using **Python 3** and the **Raylib** library (via the `pyray` wrapper).

**Technical Highlights:**
- **Movement**: Uses a "buffered input" system. If a player presses a direction key before reaching an intersection, the intent is stored and executed as soon as the path is clear.
- **Collisions**: Hybrid collision detection using `CircleBox` for the player/ghosts and `RectangleBox` for walls, optimized for grid-based movement.
- **Combat**: An AK-47 mechanic is implemented using a `Bullet` class with trajectory logic and bounce counts, adding a modern twist to the classic gameplay.
- **State Machine**: The `Manager.py` acts as a state controller, handling transitions between menus, the game loop, and the "Won/Lost" screens.

## General Software Architecture
The software follows a modular Object-Oriented Programming (OOP) approach to ensure maintainability.

**Core Modules:**
- **Manager (`Manager.py`)**: The central hub. It initializes the window, loads assets, and switches between different `Interfaces`.
- **Interfaces (`Interfaces.py`, `MainMenu.py`, etc.)**: An abstract base class system where every menu or game screen must implement `update()` and `draw()` methods.
- **Game Logic (`GameLogic.py`)**: The engine of the game. It handles the interaction between entities, score updates, and win/loss conditions.
- **Entities (`Player.py`, `Ghost.py`)**: Independent classes that manage their own state (position, velocity, AI behavior).
- **Physics (`Physics.py`)**: A utility module providing collision primitives and mathematical helpers for movement.

**Relationships:**
The `GameManager` holds instances of `Interface`. When the state is set to `GAME_LOGIC`, the manager passes the maze data to the logic engine, which in turn orchestrates the `Player` and `Ghost` instances.

## Project Management
The development of this project followed an iterative and structured approach to ensure all mandatory features were met within the deadline.

### Development Process
Our team divided the development into several key milestones:
1. **Foundation**: Setting up the `GameManager` and the basic window rendering with Raylib.
2. **Core Mechanics**: Implementing the `Player` movement, **collision system**, and basic grid parsing.
3. **Maze Integration**: Connecting the given `A-Maze-ing` package to generate dynamic levels based on the `config.json`.
4. **AI & Combat**: Developing the Ghost pathfinding (A*) and the AK-47 projectile logic.
5. **UI & Polish**: Finalizing the menu system (Main, Level Selection, Pause) and the Highscore persistent storage.

### Tools and Methodology
- **Version Control**: Git was used for every step, with clear commit messages to track the evolution of the software.
- **Task Tracking**: We maintained a clear list of objectives (TODOs) to manage priorities between the logic engine and the graphical interface.
- **Documentation**: Constant updates to the code comments and this README to ensure the project remains maintainable.

## Resources
This project uses various external assets to enhance the visual and auditory experience. Below is a summary of the resources and their origin.

### Graphical Assets
- **Pacman & Ghosts**: Custom sprites based on the original Namco designs, resized and optimized for Raylib.
- **Weapon (AK-47)**: Sprite sourced from open-source game asset platforms (e.g., [OpenGameArt](https://opengameart.org/)).
- **UI Icons**: 
    - `skull.png`: Used for **game over** and hazard indicators.
    - `gold_coin.png`: Used for **game won** and currency display.
- **Backgrounds & Textures**: Procedural textures generated or loaded via the `assets/` directory.

### Libraries & Packages
- **[Raylib (pyray)](https://pypi.org/project/pyray/)**: Core library used for window management, 2D rendering, and input handling.

>AI was use to understand how used librairies works using short tutos or examples, and also to chose disegn ideas.
