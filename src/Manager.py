
import os
import time
from .Interfaces import Interface
import pyray as pr
from mazegenerator.mazegenerator import MazeGenerator
from .Constants import EXIT, PACMAN_SPRITE_QUALITY, GAME_LOGIC


class GameManager:
    """class that manages the game"""

    def __init__(self, maze: MazeGenerator) -> None:

        self.maze: MazeGenerator = maze
        self.grid: list[list[int]] = self.maze.maze
        self.maze_height: int = len(self.grid)
        self.maze_width: int = len(self.grid[0])
        self.interfaces: dict[str, Interface] = {}
        self.speed = 2.0
        self.state = ""
        self.assets: dict = {}

    def add_interface(self, name: str, interface: Interface) -> None:
        """This function adds an interface to the manager"""
        self.interfaces[name] = interface

    def set_state(self, state: str) -> None:
        """This function sets the state of the game"""
        if state not in self.interfaces:
            raise ValueError("State not found")

        self.state = state

    def start_game(self):
        """function for the logic of this interface"""

        while not pr.window_should_close():
            pr.begin_drawing()
            pr.clear_background(pr.BLACK)
            cur_interface = self.interfaces[self.state]
            interface_result = cur_interface.update()

            if interface_result == EXIT:
                break

            state = False
            if self.state != GAME_LOGIC and interface_result == GAME_LOGIC:
                state = True

            if interface_result != self.state:
                self.set_state(interface_result)

            if state:
                self.interfaces[self.state].t_start = time.time()

            pr.end_drawing()

    def create_window(self, width: int, height: int) -> tuple[int, int]:
        # pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT)
        pr.set_window_min_size(100, 100)

        pr.init_window(width, height, "Pac-Man")
        pr.gui_load_style("pacman_style.rgs")
        pr.set_target_fps(300)

        monitor = pr.get_current_monitor()

        window_width = pr.get_monitor_width(monitor)
        window_height = pr.get_monitor_height(monitor) - 100

        self.load_assets()
        return window_width, window_height

    def set_window_size(self, width: int, height: int) -> None:
        pr.set_window_size(width, height)

    def load_assets(self):
        """function made to load assets"""
        paths = {
            "pacman": "assets/pacman",
            "ghosts": "assets/ghosts/"
        }
        self.assets = {
            "pacman": [],
            "ghosts": {},
        }

        contenu = os.listdir(paths["pacman"])
        files = [
            f for f in contenu if os.path.isfile(
                os.path.join(paths["pacman"], f)
            )
        ]
        files.sort(
            key=lambda x: int(x.split('.')[0])
            if x.split('.')[0].isdigit() else x
        )

        for f in files:
            image = pr.load_image(os.path.join(paths["pacman"], f))
            # if img is not 512 px:

            # pr.image_resize(image,
            #                 PACMAN_SPRITE_QUALITY,
            #                 PACMAN_SPRITE_QUALITY)
            self.assets["pacman"].append(
                pr.load_texture_from_image(image)
            )

        contenu = os.listdir(paths["ghosts"])
        files = [f for f in contenu if os.path.isfile(
            os.path.join(paths["ghosts"], f)
        )]

        for f in files:
            image = pr.load_image(paths["ghosts"] + f)
            pr.image_resize(image,
                            64,
                            64)
            self.assets["ghosts"][f[:-4]] = pr.load_texture_from_image(image)

        ak47 = pr.load_image("assets/other/ak47.png")
        self.assets["ak47"] = pr.load_texture_from_image(ak47)
        skull = pr.load_image("assets/other/skull.png")
        pr.image_resize(skull,
                        300,
                        300)
        self.assets["skull"] = pr.load_texture_from_image(skull)

    def close_window(self):
        pr.close_window()

    def free_assets(self):
        """function made to free assets"""
        for texture in self.assets["pacman"]:
            pr.unload_texture(texture)

        for texture in self.assets["ghosts"].values():
            pr.unload_texture(texture)
