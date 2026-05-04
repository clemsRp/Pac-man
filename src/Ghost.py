
from .Physics import CircleBox, RectangleBox, CollisionBox
from mazegenerator.mazegenerator import MazeGenerator
from .solve_maze import find_path
from .Constants import SPEED, SOUTH, EAST
import pyray as pr
import random


class Ghost:
    def __init__(self,
                 ghost: pr.Texture,
                 blue_ghost: pr.Texture,
                 x: float = 60, y: float = 60,
                 radius: float = 30,
                 box_width: int = 60,
                 box_height: int = 60):
        self.x: float = x
        self.y: float = y
        self.radius = radius
        self.box: CollisionBox
        self.hitbox = CircleBox(x, y, radius)
        self.box = RectangleBox(
            x - box_width // 2,
            y - box_height // 2,
            box_width,
            box_height
        )

        self.initial_x = x
        self.initial_y = y

        self.ghost = ghost
        self.blue_ghost = blue_ghost

        self.direction: tuple[int, int] = (0, 0)
        self.try_direction: tuple[int, int] = (0, 0)
        self.last_frozen: float = 0.0
        self.death_time: float = 0.0
        self.death_position: tuple[float, float] | None = None
        self.destination: tuple[float, float] | None = None
        self.random_target: tuple[int, int] | None = None

    def set_destination(self, x: float, y: float, game_time: float) -> None:
        """set the destination of the ghost.
        the ghost will have to go here without
        any collision"""
        self.destination = (x, y)
        self.death_position = (self.x, self.y)
        self.death_time = game_time
        self.last_frozen = 0.0

    def unlock_destination(self):
        self.destination = None

    def can_see_player(self, px: int, py: int, gx: int,
                       gy: int, maze: list[list[int]]) -> bool:
        """
            Verifies that the ghost can see the player in a straight line.
        """

        # They must be aligned horizontally or vertically
        if gx != px and gy != py:
            return False

        # same column
        if gx == px:
            y_min = min(gy, py)
            y_max = max(gy, py)
            for y in range(y_min, y_max):
                if maze[y][gx] & SOUTH:
                    return False
            return True

        # same row
        if gy == py:
            x_min = min(gx, px)
            x_max = max(gx, px)
            for x in range(x_min, x_max):
                if maze[gy][x] & EAST:
                    return False
            return True

        return False

    def move(
        self, maze: MazeGenerator,
        player_x: int, player_y: int,
        scale_x: int, scale_y: int,
        is_fleeing: bool = False
    ):

        px = int((player_x - player_x % scale_x) / scale_x)
        py = int((player_y - player_y % scale_y) / scale_y)

        gx = int((self.x - self.x % scale_x) / scale_x)
        gy = int((self.y - self.y % scale_y) / scale_y)

        new_maze = [
            [~c for c in row] for row in maze
        ]

        # Try to see if player is visible in straight line
        see_player = self.can_see_player(px, py, gx, gy, maze)

        target = (py, px)
        if not see_player:
            if self.random_target is None or (gy, gx) == self.random_target:
                valid_targets = [(y, x) for y in range(len(maze))
                                 for x in range(len(maze[0]))
                                 if maze[y][x] != 15]

                if valid_targets:
                    self.random_target = random.choice(valid_targets)
                else:
                    self.random_target = (gy, gx)

            target = self.random_target
        else:
            if is_fleeing:
                if self.random_target is None or (gy, gx) == self.random_target:
                    valid_targets = [(y, x) for y in range(len(maze))
                                     for x in range(len(maze[0]))
                                     if maze[y][x] != 15]
    
                    if valid_targets:
                        self.random_target = max(valid_targets, key=lambda t: (t[0]-py)**2 + (t[1]-px)**2)
                    else:
                        self.random_target = (gy, gx)
                target = self.random_target
            else:
                self.random_target = None
                target = (py, px)

        if target[1] == gx and target[0] == gy:
            return

        path = find_path(
            new_maze, (gy, gx), target
        )[0]

        dire_x = 0
        dire_y = 0

        if path is not None and len(path) > 1:
            dire_x = path[1][1] - path[0][1]
            dire_y = path[1][0] - path[0][0]

        self.try_direction = (dire_x * SPEED, dire_y * SPEED)

    def update_collision_box(self):
        self.hitbox.center_x = self.x
        self.hitbox.center_y = self.y
        self.hitbox.radius = self.radius

        self.box.x = self.x - self.box.width // 2
        self.box.y = self.y - self.box.height // 2

    def freeze(self, current_time: float):
        self.last_frozen = current_time
