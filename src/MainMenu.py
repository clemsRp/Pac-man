from .Interfaces import Interface, Button
from .Constants import MAIN_MENU, GAME_LOGIC
from .Constants import EXIT, MAX_SCORES_SHOWN
from .Constants import PACMAN_SPRITE_QUALITY
from .Physics import CollisionBox, CircleBox
import pyray as pr
from src.parser import Parser
from src.Player import Player


class MainMenu(Interface):
    def __init__(self,
                 window_width: int,
                 window_height: int,
                 parser: Parser) -> None:
        super().__init__()
        self.window_width = window_width
        self.window_height = window_height
        self.background_pacman_speed = 5.0
        self.direction = "right"
        self.parser = parser
        self.scores = self.parser.get_scores().get("players", [])
        self.compute_scores()
        self.last_create_points_time: float = 0.0
        self.time_between_points_creation = 0.1
        button_width = int(0.25 * self.window_width)
        button_height = int(0.1 * self.window_height)

        center_x = (self.window_width - button_width) // 2
        center_y = (self.window_height - button_height) // 2
        start_button = Button(center_x,
                              int(center_y - button_height / 2),
                              button_width, button_height,
                              "Start Game",
                              pr.GREEN,
                              self.start_game)

        exit_button = Button(center_x,
                             int(center_y + button_height / 2 + 10),
                             button_width, button_height,
                             "Exit",
                             pr.RED,
                             self.exit_game)
        pac_size = 200
        self.background_pacman = Player(30, 30, pac_size)

        self.background_points: list[CollisionBox] = []

        self.reset_pacman()

        self.next_state = MAIN_MENU
        self.add_button(start_button)
        self.add_button(exit_button)

    def compute_scores(self) -> None:
        self.scores = self.parser.get_scores().get("players", [])
        self.scores = sorted(self.scores,
                             key=lambda x: x["score"],
                             reverse=True)

        # Compute the total score for each player
        player_totals: dict[str, int] = {}
        for p in self.scores:
            player_totals[p["pseudo"]] = player_totals.get(
                p["pseudo"], 0) + p["score"]

        self.best_player_name = "None"
        if len(player_totals) > 0:
            self.best_player_name = max(player_totals.keys(),
                                        key=lambda x: player_totals[x])

        if self.best_player_name != "None":
            self.best_player_score = player_totals[self.best_player_name]
        else:
            self.best_player_score = 0

    def reset_pacman(self):
        self.background_pacman.x = -self.background_pacman.radius
        self.background_pacman.y = self.background_pacman.radius
        self.direction = "right"
        self.background_points = self.create_points(
            self.background_pacman.y, self.window_width)

    def update_background_pacman(self):
        # Wait until points are fully animated before moving
        nb_points_to_show = int(
            (pr.get_time() -
             self.last_create_points_time) /
            self.time_between_points_creation)
        if nb_points_to_show < len(self.background_points):
            return

        direction = self.get_direciton_from_str(self.direction)
        self.background_pacman.x += direction * self.background_pacman_speed

        radius = self.background_pacman.radius
        line_height = radius * 2
        max_y = self.window_height - 2 * radius
        if (self.direction == "right" and
            self.background_pacman.x > self.window_width + 2 * radius) or \
                (self.direction == "left" and
                 self.background_pacman.x < -2 * radius):

            if self.background_pacman.y >= max_y:
                self.reset_pacman()
                return

            next_y = self.background_pacman.y + line_height
            if next_y > max_y:
                self.background_pacman.y = max_y
            else:
                self.background_pacman.y = next_y

            self.background_points = self.create_points(
                self.background_pacman.y,
                self.window_width)
            self.direction = "left" if self.direction == "right" else "right"
        self.background_pacman.update_collision_box()
        self.check_points_collision()

    def check_points_collision(self) -> None:
        if self.direction == "right":
            to_remove = [i for i in self.background_points if
                         i.center_x <= self.background_pacman.x]
        else:
            to_remove = [i for i in self.background_points if
                         i.center_x >= self.background_pacman.x]

        self.background_points = [i for i in self.background_points if
                                  i not in to_remove]

    def create_points(self, y: int, width: int) -> list[CollisionBox]:
        radius = self.background_pacman.radius
        cell_size = radius * 2
        nb_points = int(width // cell_size) + 2

        points: list[CollisionBox] = []
        for i in range(nb_points):
            cx = radius + i * cell_size
            cy = y
            points.append(CircleBox(cx, cy, radius))
        self.last_create_points_time = pr.get_time()
        return points

    def get_direciton_from_str(self, direc: str) -> int:
        direc = direc.lower()
        if direc == "right":
            return 1
        elif direc == "left":
            return -1
        else:
            raise ValueError("Invalid direction")

    def get_n_first_points(self, n: int, direction: str) -> list[CollisionBox]:
        if direction == "right":
            points = sorted(self.background_points,
                            key=lambda x: x.center_x)
        elif direction == "left":
            points = sorted(self.background_points,
                            key=lambda x: x.center_x, reverse=True)
        return points[:n]

    def draw_background_points(self):
        nb_points_to_show = int((pr.get_time() -
                                 self.last_create_points_time) /
                                self.time_between_points_creation)
        nb_points_to_show = min(nb_points_to_show, len(self.background_points))
        points = self.get_n_first_points(nb_points_to_show, self.direction)
        for point in points:
            cx = point.center_x
            cy = point.center_y
            pr.draw_circle(int(cx), int(cy), 23, pr.WHITE)

    def draw_background_pacman(self):
        nb_points_to_show = int(
            (pr.get_time() -
             self.last_create_points_time) /
            self.time_between_points_creation)
        if nb_points_to_show < len(self.background_points):
            return

        direction = self.direction
        pacman_len = len(self.assets["pacman"])
        if pacman_len > 0:
            index = int((pr.get_time() * 20)) % pacman_len
            texture = self.assets["pacman"][index]

            scale = self.background_pacman.radius / (PACMAN_SPRITE_QUALITY / 2)
            pos_x = float(self.background_pacman.x)
            pos_y = float(self.background_pacman.y)
            rotation = float(self.get_rotation_from_str(direction))

            pr.draw_texture_pro(
                texture,
                pr.Rectangle(0, 0,
                             texture.width, texture.height),
                pr.Rectangle(pos_x, pos_y,
                             texture.width * scale,
                             texture.height * scale),
                pr.Vector2((texture.width * scale) / 2.0,
                           (texture.height * scale) / 2.0),
                rotation,
                pr.WHITE
            )

    def start_game(self):
        self.next_state = GAME_LOGIC

    def update(self) -> str:
        self.update_background_pacman()
        self.draw_background_points()
        self.draw_background_pacman()
        super().update()
        self.draw_leaderboard()
        return self.next_state

    def draw_leaderboard(self):
        """Dessine le tableau des
        scores avec des dimensions et polices agrandies"""

        if len(self.scores) == 0:
            return

        font_size: int = int(0.025 * min([
            self.window_width,
            self.window_height
        ]))

        scores_menu_width = max([
            int(0.2 * self.window_width),
            pr.measure_text(
                " HIGH SCORES ", font_size + 20
            )
        ])
        scores_menu_height = int(
            0.12 * self.window_height + 100 +
            47 * len(self.scores[:MAX_SCORES_SHOWN])
        )
        menu_x = (self.window_width * 2 // 3)
        menu_y = int(
            (self.window_height - scores_menu_height) / 2
        )

        pr.draw_rectangle(
            menu_x - 20,
            menu_y - 20,
            scores_menu_width + 40,
            scores_menu_height,
            pr.fade(
                pr.DARKGRAY,
                0.5))
        pr.draw_rectangle_lines(
            menu_x - 20,
            menu_y - 20,
            scores_menu_width + 40,
            scores_menu_height,
            pr.GOLD)

        add_x: int = int(
            (
                scores_menu_width - pr.measure_text(
                    "HIGH SCORES", font_size + 20
                )
            ) / 2
        )

        pr.draw_text(
            "HIGH SCORES", menu_x + add_x, menu_y,
            font_size + 20, pr.GOLD
        )

        y_offset = menu_y + 80

        for i, player in enumerate(
            sorted(
                self.scores[:MAX_SCORES_SHOWN],
                key=lambda dico: dico["score"],
                reverse=True
            )
        ):
            pseudo = player["pseudo"]
            score = player["score"]

            del_x: int = scores_menu_width - pr.measure_text(
                f"{score}", font_size + 10
            )

            pr.draw_text(f"{i + 1}. {pseudo}", menu_x, y_offset,
                         font_size + 10, pr.WHITE)
            pr.draw_text(f"{score}", menu_x + del_x, y_offset,
                         font_size + 10, pr.YELLOW)

            y_offset += 45

        #  best player section

        separator_y = int(
            menu_y + scores_menu_height - 100
        )
        pr.draw_line(
            menu_x -
            20,
            separator_y,
            menu_x +
            scores_menu_width +
            20,
            separator_y,
            pr.GOLD)

        pr.draw_text(
            "Best Player :",
            menu_x,
            separator_y + 10,
            font_size,
            pr.ORANGE)

        del_x = scores_menu_width - pr.measure_text(
            f"{self.best_player_score}", font_size + 10
        )

        pr.draw_text(f"{self.best_player_name}", menu_x,
                     separator_y + font_size + 10, font_size + 10, pr.WHITE)
        pr.draw_text(f"{self.best_player_score}", menu_x +
                     del_x, separator_y + font_size + 10,
                     font_size + 10, pr.YELLOW)

    def exit_game(self):
        self.next_state = EXIT
