
from .Physics import CircleBox, RectangleBox, CollisionBox
from mazegenerator.mazegenerator import MazeGenerator
from .solve_maze import find_path
from .Constants import SPEED


class Ghost:
    def __init__(self,
                 ghost, blue_ghost,
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

        self.start_x: float = x
        self.start_y: float = y

        self.ghost = ghost
        self.blue_ghost = blue_ghost

        self.direction: tuple[int, int] = (0, 0)
        self.try_direction: tuple[int, int] = (0, 0)
        self.last_frozen: float = 0.0

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
