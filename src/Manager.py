
import os
from .Interfaces import Interface
import pyray as pr
from mazegenerator.mazegenerator import MazeGenerator


class GameManager:
    """class that manages the game"""

    def __init__(self, maze: MazeGenerator) -> None:

        self.maze: MazeGenerator = maze
        self.grid: list[list[int]] = self.maze.maze
        self.maze_height: int = len(self.grid)
        self.maze_width: int = len(self.grid[0])
        self.interfaces: dict[str, Interface] = {}
        self.speed = 2.0
        self.assets: dict = {}

    def add_interface(self, name: str, interface: Interface) -> None:
        """This function adds an interface to the manager"""
        self.interfaces[name] = interface

    def start_game(self):
        """function for the logic of this interface"""
        if not self.interfaces.get("gamelogic"):
            raise Exception("No gamelogic interface found")
        state = "gamelogic"
        while not pr.window_should_close():
            pr.clear_background(pr.BLACK)
            cur_interface = self.interfaces[state]
            interface_result = cur_interface.update()
            if interface_result != "":
                state = interface_result

    def create_window(self):
        pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT)
        pr.set_window_min_size(100, 100)
        width = pr.get_screen_width()
        height = pr.get_screen_height()
        pr.init_window(width, height, "Pac-Man")
        pr.set_target_fps(300)

        self.load_assets()

    def load_assets(self):
        """function made to load assets"""
        directions = ["down", "up", "right", "left"]
        paths = {
            "pacman": "assets/pacman-"
        }
        self.assets = {
            "pacman": {}
        }

        for dire in directions:
            self.assets["pacman"][dire] = []

            contenu = os.listdir(paths["pacman"] + dire)
            files = [f for f in contenu if os.path.isfile(
                os.path.join(paths["pacman"] + dire, f)
            )]

            for f in files:
                image = pr.load_image(paths["pacman"] + dire + "/" + f)
                pr.image_resize(image, 64, 64)
                self.assets["pacman"][dire].append(
                    pr.load_texture_from_image(image)
                )

    def close_window(self):
        pr.close_window()
