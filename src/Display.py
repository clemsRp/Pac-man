import pyray as pr
from .Constants import (NORTH, EAST, SOUTH, WEST)
from mazegenerator.mazegenerator import MazeGenerator
from .Physics import CollisionBox, CircleBox, RectangleBox
from .Player import Player

WALL_WIDTH = 3
WALL_COLOR = pr.BLUE


class Display:
    def __init__(self, maze: MazeGenerator):
        self.maze = maze
        self.grid = self.maze.maze
        self.maze_height = len(self.grid)
        self.maze_width = len(self.grid[0])
        self.screen_width = 3835
        self.screen_height = 2000
        self.scale_x = self.screen_width // self.maze_width
        self.scale_y = self.screen_height // self.maze_height
        self.collision_boxs = self.create_collision_boxs()

    def create_collision_boxs(self):
        boxes = [[[] for _ in range(self.maze_width)]
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
                            self.scale_y
                        )
                    )

                if cell & WEST:
                    boxes[y][x].append(
                        RectangleBox(
                            x * self.scale_x,
                            y * self.scale_y,
                            WALL_WIDTH,
                            self.scale_y
                        )
                    )

        return boxes

    def draw_maze(self):
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                if self.grid[y][x] & NORTH:
                    pr.draw_rectangle(x * self.scale_x,
                                      y * self.scale_y,
                                      self.scale_x,
                                      WALL_WIDTH,
                                      WALL_COLOR)
                if self.grid[y][x] & SOUTH:
                    pr.draw_rectangle(x * self.scale_x,
                                      (y + 1) * self.scale_y,
                                      self.scale_x,
                                      WALL_WIDTH,
                                      WALL_COLOR)
                if self.grid[y][x] & EAST:
                    pr.draw_rectangle((x + 1) * self.scale_x,
                                      y * self.scale_y,
                                      WALL_WIDTH,
                                      self.scale_y,
                                      WALL_COLOR)

                if self.grid[y][x] & WEST:
                    pr.draw_rectangle(
                        x * self.scale_x,
                        y * self.scale_y,
                        WALL_WIDTH,
                        self.scale_y,
                        WALL_COLOR)

    def create_window(self):
        # pr.set_config_flags(pr.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT)
        pr.init_window(self.screen_width, self.screen_height, "Pac-Man")
        pr.set_target_fps(120)

    def player_collision_events(self, new_x, new_y):
        base_y = self.player.y

        maze_pixels_x = self.maze_width * self.scale_x
        maze_pixels_y = self.maze_height * self.scale_y
        new_x = max(0, min(new_x, maze_pixels_x - 1))
        new_y = max(0, min(new_y, maze_pixels_y - 1))

        future_box_x = CircleBox(
            new_x,
            base_y,
            self.player.radius,
        )

        collision_x = False
        box_y = int(base_y // self.scale_y)

        if self.player_test.box.collides_with(future_box_x):
            collision_x = True

        for dy in [-1, 0, 1]:
            ny = box_y + dy
            if 0 <= ny < self.maze_height:
                box_x = new_x // self.scale_x
                for dx in [-1, 0, 1]:
                    nx = box_x + dx
                    if 0 <= nx < self.maze_width:
                        for box in self.collision_boxs[ny][nx]:
                            if future_box_x.collides_with(box):
                                collision_x = True
                                break

        if not collision_x:
            self.player.x = new_x

        future_box_y = CircleBox(
            self.player.x,
            new_y,
            self.player.radius,
        )


        collision_y = False
        box_x = int(self.player.x // self.scale_x)
        if self.player_test.box.collides_with(future_box_y):
            collision_y = True


        for dy in [-1, 0, 1]:
            ny = new_y // self.scale_y + dy
            if 0 <= ny < self.maze_height:
                for dx in [-1, 0, 1]:
                    nx = box_x + dx
                    if 0 <= nx < self.maze_width:
                        for box in self.collision_boxs[ny][nx]:
                            if future_box_y.collides_with(box):
                                collision_y = True
                                break

        if not collision_y:
            self.player.y = new_y
        self.player.update_collision_box()

    def handle_events(self):

        new_x = self.player.x
        new_y = self.player.y

        if pr.is_key_down(pr.KeyboardKey.KEY_RIGHT):
            new_x += 5
        if pr.is_key_down(pr.KeyboardKey.KEY_LEFT):
            new_x -= 5
        if pr.is_key_down(pr.KeyboardKey.KEY_UP):
            new_y -= 5
        if pr.is_key_down(pr.KeyboardKey.KEY_DOWN):
            new_y += 5

        self.player_collision_events(new_x, new_y)

    def render_loop(self):
        self.player_test = Player(538, 300, 20, 10)
        self.player = Player(538, 400, 20, 10)
        while not pr.window_should_close():

            pr.begin_drawing()
            pr.clear_background(pr.BLACK)
            self.draw_maze()
            self.handle_events()
            pr.draw_circle(400, 200, 5.0, pr.WHITE)
            pr.draw_circle(self.player.x,
                           self.player.y,
                           (self.player.radius),
                           pr.YELLOW)
            pr.draw_circle(self.player_test.x,
                           self.player_test.y,
                           (self.player_test.radius),
                           pr.RED)
            pr.draw_text("Score: 42", 10, 10, 20, pr.RAYWHITE)

            pr.end_drawing()

    def close_window(self):
        pr.close_window()
