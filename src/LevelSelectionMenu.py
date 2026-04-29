from .Interfaces import Interface, Button
from .Constants import LEVEL_SELECTION, GAME_LOGIC, MAIN_MENU
import pyray as pr
from src.parser import Parser
from typing import Callable


class LevelSelectionMenu(Interface):
    def __init__(self,
                 window_width: int,
                 window_height: int,
                 parser: Parser) -> None:
        super().__init__()
        self.window_width = window_width
        self.window_height = window_height
        self.parser = parser
        self.next_state = LEVEL_SELECTION
        self.selected_level = None

        self.button_width = int(0.18 * self.window_width)
        self.button_height = int(0.05 * self.window_height)
        self.margin = int(0.02 * self.window_height)
        self.buttons_per_col = 5

        self.setup_buttons()

    def setup_buttons(self):
        """creates the buttons for the level selection menu"""
        self.buttons = []
        levels = self.parser.get_config().get("levels", [])

        nb_levels = len(levels)
        nb_cols = (nb_levels + self.buttons_per_col -
                   1) // self.buttons_per_col

        grid_width = nb_cols * self.button_width + (nb_cols - 1) * self.margin
        grid_height = self.buttons_per_col * self.button_height + \
            (self.buttons_per_col - 1) * self.margin

        start_x = (self.window_width - grid_width) // 2
        start_y = (self.window_height - grid_height) // 2

        self.panel_rect = pr.Rectangle(
            start_x - 2 * self.margin,
            start_y - 4 * self.margin,
            grid_width + 4 * self.margin,
            grid_height + 10 * self.margin)

        for i, level in enumerate(levels):
            col = i // self.buttons_per_col
            row = i % self.buttons_per_col

            x = start_x + col * (self.button_width + self.margin)
            y = start_y + row * (self.button_height + self.margin)

            def make_trigger(lvl) -> Callable:
                return lambda: self.select_level(lvl)

            btn = Button(x, y, self.button_width, self.button_height,
                         level["name"].upper(), pr.BLUE, make_trigger(level))
            self.add_button(btn)

        # Back button at the bottom of the panel
        back_btn = Button((self.window_width - self.button_width) // 2,
                          int(self.panel_rect.y + self.panel_rect.height -
                              self.button_height - int(self.margin * 1.5)),
                          self.button_width, self.button_height,
                          "BACK", pr.GRAY, self.go_back)
        self.add_button(back_btn)

    def select_level(self, level):
        """selects the level and goes to the game logic"""
        self.selected_level = level
        self.next_state = GAME_LOGIC

    def go_back(self):
        """goes back to the main menu"""
        self.next_state = MAIN_MENU

    def update(self) -> str:
        """main logic of the level selection menu"""
        pr.draw_rectangle_rec(self.panel_rect, pr.fade(pr.DARKGRAY, 0.8))
        pr.draw_rectangle_lines_ex(self.panel_rect, 3, pr.GOLD)

        title = "SELECT YOUR LEVEL"
        font_size = int(0.05 * self.window_height)
        title_x = (self.window_width - pr.measure_text(title, font_size)) // 2
        pr.draw_text(
            title, title_x, int(
                self.panel_rect.y + self.margin), font_size, pr.GOLD)

        super().update()
        state_to_return = self.next_state
        if self.next_state != LEVEL_SELECTION:
            self.next_state = LEVEL_SELECTION

        return state_to_return
