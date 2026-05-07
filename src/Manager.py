
import os
import time
from .Interfaces import Interface
from .parser import Parser
import pyray as pr
from typing import Any
from mazegenerator.mazegenerator import MazeGenerator
from .Constants import (
    EXIT, GAME_LOGIC, MAIN_MENU,
    GAME_OVER, GAME_WON, LEVEL_SELECTION
)


class GameManager:
    """
    Class that manages the overall game loop, state, and window.
    """

    def __init__(
        self, maze: MazeGenerator,
        parser: Parser,
        config: dict[str, Any],
        config_file: str
    ) -> None:
        """
        Initialize the GameManager.

        Args:
            maze
                MazeGenerator: The initial maze generator.
            parser
                Parser: The configuration parser instance.
            config
                dict[str, Any]: The parsed configuration dictionary.
            config_file
                str: The path to the configuration file.
        """

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
        self.interfaces: dict[str, Any] = {}
        self.speed = 2.0
        self.state = ""
        self.assets: dict = {}
        self.config: dict[str, Any] = config

    def add_interface(self, name: str, interface: Interface) -> None:
        """
        Add an interface to the manager.

        Args:
            name
                str: The name/state identifier for the interface.
            interface
                Interface: The interface instance to add.

        Returns:
            None: No return value.
        """
        self.interfaces[name] = interface

    def set_state(self, state: str) -> None:
        """
        Set the current state of the game.

        Args:
            state
                str: The state identifier to switch to.

        Returns:
            None: No return value.
        """
        if state not in self.interfaces:
            raise ValueError("State not found")

        self.state = state

    def start_game(self) -> None:
        """
        Start the main game loop, handling state transitions and
        updating the active interface.

        Returns:
            None: No return value.
        """

        while not pr.window_should_close():
            pr.begin_drawing()
            pr.clear_background(pr.BLACK)
            cur_interface = self.interfaces[self.state]
            interface_result = cur_interface.update()
            game_won = interface_result == GAME_WON
            if interface_result == EXIT:
                break

            if self.state == LEVEL_SELECTION and \
                    interface_result == GAME_LOGIC:
                selected_level = self.interfaces[
                    LEVEL_SELECTION].selected_level
                if selected_level:
                    self.interfaces[GAME_LOGIC].current_level = self.config[
                                                "levels"].index(selected_level)
                    seed = self.config["seed"]

                    new_maze = MazeGenerator(
                        (
                            selected_level["width"],
                            selected_level["height"]
                        ),
                        seed=seed
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

            if self.state == GAME_LOGIC and interface_result in [
                    GAME_OVER, GAME_WON]:
                self.parser.parse_config(self.config_file)
                self.interfaces["GameFinish"].score = (
                    self.interfaces[self.state].score
                )
                self.interfaces["GameFinish"].won = game_won
                self.interfaces["GameFinish"].reset(
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

            if interface_result != self.state:
                # this state has 2 possible behaviours
                if interface_result in [GAME_OVER, GAME_WON]:
                    self.set_state("GameFinish")
                else:
                    self.set_state(interface_result)

            pr.end_drawing()

    def create_window(self, width: int, height: int) -> tuple[int, int]:
        """
        Create and initialize the game window using raylib.

        Args:
            width
                int: The requested window width.
            height
                int: The requested window height.

        Returns:
            tuple[int, int]: The actual window width and height created.
        """
        min_width: int = 1200
        min_height: int = 1000
        pr.set_trace_log_level(pr.TraceLogLevel.LOG_ERROR)
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
        """
        Set the size of the game window.

        Args:
            width
                int: The new window width.
            height
                int: The new window height.

        Returns:
            None: No return value.
        """
        pr.set_window_size(width, height)

    def load_assets(self) -> None:
        """
        Load game assets such as textures and images from the filesystem.

        Returns:
            None: No return value.
        """
        paths = {
            "pacman": "assets/pacman",
            "ghosts": "assets/ghosts/",
            "pause_menu": "assets/pause_menu/ghost"
        }
        self.assets = {
            "pacman": [],
            "ghosts": {},
            "pause_menu": []
        }

        for k in range(1, 4):
            self.assets["pause_menu"].append(
                pr.load_texture(f"{paths["pause_menu"]}{k}.png")
            )

        content = os.listdir(paths["pacman"])
        files = [
            f for f in content if os.path.isfile(
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

        content = os.listdir(paths["ghosts"])
        files = [f for f in content if os.path.isfile(
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
        gold_coin = pr.load_image("assets/other/gold_coin.png")
        pr.image_resize(gold_coin,
                        300,
                        300)
        self.assets["skull"] = pr.load_texture_from_image(skull)
        self.assets["gold_coin"] = pr.load_texture_from_image(gold_coin)

    def close_window(self) -> None:
        """
        Close the game window.

        Returns:
            None: No return value.
        """
        pr.close_window()

    def free_assets(self) -> None:
        """
        Free all loaded assets and textures from GPU memory.

        Returns:
            None: No return value.
        """
        for texture in self.assets["pacman"]:
            pr.unload_texture(texture)

        for texture in self.assets["ghosts"].values():
            pr.unload_texture(texture)
