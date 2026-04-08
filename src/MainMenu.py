from .Interfaces import Interface, Button
from .Constants import MAIN_MENU, GAME_LOGIC, EXIT
import pyray as pr


class MainMenu(Interface):
    def __init__(self, window_width: int, window_height: int) -> None:
        self.window_width = window_width
        self.window_height = window_height
        super().__init__()
        start_button = Button(self.window_width // 2,
                              self.window_height // 2,
                              200, 50,
                              "Start Game",
                              pr.GREEN,
                              self.start_game)

        exit_button = Button(self.window_width // 2,
                             self.window_height // 2 + 100,
                             200, 50,
                             "Exit",
                             pr.RED,
                             self.exit_game)

        self.next_state = MAIN_MENU
        self.add_button(start_button)
        self.add_button(exit_button)

    def start_game(self):
        self.next_state = GAME_LOGIC

    def update(self) -> str:
        super().update()
        return self.next_state

    def exit_game(self):
        self.next_state = EXIT
