import pyray as pr
import time
import numpy as np
from math import atan2
from typing import Any
from mazegenerator.mazegenerator import MazeGenerator
from .Physics import CollisionBox, CircleBox, RectangleBox, Bullet
from .PauseMenu import PauseMenu
from .Interfaces import Button
from .Player import Player
from .Ghost import Ghost
from .Interfaces import Interface
from .Constants import (
    NORTH,
    EAST,
    SOUTH,
    WEST,
    SPEED,
    GAME_LOGIC,
    BULLET_SPEED,
    BULLET_RADIUS,
    BULLET_FIRE_RATE,
    GAME_FINISH,
    AK47_ALWAYS_ACTIVE,
    INVINCIBILITY,
    NB_BOUNCES,
    REMOVE_COLLISIONS,
    FREEZE_GHOSTS,
    BONUS_LIVES,
    PACMAN_LIGHT_COLOR_R,
    PACMAN_LIGHT_COLOR_G,
    PACMAN_LIGHT_COLOR_B,
    PACMAN_LIGHT_RADIUS,
    LIGHT_FADE_TIME,
    PACMAN_SPRITE_QUALITY,
    AK47_SPRITE_QUALITY,
    SUPER_PACGUM_TIME,
    GHOST_RETURN_SPAWN_TIME,
    AK47_FREEZE_TIME,
    GHOST_SPRITE_QUALITY
)

WALL_WIDTH = 3
WALL_COLOR = pr.BLUE


CENTER_X = 0
CENTER_Y = 0


