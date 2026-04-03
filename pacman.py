from src.Display import Display
from src.parser import Parser
from mazegenerator.mazegenerator import MazeGenerator

if __name__ == "__main__":
    try:
        parser = Parser()
        parser.parse_config("test.json")
        maze_gen = MazeGenerator()
        display = Display(maze_gen)
        display.create_window()
        display.render_loop()
        display.close_window()

    except Exception as e:
        print(e)
