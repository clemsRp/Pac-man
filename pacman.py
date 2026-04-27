from src.Manager import GameManager

from src.parser import Parser
from mazegenerator.mazegenerator import MazeGenerator
from src.GameLogic import GameLogic
from src.GameOver import GameOver
from src.MainMenu import MainMenu
import pyray as pr
if __name__ == "__main__":

    try:
        parser = Parser()
        parser.parse_config("config.json")

        maze_gen = MazeGenerator((16, 16))

        window_width = 1000
        window_height = 800

        game_manager = GameManager(
            maze_gen,
            parser,
            parser.get_config(),
            "config.json"
        )

        # get the maximum window size
        window_width, window_height = game_manager.create_window(
            window_width, window_height)

        window_width = 1920 - 30
        window_height = 1080 - 60

        game_manager.set_window_size(window_width,
                                     window_height)
        pr.set_window_position(0, 0)

        main_menu = MainMenu(window_width,
                             window_height,
                             parser)
        main_menu.set_assets(game_manager.assets)

        game_logic = GameLogic(
            maze_gen, parser.get_config(),
            window_width, window_height
        )

        game_over = GameOver(
            window_width, window_height,
            parser.get_config(), parser.get_scores()
        )

        game_manager.add_interface("gamelogic",
                                   game_logic)
        game_manager.add_interface("mainmenu",
                                   main_menu)
        game_manager.add_interface("gameover",
                                   game_over)

        game_manager.set_state("mainmenu")

        game_logic.set_assets(game_manager.assets)
        game_over.set_assets(game_manager.assets)

        game_manager.start_game()
        game_manager.free_assets()
        game_manager.close_window()

    except Exception as e:
        print(e)
