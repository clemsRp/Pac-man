from .Interfaces import Interface, Button
from .Constants import MAIN_MENU, GAME_LOGIC
from .Constants import EXIT, MAX_SCORES_SHOWN
from .Constants import PACMAN_SPRITE_QUALITY
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
        button_width = 600
        self.background_pacman_speed = 5.0
        self.direction = "right"
        self.scores = parser.get_scores().get("players", [])
        self.compute_scores()
        button_height = 120

        center_x = (self.window_width - button_width) // 2
        center_y = (self.window_height - button_height) // 2
        start_button = Button(center_x,
                              center_y,
                              button_width, button_height,
                              "Start Game",
                              pr.GREEN,
                              self.start_game)

        exit_button = Button(center_x,
                             center_y + button_height + 10,
                             button_width, button_height,
                             "Exit",
                             pr.RED,
                             self.exit_game)
        self.background_pacman = Player(30, 30, 200)

        self.reset_pacman()

        self.next_state = MAIN_MENU
        self.add_button(start_button)
        self.add_button(exit_button)

    def compute_scores(self) -> None:
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

    def update_background_pacman(self):
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

            self.direction = "left" if self.direction == "right" else "right"

    def get_direciton_from_str(self, direc: str) -> int:
        direc = direc.lower()
        if direc == "right":
            return 1
        elif direc == "left":
            return -1
        else:
            raise ValueError("Invalid direction")

    def draw_background_points(self):
        radius = self.background_pacman.radius
        cell_size = radius * 2
        num_cells = int(self.window_width // cell_size) + 2

        for i in range(num_cells):
            cx = radius + i * cell_size
            cy = self.background_pacman.y

            if self.direction == "right":
                if self.background_pacman.x >= cx:
                    continue
            elif self.direction == "left":
                if self.background_pacman.x <= cx:
                    continue

            pr.draw_circle(int(cx), int(cy), 13, pr.WHITE)

    def draw_background_pacman(self):
        direction = self.direction
        index = 2
        time = (pr.get_time() * 100) % 60
        if time > 20:
            index -= 1
        if time > 40:
            index -= 1

        texture = self.assets["pacman"][direction][index]

        scale = self.background_pacman.radius / (PACMAN_SPRITE_QUALITY / 2)
        pos_x = float(self.background_pacman.x -
                      self.background_pacman.radius)
        pos_y = float(self.background_pacman.y -
                      self.background_pacman.radius)

        pr.draw_texture_ex(
            texture,
            pr.Vector2(pos_x, pos_y),
            0.0,
            scale,
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

        scores_menu_width = 500
        scores_menu_height = 700
        menu_x = (self.window_width * 2 // 3) - (scores_menu_width // 2)
        menu_y = (self.window_height // 2) - 250

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

        pr.draw_text("HIGH SCORES", menu_x + 60, menu_y, 50, pr.GOLD)

        y_offset = menu_y + 80

        for i, player in enumerate(self.scores[:MAX_SCORES_SHOWN]):
            pseudo = player["pseudo"]
            score = player["score"]

            pr.draw_text(f"{i + 1}. {pseudo}", menu_x, y_offset, 40, pr.WHITE)
            pr.draw_text(f"{score}", menu_x + 320, y_offset,
                         40, pr.YELLOW)

            y_offset += 45

        #  best player section

        separator_y = menu_y + scores_menu_height - 130
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
            30,
            pr.ORANGE)
        pr.draw_text(f"{self.best_player_name}", menu_x,
                     separator_y + 40, 40, pr.WHITE)
        pr.draw_text(f"{self.best_player_score}", menu_x +
                     320, separator_y + 40, 40, pr.YELLOW)

    def exit_game(self):
        self.next_state = EXIT
