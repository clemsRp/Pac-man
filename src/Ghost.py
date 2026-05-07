
from .Physics import CircleBox, RectangleBox
from mazegenerator.mazegenerator import MazeGenerator
from .solve_maze import find_path
from .Constants import SPEED, SOUTH, EAST, DELTA
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
        """
        Initialize the Ghost instance.

        Args:
            ghost
                pr.Texture: The standard texture for the ghost.
            blue_ghost
                pr.Texture: The texture for the ghost when fleeing.
            x
                float: The initial x coordinate of the ghost.
            y
                float: The initial y coordinate of the ghost.
            radius
                float: The radius of the ghost's circular hitbox.
            box_width
                int: The width of the ghost's rectangular collision box.
            box_height
                int: The height of the ghost's rectangular collision box.
        """
        self.x: float = x
        self.y: float = y
        self.radius = radius
        self.box: RectangleBox
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
        """
        Set the destination of the ghost.
        The ghost will have to go here without any collision.

        Args:
            x
                float: The destination x coordinate.
            y
                float: The destination y coordinate.
            game_time
                float: The current game time in seconds.

        Returns:
            None: No return value.
        """
        self.destination = (x, y)
        self.death_position = (self.x, self.y)
        self.death_time = game_time
        self.last_frozen = 0.0

    def unlock_destination(self) -> None:
        """
        Clear the destination of the ghost.

        Returns:
            None: No return value.
        """
        self.destination = None

    def can_see_player(self, px: int, py: int, gx: int,
                       gy: int, maze: list[list[int]]) -> bool:
        """
        Verify that the ghost can see the player in a straight line.

        Args:
            px
                int: The player's x cell coordinate.
            py
                int: The player's y cell coordinate.
            gx
                int: The ghost's x cell coordinate.
            gy
                int: The ghost's y cell coordinate.
            maze
                list[list[int]]: The maze grid.

        Returns:
            bool: True if the ghost can see the player, False otherwise.
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
    ) -> None:
        """
        Calculate and update the ghost's target direction based on
        the player position.

        Args:
            maze
                MazeGenerator: The maze object containing grid details.
            player_x
                int: The x coordinate of the player.
            player_y
                int: The y coordinate of the player.
            scale_x
                int: The x scaling factor of the grid.
            scale_y
                int: The y scaling factor of the grid.
            is_fleeing
                bool: If True, the ghost runs away from the player.

        Returns:
            None: No return value.
        """

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
                new_maze[py][px] = 0
                if self.random_target is None or (
                        gy, gx) == self.random_target:
                    queue = [(gy, gx)]
                    visited = {(gy, gx)}
                    furthest_node = (gy, gx)
                    max_dist = -1

                    while queue:
                        curr_y, curr_x = queue.pop(0)

                        dist = (curr_y - py)**2 + (curr_x - px)**2
                        if dist > max_dist:
                            max_dist = dist
                            furthest_node = (curr_y, curr_x)

                        for i in range(4):
                            mask = 1 << i
                            if new_maze[curr_y][curr_x] & mask:
                                delta = DELTA[mask]
                                next_node = (
                                    curr_y + delta[0], curr_x + delta[1])
                                if next_node not in visited and \
                                    0 <= next_node[0] < len(maze) and \
                                        0 <= next_node[1] < len(maze[0]):
                                    visited.add(next_node)
                                    queue.append(next_node)
                    self.random_target = furthest_node
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

        self.try_direction = (int(dire_x * SPEED), int(dire_y * SPEED))

    def update_collision_box(self) -> None:
        """
        Update the position of the ghost's collision boxes based on
        its coordinates.

        Returns:
            None: No return value.
        """
        self.hitbox.center_x = self.x
        self.hitbox.center_y = self.y
        self.hitbox.radius = self.radius

        self.box.x = self.x - self.box.width // 2
        self.box.y = self.y - self.box.height // 2

    def freeze(self, current_time: float) -> None:
        """
        Freeze the ghost for a short duration.

        Args:
            current_time
                float: The current game time.

        Returns:
            None: No return value.
        """
        self.last_frozen = current_time
