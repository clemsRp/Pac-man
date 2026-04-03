from src.Display import Display
from mazegenerator.mazegenerator import MazeGenerator

if __name__ == "__main__":
    maze_gen = MazeGenerator()
    display = Display(maze_gen)
    display.create_window()
    display.render_loop()
    display.close_window()
