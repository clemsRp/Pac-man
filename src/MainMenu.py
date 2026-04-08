from .Interfaces import Interface, Button
from .Constants import MAIN_MENU, GAME_LOGIC
from .Constants import EXIT, MAX_SCORES_SHOWN
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
        self.background_pacman_speed = 3.0
        self.direction = "right"
        self.scores = parser.get_scores().get("players", [])
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
        self.background_pacman = Player(30, 30, 100)

        self.reset_pacman()

        self.next_state = MAIN_MENU
        self.add_button(start_button)
        self.add_button(exit_button)

    def reset_pacman(self):
        self.background_pacman.x = self.background_pacman.radius
        self.background_pacman.y = self.background_pacman.radius
        self.direction = "right"

    def update_background_pacman(self):
        direction = self.get_direciton_from_str(self.direction)
        self.background_pacman.x += direction[0] * self.background_pacman_speed

        radius = self.background_pacman.radius
        line_height = self.background_pacman.radius * 2

        if self.direction == "right" and self.background_pacman.x \
                > self.window_width + radius:
            self.direction = "left"
            self.background_pacman.y += line_height

        elif self.direction == "left" and self.background_pacman.x < -radius:
            self.direction = "right"
            self.background_pacman.y += line_height

        if self.background_pacman.y > self.window_height + radius:
            self.reset_pacman()

    def get_direciton_from_str(self, direc: str) -> tuple[int, int]:
        direc = direc.lower()
        if direc == "right":
            return (1, 0)
        elif direc == "left":
            return (-1, 0)
        elif direc == "up":
            return (0, -1)
        elif direc == "down":
            return (0, 1)
        else:
            raise ValueError("Invalid direction")

    def draw_background_pacman(self):
        pr.draw_circle(
            int(self.background_pacman.x),
            int(self.background_pacman.y),
            200,
            pr.YELLOW
        )

    def start_game(self):
        self.next_state = GAME_LOGIC

    def update(self) -> str:
        super().update()
        self.update_background_pacman()
        self.draw_background_pacman()
        self.draw_leaderboard()
        return self.next_state

    def draw_leaderboard(self):
        """Dessine le tableau des
        scores avec des dimensions et polices agrandies"""

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
