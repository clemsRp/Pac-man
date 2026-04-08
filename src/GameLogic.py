import pyray as pr
from .Constants import (NORTH, EAST, SOUTH, WEST)
from mazegenerator.mazegenerator import MazeGenerator
from .Physics import CollisionBox, CircleBox, RectangleBox
from .Player import Player
from .Ghost import Ghost
from .Interfaces import Interface
from .Constants import (MAIN_MENU, GAME_LOGIC, PACMAN_SPRITE_QUALITY)
WALL_WIDTH = 3
WALL_COLOR = pr.BLUE
SPEED = 2.0


class GameLogic(Interface):
    def __init__(self, maze: MazeGenerator,
                 screen_width: int, screen_height: int):
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
        self.entities: list[CollisionBox] = []
        self.collision_boxs: list[
            list[
                list[
                    RectangleBox]
            ]] = self.create_collision_boxs()

        self.entities = [Player(538, 300, 20, self.scale_x, self.scale_y)]
        self.assets: dict = {}
        SIZE_PACMAN = self.update_radius()
        hitbox_w = self.scale_x - 2 * WALL_WIDTH
        hitbox_h = self.scale_y - 2 * WALL_WIDTH
        self.player = Player(int((0.5 + self.maze_width // 2) * self.scale_x),
                             int((0.5 + self.maze_height // 2) * self.scale_y),
                             SIZE_PACMAN,
                             hitbox_w, hitbox_h, "rect")

        self.ghosts = []

        self.points = self.create_points()

    def set_assets(self, assets: dict):
        super().set_assets(assets)
        self.ghosts = [
            Ghost(
                self.assets["ghosts"]["pinky"],
                self.assets["ghosts"]["blue_ghost"],
                int(self.scale_x / 2),
                int(self.scale_y / 2)
            ),
            Ghost(
                self.assets["ghosts"]["clyde"],
                self.assets["ghosts"]["blue_ghost"],
                int(self.scale_x / 2),
                int((self.maze_height - 0.5) * self.scale_y)
            ),
            Ghost(
                self.assets["ghosts"]["inky"],
                self.assets["ghosts"]["blue_ghost"],
                int((self.maze_width - 0.5) * self.scale_x),
                int(self.scale_y / 2)
            ),
            Ghost(
                self.assets["ghosts"]["blinky"],
                self.assets["ghosts"]["blue_ghost"],
                int((self.maze_width - 0.5) * self.scale_x),
                int((self.maze_height - 0.5) * self.scale_y)
            )
        ]

    def create_collision_boxs(self) -> list[list[list[RectangleBox]]]:
        boxes: list[list[list[RectangleBox]]] = [[
            [] for _ in range(self.maze_width)]
            for _ in range(self.maze_height)]

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
                    boxes[y][x].append(
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

        return boxes

    def create_points(self) -> list:
        points = []
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                if self.grid[y][x] != 15:
                    points.append((x, y))

        return points

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
                            start_x - WALL_WIDTH,
                            start_y - WALL_WIDTH,
                            int(WALL_WIDTH),
                            int(WALL_WIDTH),
                            WALL_COLOR
                        )

                    if self.grid[y - 1][x] & SOUTH and \
                            self.grid[y - 1][x] & WEST:
                        pr.draw_rectangle(
                            start_x - WALL_WIDTH,
                            start_y,
                            int(WALL_WIDTH),
                            int(WALL_WIDTH),
                            WALL_COLOR
                        )

                    if self.grid[y][x - 1] & NORTH and \
                            self.grid[y][x - 1] & EAST:
                        pr.draw_rectangle(
                            start_x,
                            start_y - WALL_WIDTH,
                            int(WALL_WIDTH),
                            int(WALL_WIDTH),
                            WALL_COLOR
                        )

                    if self.grid[y - 1][x - 1] & SOUTH and \
                            self.grid[y - 1][x - 1] & EAST:
                        pr.draw_rectangle(
                            start_x,
                            start_y,
                            int(WALL_WIDTH),
                            int(WALL_WIDTH),
                            WALL_COLOR
                        )

                # Draw isolated cells
                if self.grid[y][x] == 15:
                    pr.draw_rectangle(start_x,
                                      start_y,
                                      cell_width,
                                      cell_height,
                                      WALL_COLOR)
                    continue

                # Draw walls
                if self.grid[y][x] & NORTH:
                    pr.draw_rectangle(start_x,
                                      start_y,
                                      cell_width,
                                      int(WALL_WIDTH),
                                      WALL_COLOR)
                if self.grid[y][x] & SOUTH:
                    pr.draw_rectangle(start_x,
                                      next_y - WALL_WIDTH,
                                      cell_width,
                                      int(WALL_WIDTH),
                                      WALL_COLOR)
                if self.grid[y][x] & EAST:
                    pr.draw_rectangle(next_x - WALL_WIDTH,
                                      start_y,
                                      int(WALL_WIDTH),
                                      cell_height,
                                      WALL_COLOR)

                if self.grid[y][x] & WEST:
                    pr.draw_rectangle(start_x,
                                      start_y,
                                      int(WALL_WIDTH),
                                      cell_height,
                                      WALL_COLOR)

        """ for y in range(len(self.collision_boxs)):
            for x in range(len(self.collision_boxs[y])):
                for el in self.collision_boxs[y][x]:
                    pr.draw_rectangle(
                        el.x, el.y,
                        el.width, el.height,
                        pr.WHITE
                    ) """

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
        # for entity in self.entities:
        #     if entity.box.collides_with(future_box_x):
        #         return True

        for dy in [-1, 0, 1]:
            ny = int(box_y) + dy
            if 0 <= ny < self.maze_height:
                box_x = int(new_x // self.scale_x)
                for dx in [-1, 0, 1]:
                    nx = box_x + dx
                    if 0 <= nx < self.maze_width:
                        for box in self.collision_boxs[ny][nx]:
                            if future_box_x.collides_with(box):
                                return True
        return collision_x

    def check_collision_y(self, box_x: int, new_y: float,
                          future_box_y: CollisionBox) -> bool:
        collision_y = False
        # for entity in self.entities:
        #     if entity.box.collides_with(future_box_y):
        #         return True

        for dy in [-1, 0, 1]:
            ny = int(new_y // self.scale_y) + dy
            if 0 <= ny < self.maze_height:
                box_x = int(box_x)
                for dx in [-1, 0, 1]:
                    nx = box_x + dx
                    if 0 <= nx < self.maze_width:
                        for box in self.collision_boxs[ny][nx]:
                            if future_box_y.collides_with(box):
                                return True
        return collision_y

    def player_collision_events(
        self,
        new_x: float, new_y: float
    ):
        base_y = self.player.y

        maze_pixels_x = self.maze_width * self.scale_x
        maze_pixels_y = self.maze_height * self.scale_y
        new_x = max(0, min(new_x, maze_pixels_x - 1))
        new_y = max(0, min(new_y, maze_pixels_y - 1))

        future_box_x = self.create_future_box(new_x, base_y)

        box_y = int(base_y // self.scale_y)
        collision_x = self.check_collision_x(box_y, new_x, future_box_x)

        if not collision_x:
            self.player.x = new_x

        future_box_y = self.create_future_box(self.player.x, new_y)

        box_x = int(self.player.x // self.scale_x)
        collision_y = self.check_collision_y(box_x, new_y, future_box_y)

        if not collision_y:
            self.player.y = new_y
        self.player.update_collision_box()

    def can_move_direction(self, add_x: int, add_y: int) -> bool:
        base_y = self.player.y

        new_x = self.player.x + add_x
        new_y = self.player.y + add_y

        maze_pixels_x = self.maze_width * self.scale_x
        maze_pixels_y = self.maze_height * self.scale_y
        new_x = max(0, min(new_x, maze_pixels_x - 1))
        new_y = max(0, min(new_y, maze_pixels_y - 1))

        future_box_x = self.create_future_box(new_x, base_y)

        box_y = int(base_y // self.scale_y)
        collision_x = self.check_collision_x(box_y, new_x, future_box_x)

        future_box_y = self.create_future_box(self.player.x, new_y)

        box_x = int(self.player.x // self.scale_x)
        collision_y = self.check_collision_y(box_x, new_y, future_box_y)

        return not collision_x and not collision_y

    def handle_events(self):
        if pr.is_key_down(pr.KeyboardKey.KEY_RIGHT):
            self.player.try_direction = (SPEED, 0)
            if self.can_move_direction(SPEED, 0):
                self.player.direction = (SPEED, 0)

        if pr.is_key_down(pr.KeyboardKey.KEY_LEFT):
            self.player.try_direction = (-SPEED, 0)
            if self.can_move_direction(-SPEED, 0):
                self.player.direction = (-SPEED, 0)

        if pr.is_key_down(pr.KeyboardKey.KEY_UP):
            self.player.try_direction = (0, -SPEED)
            if self.can_move_direction(0, -SPEED):
                self.player.direction = (0, -SPEED)

        if pr.is_key_down(pr.KeyboardKey.KEY_DOWN):
            self.player.try_direction = (0, SPEED)
            if self.can_move_direction(0, SPEED):
                self.player.direction = (0, SPEED)

        add_x = self.player.direction[0]
        add_y = self.player.direction[1]

        if self.can_move_direction(
            self.player.try_direction[0],
            self.player.try_direction[1]
        ):
            self.player.direction = self.player.try_direction
            add_x = self.player.try_direction[0]
            add_y = self.player.try_direction[1]

        self.player_collision_events(
            self.player.x + add_x,
            self.player.y + add_y
        )

        px = self.player.x // self.scale_x
        py = self.player.y // self.scale_y

        if (px, py) in self.points:
            self.points.remove((px, py))

    def update_radius(self) -> float:
        return min(self.scale_x, self.scale_y) // 2.5

    def update_entity(self, entity: Player,
                      scale_ratio_x: float,
                      scale_ratio_y: float):
        entity.x *= scale_ratio_x
        entity.y *= scale_ratio_y
        entity.radius = self.update_radius()
        if isinstance(entity.box, RectangleBox):
            entity.box.width *= scale_ratio_x
            entity.box.height *= scale_ratio_y
        entity.update_collision_box()

    def draw_points(self) -> None:
        for point in self.points:
            x: int = int(
                self.scale_x / 2 +
                point[0] * self.scale_x
            )
            y: int = int(
                self.scale_y / 2 +
                point[1] * self.scale_y
            )

            pr.draw_circle(
                x, y, 10, pr.WHITE
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

        index = 2
        time = (pr.get_time() * 100) % 60
        if time > 20:
            index -= 1
        if time > 40:
            index -= 1

        texture = self.assets["pacman"][dire][index]
        scale = self.player.radius / (PACMAN_SPRITE_QUALITY / 2)
        pos_x = float(self.player.x - self.player.radius)
        pos_y = float(self.player.y - self.player.radius)

        pr.draw_texture_ex(
            texture,
            pr.Vector2(pos_x, pos_y),
            0.0,
            scale,
            pr.WHITE
        )
        """ pr.draw_circle(int(self.player.x),
                       int(self.player.y),
                       int(self.player.radius),
                       pr.YELLOW) """
        """ pr.draw_rectangle(int(self.player.box.x),
                          int(self.player.box.y),
                          int(self.player.box.width),
                          int(self.player.box.height),
                          pr.WHITE) """

    def draw_ghosts(self):
        for ghost in self.ghosts:
            pr.draw_texture(
                ghost.ghost,
                int(ghost.x - 32),
                int(ghost.y - 32),
                pr.WHITE
            )

    def update(self) -> str:
        self.draw_maze()
        self.handle_events()
        self.draw_points()
        self.draw_player()
        self.draw_ghosts()
        """ pr.draw_circle(int(self.entities[0].x),
                        int(self.entities[0].y),
                        (self.entities[0].radius),
                        pr.RED) """

        pr.draw_text("Score: 42", 10, 10, 20, pr.RAYWHITE)

        return GAME_LOGIC
