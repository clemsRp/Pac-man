
import os
import time
from .Interfaces import Interface
from .parser import Parser
import pyray as pr
from typing import Any
from mazegenerator.mazegenerator import MazeGenerator
from .Constants import (
    EXIT, GAME_LOGIC, MAIN_MENU,
    GAME_OVER, LEVEL_SELECTION
)


class GameManager:
    """class that manages the game"""

    def __init__(
                self, maze: MazeGenerator,
                parser: Parser,
                config: dict[str, Any],
                config_file: str
            ) -> None:

        self.maze: MazeGenerator = maze
        self.parser: Parser = parser
        self.config_file: str = config_file
        self.window_width: int = 0
        self.window_height: int = 0
        self.scale_x: int = 0
        self.scale_y: int = 0
        self.grid: list[list[int]] = self.maze.maze
        self.maze_height: int = len(self.grid)
        self.maze_width: int = len(self.grid[0])
        self.interfaces: dict[str, Interface] = {}
        self.speed = 2.0
        self.state = ""
        self.assets: dict = {}
        self.config: dict[str, Any] = config

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

            if self.state == LEVEL_SELECTION and \
                    interface_result == GAME_LOGIC:
                selected_level = self.interfaces[
                                                LEVEL_SELECTION].selected_level
                if selected_level:
                    new_maze = MazeGenerator(
                        (
                            selected_level["width"],
                            selected_level["height"]
                        )
                    )
                    self.interfaces[GAME_LOGIC].reset(new_maze)

            if self.state != GAME_LOGIC and interface_result == GAME_LOGIC:
                self.interfaces[interface_result].life = self.config["lives"]
                self.interfaces[interface_result].t_start = time.time()
                self.interfaces[interface_result].score = 0
                self.interfaces[interface_result].points = (
                    self.interfaces[interface_result].create_points()
                )
                self.interfaces[interface_result].game_duration = 0.0
                self.interfaces[interface_result].level_start = 0.0

            if self.state != GAME_OVER and interface_result == GAME_OVER:
                self.parser.parse_config(self.config_file)
                self.interfaces[interface_result].score = (
                    self.interfaces[self.state].score
                )
                self.interfaces[interface_result].reset(
                    self.parser.get_config(),
                    self.parser.get_scores()
                )

            if self.state != MAIN_MENU and interface_result == MAIN_MENU:
                self.interfaces[interface_result].next_state = MAIN_MENU
                self.parser.parse_config(self.config_file)
                self.interfaces[interface_result].compute_scores()
                self.interfaces[interface_result].scores = (
                    self.parser.get_scores().get("players", [])
                )

            if self.state != MAIN_MENU and interface_result == MAIN_MENU:
                self.parser.parse_config(self.config_file)
                self.interfaces[interface_result].scores = (
                    self.parser.get_scores().get("players", [])
                )

            if self.state != GAME_OVER and interface_result == GAME_OVER:
                self.interfaces["gameover"].state = GAME_OVER
            if interface_result != self.state:
                self.set_state(interface_result)

            pr.end_drawing()

    def create_window(self, width: int, height: int) -> tuple[int, int]:
        # pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT)
        min_width: int = 1200
        min_height: int = 1000

        pr.set_window_min_size(min_width, min_height)

        if width < min_width:
            width = min_width
        if height < min_height:
            height = min_height

        pr.init_window(width, height, "Pac-Man")
        pr.gui_load_style("pacman_style.rgs")
        pr.set_target_fps(300)

        monitor = pr.get_current_monitor()

        self.window_width = pr.get_monitor_width(monitor)
        self.window_height = pr.get_monitor_height(monitor) - 100
        self.scale_x = int(self.window_width / self.maze_width)
        self.scale_y = int(self.window_height / self.maze_height)
        self.scale_x = min([self.scale_x, self.scale_y])
        self.scale_x -= self.scale_x % 2
        self.scale_y = self.scale_x

        self.load_assets()
        return self.window_width, self.window_height

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
                            int(self.scale_x),
                            int(self.scale_y))
            self.assets["ghosts"][f[:-4]] = pr.load_texture_from_image(image)

        ak47 = pr.load_image("assets/ak47/ak47.png")
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
