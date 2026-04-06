import pyray as pr
from .Constants import (NORTH, EAST, SOUTH, WEST)
from mazegenerator.mazegenerator import MazeGenerator
from .Physics import CollisionBox, CircleBox, RectangleBox
from .Player import Player

WALL_WIDTH = 3
WALL_COLOR = pr.BLUE


class Display:
    def __init__(self, maze: MazeGenerator):
        self.maze: MazeGenerator = maze
        self.grid: list[list[int]] = self.maze.maze
        self.maze_height: int = len(self.grid)
        self.maze_width: int = len(self.grid[0])
        self.screen_width: int = 1500  # will be updated in resize_event
        self.screen_height: int = 1500
        self.scale_x: float = self.screen_width / self.maze_width
        self.scale_y: float = self.screen_height / self.maze_height
        self.entities: list[CollisionBox] = []
        self.collision_boxs: list[
                                list[
                                    list[
                                     RectangleBox]
                                     ]] = self.create_collision_boxs()

    def create_collision_boxs(self) -> list[list[list[RectangleBox]]]:
        boxes: list[list[list[RectangleBox]]] = [[
                 [] for _ in range(self.maze_width)]
                 for _ in range(self.maze_height)]

        for y in range(self.maze_height):
            for x in range(self.maze_width):
                cell = self.grid[y][x]

                if cell & NORTH:
                    boxes[y][x].append(
                        RectangleBox(
                            x * self.scale_x,
                            y * self.scale_y,
                            self.scale_x,
                            WALL_WIDTH
                        )
                    )

                if cell & SOUTH:
                    boxes[y][x].append(
                        RectangleBox(
                            x * self.scale_x,
                            (y + 1) * self.scale_y,
                            self.scale_x,
                            WALL_WIDTH
                        )
                    )

                if cell & EAST:
                    boxes[y][x].append(
                        RectangleBox(
                            (x + 1) * self.scale_x,
                            y * self.scale_y,
                            WALL_WIDTH,
                            self.scale_y + WALL_WIDTH
                        )
                    )

                if cell & WEST:
                    boxes[y][x].append(
                        RectangleBox(
                            x * self.scale_x,
                            y * self.scale_y,
                            WALL_WIDTH,
                            self.scale_y + WALL_WIDTH
                        )
                    )

                boxes[y][x].append(
                    RectangleBox(
                        (x + 1) * self.scale_x,
                        (y + 1) * self.scale_y,
                        WALL_WIDTH,
                        WALL_WIDTH
                    )
                )

        return boxes

    def draw_maze(self):
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                start_x = int(x * self.scale_x)
                start_y = int(y * self.scale_y)
                next_x = int((x + 1) * self.scale_x)
                next_y = int((y + 1) * self.scale_y)
                cell_width = next_x - start_x
                cell_height = next_y - start_y

                if self.grid[y][x] == 15:
                    pr.draw_rectangle(start_x,
                                      start_y,
                                      cell_width,
                                      cell_height,
                                      WALL_COLOR)
                    continue

                if self.grid[y][x] & NORTH:
                    pr.draw_rectangle(start_x,
                                      start_y,
                                      cell_width,
                                      int(WALL_WIDTH),
                                      WALL_COLOR)
                if self.grid[y][x] & SOUTH:
                    pr.draw_rectangle(start_x,
                                      next_y,
                                      cell_width,
                                      int(WALL_WIDTH),
                                      WALL_COLOR)
                if self.grid[y][x] & EAST:
                    pr.draw_rectangle(next_x,
                                      start_y,
                                      int(WALL_WIDTH),
                                      cell_height + WALL_WIDTH,
                                      WALL_COLOR)

                if self.grid[y][x] & WEST:
                    pr.draw_rectangle(start_x,
                                      start_y,
                                      int(WALL_WIDTH),
                                      cell_height + WALL_WIDTH,
                                      WALL_COLOR)

    def create_window(self):
        pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT)
        pr.set_window_min_size(100, 100)
        width = pr.get_screen_width()
        height = pr.get_screen_height()
        pr.init_window(width, height, "Pac-Man")
        pr.set_target_fps(300)

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
        for entity in self.entities:
            if entity.box.collides_with(future_box_x):
                return True

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
        for entity in self.entities:
            if entity.box.collides_with(future_box_y):
                return True

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
        SPEED = 2.0
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

    def resize_event(self):
        old_scale_x = self.scale_x
        old_scale_y = self.scale_y

        self.screen_width = pr.get_screen_width() - 10
        self.screen_height = pr.get_screen_height() - 10

        if self.screen_width < self.maze_width or \
                self.screen_height < self.maze_height:
            return

        self.scale_x = self.screen_width / self.maze_width
        self.scale_y = self.screen_height / self.maze_height

        if old_scale_x > 0 and old_scale_y > 0:
            scale_ratio_x = self.scale_x / old_scale_x
            scale_ratio_y = self.scale_y / old_scale_y

            self.update_entity(self.player, scale_ratio_x, scale_ratio_y)

            for entity in self.entities:
                self.update_entity(entity, scale_ratio_x, scale_ratio_y)

        self.collision_boxs = self.create_collision_boxs()

    def draw_player(self):
        # draw hitbox for debugging

        pr.draw_circle(int(self.player.x),
                       int(self.player.y),
                       int(self.player.radius),
                       pr.YELLOW)
        """ pr.draw_rectangle(int(self.player.box.x),
                          int(self.player.box.y),
                          int(self.player.box.width),
                          int(self.player.box.height),
                          pr.WHITE) """

    def render_loop(self):
        SIZE_PACMAN = self.update_radius()
        # self.entities = [Player(538, 300, 20, self.scale_x, self.scale_y)]
        self.entities = []
        hitbox_w = self.scale_x - 2 * WALL_WIDTH
        hitbox_h = self.scale_y - 2 * WALL_WIDTH
        self.player = Player(self.scale_x // 2 + WALL_WIDTH - 2,
                             self.scale_y // 2 + WALL_WIDTH,
                             SIZE_PACMAN,
                             hitbox_w + 2, hitbox_h - 2, "rect")
        self.resize_event()
        while not pr.window_should_close():
            if pr.is_window_resized():
                self.resize_event()
            pr.begin_drawing()
            pr.clear_background(pr.BLACK)
            self.draw_maze()
            self.handle_events()
            # pr.draw_circle(400, 200, 5.0, pr.WHITE)
            self.draw_player()
            # pr.draw_circle(int(self.entities[0].x),
            #                int(self.entities[0].y),
            #                (self.entities[0].radius),
            #                pr.RED)

            pr.draw_text("Score: 42", 10, 10, 20, pr.RAYWHITE)

            pr.end_drawing()

    def close_window(self):
        pr.close_window()