class GameLogic(Interface):
    def __init__(
        self,
        maze: MazeGenerator, config: dict[str, Any],
        screen_width: int, screen_height: int
    ):
        global CENTER_X, CENTER_Y
        super().__init__()
        self.maze: MazeGenerator = maze
        self.grid: list[list[int]] = self.maze.maze
        self.maze_height: int = len(self.grid)
        self.maze_width: int = len(self.grid[0])
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height

        self.scale_x: float = self.screen_width / self.maze_width
        self.scale_y: float = self.screen_height / self.maze_height
        self.scale_x = min([self.scale_x, self.scale_y])
        self.scale_x -= self.scale_x % 2
        self.scale_y = self.scale_x

        buttons_width = 300
        buttons_height = 50
        window_offset = 40

        self.game_duration: float = 0.0
        self.level_start: float = 0.0
        self.update_game_duration: bool = False
        self.nb_wait: int = 0

        pause_button_x = int(self.screen_width - buttons_width - window_offset)
        pause_button_y = int(window_offset)
        pause_button = Button(pause_button_x,
                              pause_button_y,
                              buttons_width,
                              buttons_height,
                              "Pause Game",
                              color=pr.GRAY,
                              triggered_function=self.pause_action)
        self.add_button(pause_button)
        self.pause_menu = PauseMenu(self.screen_width, self.screen_height)
        self.paused = False
        self.total_paused_time = 0.0
        self.pause_started_at: float | None = None

        self.score = 0
        self.life = int(config["lives"])

        self.t_start = 0.0

        CENTER_X = int(
            (
                screen_width - self.scale_x * self.maze_width
            ) / 2
        )
        CENTER_Y = int(
            (
                screen_height - self.scale_y * self.maze_height
            ) / 2
        )

        CENTER_X -= CENTER_X % 10
        CENTER_Y -= CENTER_Y % 10

        self.collision_boxs: dict[str, list[
            list[
                list[
                    RectangleBox]
            ]]] = self.create_collision_boxs()

        self.bullets: list[Bullet] = []
        self.assets: dict = {}
        SIZE_PACMAN = self.update_radius()
        hitbox_w = self.scale_x - 2 * WALL_WIDTH
        hitbox_h = self.scale_y - 2 * WALL_WIDTH
        is_pair = (self.maze_width % 2 + 1) % 2
        self.player = Player(
            int(
                (0.5 + self.maze_width // 2 - is_pair) * self.scale_x
            ),
            int(
                (0.5 + self.maze_height // 2) * self.scale_y
            ),
            SIZE_PACMAN,
            hitbox_w,
            hitbox_h
        )

        self.ghosts: list[Ghost] = []
        self.remove_collisions_active = False
        self.super_pacgum_state = False
        self.last_super_pacgum = 0.0
        self.last_bullet = 0.0
        self._init_raytracing()
        self.points: list[CircleBox] = self.create_points()
        self.super_pacgums: list[CircleBox] = self.create_super_pacgums()

        self.config: dict[str, Any] = config
        self.current_level: int = 0

    def reset(self, maze: MazeGenerator = None):
        global CENTER_X, CENTER_Y
        if maze is not None:
            self.maze = maze

        self.grid = self.maze.maze
        self.maze_height = len(self.grid)
        self.maze_width = len(self.grid[0])
        self.scale_x = self.screen_width / self.maze_width
        self.scale_y = self.screen_height / self.maze_height
        self.scale_x = min([self.scale_x, self.scale_y])
        self.scale_x -= self.scale_x % 2
        self.scale_y = self.scale_x

        self.game_duration = 0.0
        self.level_start = 0.0
        self.super_pacgum_state = False

        self.buttons = []
        buttons_width = 300
        buttons_height = 50
        window_offset = 40
        pause_button_x = int(self.screen_width - buttons_width - window_offset)
        pause_button_y = int(window_offset)
        pause_button = Button(pause_button_x,
                              pause_button_y,
                              buttons_width,
                              buttons_height,
                              "Pause Game",
                              color=pr.GRAY,
                              triggered_function=self.pause_action)
        self.add_button(pause_button)
        self.pause_menu = PauseMenu(self.screen_width, self.screen_height)
        self.paused = False
        self.total_paused_time = 0.0
        self.pause_started_at: float | None = None

        self.t_start = self.get_game_time()
        CENTER_X = int(
            (
                self.screen_width - self.scale_x * self.maze_width
            ) / 2
        )
        CENTER_Y = int(
            (
                self.screen_height - self.scale_y * self.maze_height
            ) / 2
        )

        CENTER_X -= CENTER_X % 10
        CENTER_Y -= CENTER_Y % 10

        self.collision_boxs = self.create_collision_boxs()

        self.bullets = []
        SIZE_PACMAN = self.update_radius()
        hitbox_w = self.scale_x - 2 * WALL_WIDTH
        hitbox_h = self.scale_y - 2 * WALL_WIDTH
        is_pair = (self.maze_width % 2 + 1) % 2
        self.player = Player(
            int(
                (0.5 + self.maze_width // 2 - is_pair) * self.scale_x
            ),
            int(
                (0.5 + self.maze_height // 2) * self.scale_y
            ),
            SIZE_PACMAN,
            hitbox_w,
            hitbox_h
        )

        self._init_raytracing()
        self.points = self.create_points()
        self.super_pacgums = self.create_super_pacgums()

        if hasattr(self, "assets") and self.assets:
            self.set_assets(self.assets)

    def get_game_time(self) -> float:
        """Return a pause-aware game time in seconds."""
        now = time.time()
        paused_time = self.total_paused_time
        if self.paused and self.pause_started_at is not None:
            paused_time += now - self.pause_started_at
        return now - paused_time

    def pause_action(self):
        if not self.paused:
            self.paused = True
            self.pause_started_at = time.time()
        else:
            self.resume_game()

    def resume_game(self):
        if self.paused and self.pause_started_at is not None:
            self.total_paused_time += time.time() - self.pause_started_at
            self.pause_started_at = None
        self.paused = False

    def get_nearest_walkable_cell_center(
        self,
        x: float,
        y: float,
    ) -> tuple[int, int]:
        """get the position of the nearest
        walkable cell center to the given position"""
        best_x = int(x)
        best_y = int(y)
        best_distance = None

        for cell_y in range(self.maze_height):
            for cell_x in range(self.maze_width):
                if self.grid[cell_y][cell_x] == 15:
                    continue

                center_x = int((cell_x + 0.5) * self.scale_x)
                center_y = int((cell_y + 0.5) * self.scale_y)
                distance = (center_x - x) ** 2 + (center_y - y) ** 2

                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best_x = center_x
                    best_y = center_y

        return best_x, best_y

    def sync_remove_collisions_state(self) -> None:
        """sync the playerposition with the nearest
        walkable cell after the remove_collisions cheat is disabled"""
        remove_collisions = self.pause_menu.cheats[REMOVE_COLLISIONS]
        # means that we just disabled remove collisions
        if self.remove_collisions_active and not remove_collisions:
            safe_x, safe_y = self.get_nearest_walkable_cell_center(
                self.player.x,
                self.player.y,
            )
            self.player.x = safe_x
            self.player.y = safe_y
            self.player.direction = (0, 0)
            self.player.try_direction = (0, 0)
            self.player.update_collision_box()

        self.remove_collisions_active = remove_collisions

    def set_assets(self, assets: dict):
        super().set_assets(assets)
        self.ghosts = [
            Ghost(
                self.assets["ghosts"]["pinky"],
                self.assets["ghosts"]["blue_ghost"],
                int(self.scale_x / 2),
                int(self.scale_y / 2),
                int(0.45 * self.scale_x),
                int(0.9 * self.scale_x),
                int(0.9 * self.scale_x)
            ),
            Ghost(
                self.assets["ghosts"]["clyde"],
                self.assets["ghosts"]["blue_ghost"],
                int(self.scale_x / 2),
                int((self.maze_height - 0.5) * self.scale_y),
                int(0.45 * self.scale_x),
                int(0.9 * self.scale_x),
                int(0.9 * self.scale_x)
            ),
            Ghost(
                self.assets["ghosts"]["inky"],
                self.assets["ghosts"]["blue_ghost"],
                int((self.maze_width - 0.5) * self.scale_x),
                int(self.scale_y / 2),
                int(0.45 * self.scale_x),
                int(0.9 * self.scale_x),
                int(0.9 * self.scale_x)
            ),
            Ghost(
                self.assets["ghosts"]["blinky"],
                self.assets["ghosts"]["blue_ghost"],
                int((self.maze_width - 0.5) * self.scale_x),
                int((self.maze_height - 0.5) * self.scale_y),
                int(0.45 * self.scale_x),
                int(0.9 * self.scale_x),
                int(0.9 * self.scale_x)
            )
        ]

    def create_collision_boxs(
        self,
    ) -> dict[str, list[list[list[RectangleBox]]]]:
        collision_boxs = {}

        boxes: list[list[list[RectangleBox]]] = [[
            [] for _ in range(self.maze_width)]
            for _ in range(self.maze_height)]

        added_boxes: list[list[list[RectangleBox]]] = [[
            [] for _ in range(self.maze_width)]
            for _ in range(self.maze_height)]

        collision_boxs["walls"] = boxes
        collision_boxs["added_boxes"] = added_boxes
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                cell = self.grid[y][x]

                start_x = int(x * self.scale_x)
                start_y = int(y * self.scale_y)
                next_x = int((x + 1) * self.scale_x)
                next_y = int((y + 1) * self.scale_y)
                cell_width = next_x - start_x
                cell_height = next_y - start_y

                # Box corners
                if y > 0 and x > 0:
                    added_boxes[y][x].append(
                        RectangleBox(
                            start_x - WALL_WIDTH,
                            start_y - WALL_WIDTH,
                            int(2 * WALL_WIDTH),
                            int(2 * WALL_WIDTH)
                        )
                    )

                # Box isolated cells
                if cell == 15:
                    boxes[y][x].append(
                        RectangleBox(
                            start_x,
                            start_y,
                            cell_width,
                            cell_height
                        )
                    )
                    continue

                # Box walls
                if cell & NORTH:
                    boxes[y][x].append(
                        RectangleBox(
                            start_x,
                            start_y,
                            cell_width,
                            int(WALL_WIDTH)
                        )
                    )

                if cell & SOUTH:
                    boxes[y][x].append(
                        RectangleBox(
                            start_x,
                            next_y - WALL_WIDTH,
                            cell_width,
                            int(WALL_WIDTH),
                        )
                    )
                if cell & EAST:
                    boxes[y][x].append(
                        RectangleBox(
                            next_x - WALL_WIDTH,
                            start_y,
                            int(WALL_WIDTH),
                            cell_height,
                        )
                    )

                if cell & WEST:
                    boxes[y][x].append(
                        RectangleBox(
                            start_x,
                            start_y,
                            int(WALL_WIDTH),
                            cell_height,
                        )
                    )

        return collision_boxs

    def _build_wallmap(self) -> np.ndarray:
        """Précalcule un array booléen
           (H_px, W_px) : True = pixel dans un mur."""
        cell_w, cell_h = self.get_cell_pixel_size()
        H = self.maze_height * cell_h
        W = self.maze_width * cell_w
        wall = np.zeros((H, W), dtype=bool)

        for cy in range(self.maze_height):
            for cx in range(self.maze_width):
                cell = self.grid[cy][cx]
                x0 = cx * cell_w
                y0 = cy * cell_h
                x1 = x0 + cell_w
                y1 = y0 + cell_h

                if cell == 15:
                    wall[y0:y1, x0:x1] = True
                    continue
                if cell & NORTH:
                    wall[y0:y0 + WALL_WIDTH, x0:x1] = True
                if cell & SOUTH:
                    wall[y1 - WALL_WIDTH:y1, x0:x1] = True
                if cell & EAST:
                    wall[y0:y1, x1 - WALL_WIDTH:x1] = True
                if cell & WEST:
                    wall[y0:y1, x0:x0 + WALL_WIDTH] = True

            # Coins
            for cx in range(1, self.maze_width):
                c = self.grid[cy][cx]
                w_ = self.grid[cy][cx - 1]
                x0 = cx * cell_w
                y0 = cy * cell_h
                if cy > 0:
                    n = self.grid[cy - 1][cx]
                    nw = self.grid[cy - 1][cx - 1]
                    if c & NORTH and c & WEST:
                        wall[y0 - WALL_WIDTH:y0, x0 - WALL_WIDTH:x0] = True
                    if n & SOUTH and n & WEST:
                        wall[y0:y0 + WALL_WIDTH, x0 - WALL_WIDTH:x0] = True
                    if w_ & NORTH and w_ & EAST:
                        wall[y0 - WALL_WIDTH:y0, x0:x0 + WALL_WIDTH] = True
                    if nw & SOUTH and nw & EAST:
                        wall[y0:y0 + WALL_WIDTH, x0:x0 + WALL_WIDTH] = True

        return wall

    def _init_raytracing(self):
        """initializes GPU ray tracing by creating wallmap texture"""
        if hasattr(self, "wallmap_texture"):
            pr.unload_texture(self.wallmap_texture)
        if hasattr(self, "shader"):
            pr.unload_shader(self.shader)

        self._wallmap = np.ascontiguousarray(self._build_wallmap())
        height, width = self._wallmap.shape

        wallmap_rgba = np.zeros((height, width, 4), dtype=np.uint8)
        wallmap_rgba[self._wallmap] = [255, 255, 255, 255]

        img = pr.gen_image_color(width, height, pr.BLANK)
        self.wallmap_texture = pr.load_texture_from_image(img)
        pr.unload_image(img)

        data_ptr = pr.ffi.cast("void *", wallmap_rgba.ctypes.data)
        pr.update_texture(self.wallmap_texture, data_ptr)

        self.shader = pr.load_shader("", "src/lighting.fs")
        self.maze_size_loc = pr.get_shader_location(self.shader, "mazeSize")
        self.light_pos_loc = pr.get_shader_location(self.shader, "lightPos")
        self.radius_loc = pr.get_shader_location(self.shader, "radius")
        self.color_loc = pr.get_shader_location(self.shader, "lightColor")

    def create_points(self) -> list[CircleBox]:
        points = []
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                if self.grid[y][x] != 15:
                    pos_x = int(
                        (x + 0.5) * self.scale_x
                    )
                    pos_y = int(
                        (y + 0.5) * self.scale_y
                    )
                    if pos_x != self.player.x or \
                            pos_y != self.player.y:

                        points.append(
                            CircleBox(
                                pos_x,
                                pos_y,
                                int(0.1 * self.scale_x)
                            )
                        )

        return points

    def create_super_pacgums(self) -> list[CircleBox]:
        super_pacgums = []
        for x in [0, self.maze_width - 1]:
            for y in [0, self.maze_height - 1]:
                pos_x = int(
                    (x + 0.5) * self.scale_x
                )
                pos_y = int(
                    (y + 0.5) * self.scale_y
                )
                super_pacgums.append(
                    CircleBox(
                        pos_x,
                        pos_y,
                        30
                    )
                )
        return super_pacgums

    def draw_maze(self):
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                start_x = int(x * self.scale_x)
                start_y = int(y * self.scale_y)
                next_x = int((x + 1) * self.scale_x)
                next_y = int((y + 1) * self.scale_y)
                cell_width = next_x - start_x
                cell_height = next_y - start_y

                # Draw corners
                if y > 0 and x > 0:
                    if self.grid[y][x] & NORTH and \
                            self.grid[y][x] & WEST:
                        pr.draw_rectangle(
                            start_x - WALL_WIDTH + CENTER_X,
                            start_y - WALL_WIDTH + CENTER_Y,
                            int(WALL_WIDTH),
                            int(WALL_WIDTH),
                            WALL_COLOR
                        )

                    if self.grid[y - 1][x] & SOUTH and \
                            self.grid[y - 1][x] & WEST:
                        pr.draw_rectangle(
                            start_x - WALL_WIDTH + CENTER_X,
                            start_y + CENTER_Y,
                            int(WALL_WIDTH),
                            int(WALL_WIDTH),
                            WALL_COLOR
                        )

                    if self.grid[y][x - 1] & NORTH and \
                            self.grid[y][x - 1] & EAST:
                        pr.draw_rectangle(
                            start_x + CENTER_X,
                            start_y - WALL_WIDTH + CENTER_Y,
                            int(WALL_WIDTH),
                            int(WALL_WIDTH),
                            WALL_COLOR
                        )

                    if self.grid[y - 1][x - 1] & SOUTH and \
                            self.grid[y - 1][x - 1] & EAST:
                        pr.draw_rectangle(
                            start_x + CENTER_X,
                            start_y + CENTER_Y,
                            int(WALL_WIDTH),
                            int(WALL_WIDTH),
                            WALL_COLOR
                        )

                # Draw isolated cells
                if self.grid[y][x] == 15:
                    pr.draw_rectangle(start_x + CENTER_X,
                                      start_y + CENTER_Y,
                                      cell_width,
                                      cell_height,
                                      WALL_COLOR)
                    continue

                # Draw walls
                if self.grid[y][x] & NORTH:
                    pr.draw_rectangle(start_x + CENTER_X,
                                      start_y + CENTER_Y,
                                      cell_width,
                                      int(WALL_WIDTH),
                                      WALL_COLOR)
                if self.grid[y][x] & SOUTH:
                    pr.draw_rectangle(start_x + CENTER_X,
                                      next_y - WALL_WIDTH + CENTER_Y,
                                      cell_width,
                                      int(WALL_WIDTH),
                                      WALL_COLOR)
                if self.grid[y][x] & EAST:
                    pr.draw_rectangle(next_x - WALL_WIDTH + CENTER_X,
                                      start_y + CENTER_Y,
                                      int(WALL_WIDTH),
                                      cell_height,
                                      WALL_COLOR)

                if self.grid[y][x] & WEST:
                    pr.draw_rectangle(start_x + CENTER_X,
                                      start_y + CENTER_Y,
                                      int(WALL_WIDTH),
                                      cell_height,
                                      WALL_COLOR)

    def create_future_box(self, new_x: float, new_y: float) -> CollisionBox:
        if isinstance(self.player.box, CircleBox):
            return CircleBox(new_x, new_y, float(self.player.radius))
        elif isinstance(self.player.box, RectangleBox):
            rect_x = new_x - (self.player.box.width / 2.0)
            rect_y = new_y - (self.player.box.height / 2.0)

            return RectangleBox(rect_x,
                                rect_y,
                                float(self.player.box.width),
                                float(self.player.box.height))
        else:
            raise TypeError("Unknown Box Type")

    def check_collision_x(self, box_y: int, new_x: float,
                          future_box_x: CollisionBox) -> bool:

        collision_x = False

        for dy in [-1, 0, 1]:
            ny = int(box_y) + dy
            if 0 <= ny < self.maze_height:
                box_x = int(new_x // self.scale_x)
                for dx in [-1, 0, 1]:
                    nx = box_x + dx
                    if 0 <= nx < self.maze_width:
                        for box in self.collision_boxs["walls"][ny][nx]:
                            if future_box_x.collides_with(box):
                                return True
                        for box in self.collision_boxs["added_boxes"][ny][nx]:
                            if future_box_x.collides_with(box):
                                return True
        return collision_x

    def check_collision_y(self, box_x: int, new_y: float,
                          future_box_y: CollisionBox) -> bool:
        collision_y = False

        for dy in [-1, 0, 1]:
            ny = int(new_y // self.scale_y) + dy
            if 0 <= ny < self.maze_height:
                box_x = int(box_x)
                for dx in [-1, 0, 1]:
                    nx = box_x + dx
                    if 0 <= nx < self.maze_width:
                        for box in self.collision_boxs["walls"][ny][nx]:
                            if future_box_y.collides_with(box):
                                return True
                        for box in self.collision_boxs["added_boxes"][ny][nx]:
                            if future_box_y.collides_with(box):
                                return True
        return collision_y

    def collision_events(
        self,
        new_x: float, new_y: float,
        ghost: Ghost | None = None,
        ignore_collisions: bool = False
    ):
        hit = self.player.hitbox
        cond1: bool = new_x + hit.radius < \
            self.scale_x * self.maze_width
        cond2: bool = new_x - hit.radius > 0
        cond3: bool = new_y + hit.radius < \
            self.scale_y * self.maze_height
        cond4: bool = new_y - hit.radius > 0

        inside_maze: bool = cond1 and cond2 and cond3 and cond4

        if ghost is None:
            if not inside_maze:
                return
            ghost = self.player

        base_y = ghost.y

        maze_pixels_x = self.maze_width * self.scale_x
        maze_pixels_y = self.maze_height * self.scale_y
        new_x = max(0, min(new_x, maze_pixels_x - 1))
        new_y = max(0, min(new_y, maze_pixels_y - 1))

        if ignore_collisions:
            ghost.x = new_x
            ghost.y = new_y
            ghost.update_collision_box()
            return

        future_box_x = self.create_future_box(new_x, base_y)

        box_y = int(base_y // self.scale_y)
        collision_x = self.check_collision_x(box_y, new_x, future_box_x)

        if not collision_x:
            ghost.x = new_x

        future_box_y = self.create_future_box(ghost.x, new_y)

        box_x = int(ghost.x // self.scale_x)
        collision_y = self.check_collision_y(box_x, new_y, future_box_y)

        if not collision_y:
            ghost.y = new_y
        ghost.update_collision_box()

    def can_move_direction(
        self,
        add_x: int, add_y: int,
        ghost: Ghost | None = None,
    ) -> bool:
        if ghost is None:
            ghost = self.player

        base_y = ghost.y

        new_x = ghost.x + add_x
        new_y = ghost.y + add_y

        maze_pixels_x = self.maze_width * self.scale_x
        maze_pixels_y = self.maze_height * self.scale_y
        new_x = max(0, min(new_x, maze_pixels_x - 1))
        new_y = max(0, min(new_y, maze_pixels_y - 1))

        future_box_x = self.create_future_box(new_x, base_y)

        box_y = int(base_y // self.scale_y)

        collision_x = self.check_collision_x(box_y, new_x, future_box_x)

        future_box_y = self.create_future_box(ghost.x, new_y)

        box_x = int(ghost.x // self.scale_x)
        collision_y = self.check_collision_y(box_x, new_y, future_box_y)

        return not collision_x and not collision_y

    def death_event(self) -> None:
        self.nb_wait += 1
        self.life -= 1

        for ghost in self.ghosts:
            ghost.direction = (0, 0)
            ghost.try_direction = (0, 0)
            ghost.unlock_destination()

        self.ghosts[0].x = int(self.scale_x / 2)
        self.ghosts[0].y = int(self.scale_y / 2)

        self.ghosts[1].x = int(self.scale_x / 2)
        self.ghosts[1].y = int(
            (self.maze_height - 0.5) * self.scale_y
        )

        self.ghosts[2].x = int(
            (self.maze_width - 0.5) * self.scale_x
        )
        self.ghosts[2].y = int(self.scale_y / 2)

        self.ghosts[3].x = int(
            (self.maze_width - 0.5) * self.scale_x
        )
        self.ghosts[3].y = int(
            (self.maze_height - 0.5) * self.scale_y
        )

        for ghost_to_reset in self.ghosts:
            ghost_to_reset.update_collision_box()

        is_pair = (self.maze_width % 2 + 1) % 2
        self.player.x = int(
            (0.5 + self.maze_width // 2 - is_pair) * self.scale_x
        )
        self.player.y = int(
            (0.5 + self.maze_height // 2) * self.scale_y
        )
        self.player.direction = (0, 0)
        self.player.try_direction = (0, 0)
        self.player.update_collision_box()

        self.t_start = self.get_game_time()

    def handle_events(self, mouse_angle_deg: float) -> None:
        """Handle player input and ghost movement, then update score/life."""
        remove_collisions = self.pause_menu.cheats[REMOVE_COLLISIONS]
        freeze_ghosts = self.pause_menu.cheats[FREEZE_GHOSTS]
        ak47_active: bool = self.pause_menu.cheats[AK47_ALWAYS_ACTIVE] or \
            self.super_pacgum_state

        # usefull if the player is in a wall
        ghost_target_x = self.player.x
        ghost_target_y = self.player.y
        if remove_collisions:
            ghost_target_x, ghost_target_y = (
                self.get_nearest_walkable_cell_center(
                    self.player.x,
                    self.player.y,
                )
            )
        # Ghosts
        if self.get_game_time() - self.t_start < 3:
            self.update_game_duration = False
            if self.level_start != 0.0:
                # to avoid incrementing the time when we die
                self.level_start += pr.get_frame_time()
            return
        elif self.level_start == 0.0:
            self.level_start = self.get_game_time()
            self.game_duration = 0.0
        self.update_game_duration = True

        for ghost in self.ghosts:
            if not freeze_ghosts:
                can_move = self.get_game_time() - ghost.last_frozen > \
                    AK47_FREEZE_TIME
                if can_move:
                    if ghost.destination is not None:
                        time_elapsed = self.get_game_time() - ghost.death_time
                        if time_elapsed >= GHOST_RETURN_SPAWN_TIME:
                            ghost.x = ghost.destination[0]
                            ghost.y = ghost.destination[1]
                            ghost.destination = None
                        else:
                            ratio = time_elapsed / GHOST_RETURN_SPAWN_TIME
                            ghost.x = ghost.death_position[0] + (
                                ghost.destination[0] - ghost.death_position[0]
                            ) * ratio
                            ghost.y = ghost.death_position[1] + (
                                ghost.destination[1] - ghost.death_position[1]
                            ) * ratio
                        ghost.update_collision_box()
                        continue
                    ghost.move(
                        self.grid,
                        int(ghost_target_x),
                        int(ghost_target_y),
                        int(self.scale_x),
                        int(self.scale_y),
                        self.super_pacgum_state
                    )

                    add_ghost_x = ghost.direction[0]
                    add_ghost_y = ghost.direction[1]

                    if self.can_move_direction(
                        ghost.try_direction[0],
                        ghost.try_direction[1],
                        ghost
                    ):
                        ghost.direction = ghost.try_direction
                        add_ghost_x = ghost.try_direction[0]
                        add_ghost_y = ghost.try_direction[1]

                    self.collision_events(
                        ghost.x + add_ghost_x,
                        ghost.y + add_ghost_y,
                        ghost
                    )

        # Player
        right = pr.is_key_down(
            pr.KeyboardKey.KEY_RIGHT) or pr.is_key_down(
            pr.KeyboardKey.KEY_D)
        left = pr.is_key_down(
            pr.KeyboardKey.KEY_LEFT) or pr.is_key_down(
            pr.KeyboardKey.KEY_A)
        up = pr.is_key_down(
            pr.KeyboardKey.KEY_UP) or pr.is_key_down(
            pr.KeyboardKey.KEY_W)
        down = pr.is_key_down(
            pr.KeyboardKey.KEY_DOWN) or pr.is_key_down(
            pr.KeyboardKey.KEY_S)

        left_click = pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_LEFT)

        nb_bounces = self.pause_menu.cheats[NB_BOUNCES]
        if BULLET_FIRE_RATE > 0:
            bullet_rate = 1 / BULLET_FIRE_RATE
        else:
            bullet_rate = 0

        bullet_ready = self.get_game_time() - self.last_bullet > bullet_rate
        if ak47_active and left_click and \
                bullet_ready:
            self.bullets.append(
                Bullet(
                    self.player.x,
                    self.player.y,
                    BULLET_RADIUS,
                    mouse_angle_deg,
                    BULLET_SPEED,
                    bounces=nb_bounces
                )
            )
            self.last_bullet = self.get_game_time()
        if right:
            self.player.try_direction = (SPEED, 0)
            if remove_collisions or self.can_move_direction(SPEED, 0):
                self.player.direction = (SPEED, 0)

        if left:
            self.player.try_direction = (-SPEED, 0)
            if remove_collisions or self.can_move_direction(-SPEED, 0):
                self.player.direction = (-SPEED, 0)

        if up:
            self.player.try_direction = (0, -SPEED)
            if remove_collisions or self.can_move_direction(0, -SPEED):
                self.player.direction = (0, -SPEED)

        if down:
            self.player.try_direction = (0, SPEED)
            if remove_collisions or self.can_move_direction(0, SPEED):
                self.player.direction = (0, SPEED)

        add_x = self.player.direction[0]
        add_y = self.player.direction[1]

        if remove_collisions or self.can_move_direction(
            self.player.try_direction[0],
            self.player.try_direction[1]
        ):
            self.player.direction = self.player.try_direction
            add_x = self.player.try_direction[0]
            add_y = self.player.try_direction[1]

        self.collision_events(
            self.player.x + add_x,
            self.player.y + add_y,
            ignore_collisions=remove_collisions
        )

        for point in self.points:
            if point.collides_with(self.player.hitbox):
                self.score += self.config["points_per_pacgum"]
                self.points.remove(point)
                break

        for pacgum in self.super_pacgums:
            if pacgum.collides_with(self.player.hitbox):
                self.score += self.config["points_per_super_pacgum"]
                self.super_pacgum_state = True
                self.super_pacgums.remove(pacgum)
                self.last_super_pacgum = self.get_game_time()
                break

        for bullet in self.bullets:
            bullet.update()
            x = bullet.center_x
            y = bullet.center_y
            cell_x = int(x // self.scale_x)
            cell_y = int(y // self.scale_y)
            resolved = False
            for dx in [-1, 0, 1]:
                if resolved:
                    break
                nx = cell_x + dx
                if 0 <= nx < self.maze_width:
                    for dy in [-1, 0, 1]:
                        if resolved:
                            break
                        ny = cell_y + dy
                        if 0 <= ny < self.maze_height:
                            boxes = self.collision_boxs["walls"][ny][nx]
                            for box in boxes:
                                if bullet.collides_with(box):
                                    bullet.remaining_bounces -= 1
                                    bullet.center_x -= (
                                        bullet.speed * np.cos(bullet.angle)
                                    )
                                    bullet.center_y -= (
                                        bullet.speed * np.sin(bullet.angle)
                                    )
                                    closest_x = max(
                                        box.x, min(
                                            bullet.center_x,
                                            box.x + box.width))
                                    closest_y = max(
                                        box.y, min(
                                            bullet.center_y,
                                            box.y + box.height))
                                    dx_norm = bullet.center_x - closest_x
                                    dy_norm = bullet.center_y - closest_y

                                    if dx_norm == 0 and dy_norm == 0:
                                        bullet.angle += np.pi
                                    else:
                                        norm = np.hypot(dx_norm, dy_norm)
                                        nx_norm = dx_norm / norm
                                        ny_norm = dy_norm / norm
                                        vel_x = np.cos(bullet.angle)
                                        vel_y = np.sin(bullet.angle)
                                        dot_prod = vel_x * nx_norm + \
                                            vel_y * ny_norm

                                        if dot_prod < 0:
                                            rx = vel_x - 2 * dot_prod * nx_norm
                                            ry = vel_y - 2 * dot_prod * ny_norm
                                            bullet.angle = np.arctan2(ry, rx)
                                    resolved = True
                                    break

        to_remove = []
        for bullet in self.bullets:
            if bullet.remaining_bounces == 0:
                to_remove.append(bullet)
                continue

            for ghost in self.ghosts:
                if ghost.destination is not None:
                    continue
                if bullet.collides_with(ghost.hitbox):
                    ghost.freeze(self.get_game_time())
                    to_remove.append(bullet)
                    break

        for bullet in to_remove:
            self.bullets.remove(bullet)

        if not remove_collisions:
            invincibility = self.pause_menu.cheats[INVINCIBILITY]
            for ghost in self.ghosts:
                if ghost.hitbox.collides_with(self.player.hitbox):
                    if self.super_pacgum_state:
                        if freeze_ghosts:
                            self.score += self.config["points_per_ghost"]
                            ghost.x = ghost.initial_x
                            ghost.y = ghost.initial_y
                            ghost.destination = None
                            ghost.update_collision_box()
                        elif ghost.destination is None:
                            self.score += self.config["points_per_ghost"]
                            ghost.set_destination(ghost.initial_x,
                                                  ghost.initial_y,
                                                  self.get_game_time())
                    elif not invincibility:
                        self.death_event()
                    break

    def update_radius(self) -> float:
        """update the radius of an entity so it is not too big"""
        return min(self.scale_x, self.scale_y) // 2.5

    def update_entity(self, entity: Player,
                      scale_ratio_x: float,
                      scale_ratio_y: float):
        """update the position and radius of an entity"""
        entity.x *= scale_ratio_x
        entity.y *= scale_ratio_y
        entity.radius = self.update_radius()
        if isinstance(entity.box, RectangleBox):
            entity.box.width *= scale_ratio_x
            entity.box.height *= scale_ratio_y
        entity.update_collision_box()

    def draw_points(self) -> None:
        for point in self.points:
            pr.draw_circle(
                point.center_x + CENTER_X,
                point.center_y + CENTER_Y,
                point.radius, pr.WHITE
            )

    def draw_super_pacgums(self) -> None:
        for point in self.super_pacgums:
            pr.draw_circle(
                point.center_x + CENTER_X,
                point.center_y + CENTER_Y,
                int(self.scale_x * 0.4), pr.YELLOW
            )

    def draw_player(self):
        # draw hitbox for debugging
        dire = "right"
        cur_dir = self.player.direction
        if cur_dir[0] == -SPEED:
            dire = "left"
        elif cur_dir[1] == SPEED:
            dire = "down"
        elif cur_dir[1] == -SPEED:
            dire = "up"
        elif cur_dir[0] == SPEED:
            dire = "right"

        pacman_len = len(self.assets["pacman"])
        if pacman_len > 0:
            index = int((pr.get_time() * 20)) % pacman_len
            texture = self.assets["pacman"][index]
            scale = self.player.radius / (PACMAN_SPRITE_QUALITY / 2)
            pos_x = float(self.player.x)
            pos_y = float(self.player.y)
            rotation = float(self.get_rotation_from_str(dire))

            pr.draw_texture_pro(
                texture,
                pr.Rectangle(0, 0, texture.width, texture.height),
                pr.Rectangle(
                    pos_x + CENTER_X,
                    pos_y + CENTER_Y,
                    texture.width * scale,
                    texture.height * scale
                ),
                pr.Vector2(
                    (texture.width * scale) / 2.0,
                    (texture.height * scale) / 2.0
                ),
                rotation,
                pr.WHITE
            )
        """ pr.draw_rectangle(int(self.player.box.x) + CENTER_X,
                          int(self.player.box.y) + CENTER_Y,
                          int(self.player.box.width),
                          int(self.player.box.height),
                          pr.WHITE)
        pr.draw_circle(int(self.player.x) + CENTER_X,
                       int(self.player.y) + CENTER_Y,
                       int(self.player.radius),
                       pr.YELLOW) """

    def draw_lighting(self):
        pr.begin_blend_mode(pr.BlendMode.BLEND_ADDITIVE)
        pr.begin_shader_mode(self.shader)

        res_val = pr.ffi.new(
            "float[]", [
                float(
                    self._wallmap.shape[1]), float(
                    self._wallmap.shape[0])])
        pr.set_shader_value(
            self.shader,
            self.maze_size_loc,
            res_val,
            pr.ShaderUniformDataType.SHADER_UNIFORM_VEC2)

        light_x = max(0.0, min(float(self.player.x),
                               float(self._wallmap.shape[1] - 1)))
        light_y = max(0.0, min(float(self.player.y),
                               float(self._wallmap.shape[0] - 1)))
        pos_val = pr.ffi.new("float[]", [light_x, light_y])
        pr.set_shader_value(
            self.shader,
            self.light_pos_loc,
            pos_val,
            pr.ShaderUniformDataType.SHADER_UNIFORM_VEC2)

        rad_val = pr.ffi.new("float*", PACMAN_LIGHT_RADIUS)
        pr.set_shader_value(
            self.shader,
            self.radius_loc,
            rad_val,
            pr.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

        pac_color_r = PACMAN_LIGHT_COLOR_R
        pac_color_g = PACMAN_LIGHT_COLOR_G
        pac_color_b = PACMAN_LIGHT_COLOR_B
        time_left = SUPER_PACGUM_TIME - (
            self.get_game_time() - self.last_super_pacgum
        )

        if time_left < LIGHT_FADE_TIME:
            fade = max(0.0, time_left / LIGHT_FADE_TIME)
            pac_color_r *= fade
            pac_color_g *= fade
            pac_color_b *= fade

        col_val = pr.ffi.new("float[]", [pac_color_r / 255.0,
                                         pac_color_g / 255.0,
                                         pac_color_b / 255.0])
        pr.set_shader_value(
            self.shader,
            self.color_loc,
            col_val,
            pr.ShaderUniformDataType.SHADER_UNIFORM_VEC3)

        pr.draw_texture_ex(
            self.wallmap_texture,
            pr.Vector2(float(CENTER_X), float(CENTER_Y)),
            0.0, 1.0, pr.WHITE
        )

        pr.end_shader_mode()
        pr.end_blend_mode()

    def draw_floor(self):
        maze_w = int(self.maze_width * self.scale_x)
        maze_h = int(self.maze_height * self.scale_y)
        pr.draw_rectangle(CENTER_X, CENTER_Y, maze_w, maze_h, pr.BLACK)

    def draw_ghosts(self) -> None:
        for ghost in self.ghosts:

            if self.super_pacgum_state:
                texture = ghost.blue_ghost
            else:
                texture = ghost.ghost

            # même logique que pacman
            scale = (self.player.radius / (GHOST_SPRITE_QUALITY / 2)) * 0.5

            pr.draw_texture_pro(
                texture,
                pr.Rectangle(0, 0, texture.width, texture.height),
                pr.Rectangle(
                    ghost.x + CENTER_X,
                    ghost.y + CENTER_Y,
                    texture.width * scale,
                    texture.height * scale
                ),
                pr.Vector2(
                    (texture.width * scale) / 2.0,
                    (texture.height * scale) / 2.0
                ),
                0,
                pr.WHITE
            )

            """ pr.draw_rectangle(
                int(
                    ghost.box.x +
                    CENTER_X
                ),
                int(
                    ghost.box.y +
                    CENTER_Y
                ),
                int(
                    ghost.box.width
                ),
                int(
                    ghost.box.height
                ),
                pr.WHITE
            )

            pr.draw_circle(
                ghost.hitbox.center_x + CENTER_X,
                ghost.hitbox.center_y + CENTER_Y,
                ghost.hitbox.radius,
                pr.YELLOW
            ) """

    def get_angle_deg(self) -> float:
        mouse_pos = pr.get_mouse_position()
        player_pos = pr.Vector2(self.player.x + CENTER_X,
                                self.player.y + CENTER_Y)
        diff_vec: pr.Vector2 = pr.Vector2(mouse_pos.x - player_pos.x,
                                          mouse_pos.y - player_pos.y)
        angle_rad: float = atan2(diff_vec.y, diff_vec.x)
        angle_deg: float = (angle_rad * 180) / np.pi
        if angle_deg < 0:
            angle_deg += 360
        return angle_deg

    def draw_ak47(self, angle_deg: float) -> None:
        """draw the ak47 sprite at the pacman position"""
        scale = self.player.radius / (PACMAN_SPRITE_QUALITY / 2)
        source_height = AK47_SPRITE_QUALITY
        if 90 < angle_deg < 270:
            source_height = -AK47_SPRITE_QUALITY

        pivot_ratio_x = 0.25  # place it at 25% of the width
        pivot_ratio_y = 0.50  # place it at 50% of the height
        pr.draw_texture_pro(
            self.assets["ak47"],
            pr.Rectangle(0, 0, AK47_SPRITE_QUALITY, source_height),
            pr.Rectangle(
                self.player.x + CENTER_X,
                self.player.y + CENTER_Y,
                AK47_SPRITE_QUALITY * scale,
                AK47_SPRITE_QUALITY * scale),
            pr.Vector2((AK47_SPRITE_QUALITY * scale) * pivot_ratio_x,
                       (AK47_SPRITE_QUALITY * scale) * pivot_ratio_y),
            angle_deg,
            pr.WHITE
        )

    def get_cell_pixel_size(self) -> tuple[int, int]:
        return int(self.scale_x), int(self.scale_y)

    def update(self) -> str:
        """update the game logic, this is called every frame"""
        super().update()

        if self.update_game_duration:
            self.game_duration = self.get_game_time() - self.level_start
            if self.level_start == 0.0:
                self.game_duration = 0.0

        mouse_angle = self.get_angle_deg()
        if not self.paused:
            self.handle_events(mouse_angle)

        if self.get_game_time() - self.last_super_pacgum > SUPER_PACGUM_TIME:
            self.super_pacgum_state = False

        self.draw_floor()
        if self.super_pacgum_state:
            self.draw_lighting()
        self.draw_maze()

        self.draw_points()
        self.draw_super_pacgums()
        self.draw_player()

        self.draw_ghosts()

        bullet_color = pr.Color(225, 210, 180, 255)
        for bullet in self.bullets:
            pr.draw_circle(int(bullet.center_x + CENTER_X),
                           int(bullet.center_y + CENTER_Y),
                           int(bullet.radius),
                           bullet_color)

        if self.super_pacgum_state or \
                self.pause_menu.cheats[AK47_ALWAYS_ACTIVE]:
            self.draw_ak47(mouse_angle)

        if self.paused:
            pause_menu_result: str = self.pause_menu.update()
            self.sync_remove_collisions_state()
            if pause_menu_result == GAME_LOGIC:
                self.resume_game()

        texture = self.assets["pacman"][1]
        scale = self.player.radius / (PACMAN_SPRITE_QUALITY / 2)

        size: tuple[int, int] = (
            self.config["levels"][self.current_level]["width"],
            self.config["levels"][self.current_level]["height"]
        )

        datas: dict[str, str] = {
            "Level": self.config["levels"][self.current_level]["name"],
            "Size": str(size),
            "Score": str(self.score),
            "Time": f"{abs(self.game_duration):.1f}",
            "Max level time": str(self.config["level_max_time"])
        }

        index: int = 0
        offset: int = 20
        for (key, val) in datas.items():
            pr.draw_text(
                f"{key}: {val}",
                15,
                15 + index * offset + int(texture.height * scale),
                20, pr.WHITE
            )
            index += 1

        bonus_lives = self.pause_menu.cheats[BONUS_LIVES]

        bonus_lives = self.pause_menu.cheats[BONUS_LIVES]

        for k in range(self.life + bonus_lives):
            pr.draw_texture_pro(
                texture,
                pr.Rectangle(0, 0, texture.width, texture.height),
                pr.Rectangle(
                    (k + 1) * (texture.width * 1.2) * scale * 0.5,
                    15 + (texture.height * scale) / 2,
                    texture.width * scale * 0.5,
                    texture.height * scale * 0.5
                ),
                pr.Vector2(
                    (texture.width * scale) / 2.0,
                    (texture.height * scale) / 2.0
                ),
                0,
                pr.WHITE
            )

        if len(self.points) + len(self.super_pacgums) == 0:
            self.current_level += 1
            if self.current_level >= 10:
                return GAME_FINISH

            size: tuple[int, int] = (
                self.config["levels"][self.current_level]["width"],
                self.config["levels"][self.current_level]["height"]
            )

            seed = self.config["seed"]
            self.reset(MazeGenerator(size, seed=seed))

        if self.life + bonus_lives < 0:
            if not self.paused:
                return GAME_FINISH

        if self.game_duration > float(self.config["level_max_time"]):
            return GAME_FINISH

        return GAME_LOGIC
