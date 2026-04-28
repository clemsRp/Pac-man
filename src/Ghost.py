
from .Physics import CircleBox, RectangleBox, CollisionBox
from mazegenerator.mazegenerator import MazeGenerator
from .solve_maze import find_path
from .Constants import SPEED
import pyray as pr


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

    def move(
        self, maze: MazeGenerator,
        player_x: int, player_y: int,
        scale_x: int, scale_y: int,
        is_killable: bool
    ):
        if is_killable:
            pass

        else:
            px = int((player_x - player_x % scale_x) / scale_x)
            py = int((player_y - player_y % scale_y) / scale_y)

            gx = int((self.x - self.x % scale_x) / scale_x)
            gy = int((self.y - self.y % scale_y) / scale_y)

            new_maze = [
                [~c for c in row] for row in maze
            ]

            if px == gx and py == gy:
                return

            path = find_path(
                new_maze, (gy, gx), (py, px)
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
