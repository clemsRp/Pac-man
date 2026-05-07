# Pac-Man: Ghosts! More Ghosts!

Welcome to this custom implementation of Pac-Man! This standalone package contains everything you need to play the game without installing Python or any dependencies.

## 🚀 How to Start the Game

Because the game relies on a configuration file, **you must launch it from a terminal**:
1. Open a terminal in the folder containing the `pacman` executable.
2. Run the following command:
   ```bash
   ./pacman config.json
   ```

## 🎮 Controls & Gameplay

- **Goal**: Eat all the small points (pacgums) and big points (super-pacgums) to advance to the next level. Complete all levels to win the game!
- **Move**: Use the `Arrow Keys` or `W, A, S, D`.
- **Shoot (AK-47)**: `Left Mouse Click` (aim with your mouse cursor). *Note: You can only shoot when you eat a Super-Pacgum (large yellow circle) or if you enable the cheat in the Pause Menu.*
- **Pause**: Click the `Pause Game` button in the top right corner.

## ⚙️ In-Game Options & Cheats

While playing, you can pause the game to access the **Cheat Menu**. Here you can toggle:
- **Invincibility**: Ghosts cannot kill you.
- **Remove Collisions**: Walk freely through the maze walls.
- **Level Skip**: Instantly skip to the next level.
- **Freeze Ghosts**: Stop the ghosts from moving entirely.
- **Bonus Lives**: Add extra lives to your counter.
- **AK47 Always Active**: Shoot bullets at any time, even without a Super-Pacgum.
- **Nb Bounces**: Increase the number of times your bullets bounce off the walls!

## 🛠️ Configuration & Modding

You can easily modify the game's rules and levels without touching the code! Open the **`config.json`** file located in this folder using any text editor:

- **`lives`**: Change the starting number of lives.
- **`level_max_time`**: Increase or decrease the time limit for each level.
- **`levels`**: Add or modify the `width` and `height` of the procedural mazes.
- **`points_per_ghost`** / **`points_per_pacgum`**: Change the score rewards.

## 🏆 Leaderboard & Saving Your Score

When your game ends—whether you win by completing all levels, or get a Game Over—a screen will appear prompting you for your name. 
1. Type your **pseudonym** using your keyboard.
2. Press **Enter** to save it.

Your highest scores are automatically saved in **`scores.json`**. If you want to reset the leaderboard, simply open the file and clear out the player list!
