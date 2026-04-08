from src.Manager import GameManager

from src.parser import Parser
from mazegenerator.mazegenerator import MazeGenerator
from src.GameLogic import GameLogic
from src.MainMenu import MainMenu
if __name__ == "__main__":
    try:
        parser = Parser()
        parser.parse_config("test.json")
        maze_gen = MazeGenerator((16, 16))

        game_manager = GameManager(maze_gen)
        game_manager.create_window()

        main_menu = MainMenu(1500, 1500)
        game_logic = GameLogic(maze_gen, 1500, 1500)

        game_manager.add_interface("gamelogic",
                                   game_logic)
        game_manager.add_interface("mainmenu",
                                   main_menu)
        game_manager.set_state("mainmenu")

        game_logic.set_assets(game_manager.assets)
        game_manager.start_game()
        game_manager.free_assets()
        game_manager.close_window()

    except Exception as e:
        print(e)
