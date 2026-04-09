from .Interfaces import Interface, Button, Checkbox
from .Constants import PAUSE_MENU, GAME_LOGIC
import pyray as pr


class PauseMenu(Interface):
    def __init__(self,
                 window_width: int,
                 window_height: int) -> None:
        super().__init__()
        self.next_state = PAUSE_MENU
        self.window_width = window_width
        self.window_height = window_height
        PAUSE_MENU_FADE = 0.8

        self.menu_width = int(self.window_width // 1.5)
        self.menu_height = int(self.window_height // 1.5)
        self.menu_color = pr.fade(pr.BLACK, PAUSE_MENU_FADE)
        self.menu_border_color = pr.Color(0, 180, 255, 255)
        self.background_color = pr.fade(pr.BLACK, 0.3)
        self.menu_x = (self.window_width - self.menu_width) // 2
        self.menu_y = (self.window_height - self.menu_height) // 2

        buttons_width = self.menu_width // 5
        buttons_height = self.menu_height // 15
        padding_bottom = 30

        resume_button_x = int(self.menu_x + (self.menu_width -
                                             buttons_width) / 2)

        resume_button_y = int(self.menu_y +
                              self.menu_height -
                              buttons_height -
                              padding_bottom)
        resume_button = Button(resume_button_x,
                               resume_button_y,
                               buttons_width,
                               buttons_height,
                               "Resume Game",
                               pr.RED,
                               self.resume_game)
        self.add_button(resume_button)

        checkbox_texts = [
            "Invincibility",
            "Level skip",
            "Ghost freeze",
            "Extra lives",
            "Remove collisions"
        ]
        
        checkbox_size = 50
        start_y = int(self.menu_y + 100)
        box_x = int(self.menu_x + self.menu_width - 100)
        
        for i, text in enumerate(checkbox_texts):
            checkbox_sep_size = checkbox_size + 30
            cb = Checkbox(box_x, 
                          start_y + i * checkbox_sep_size, 
                          checkbox_size, 
                          text, 
                          pr.RAYWHITE)
            self.add_checkbox(cb)

    def resume_game(self):
        self.next_state = GAME_LOGIC

    def draw_background_color(self):
        pr.draw_rectangle(0,
                          0,
                          self.window_width,
                          self.window_height,
                          self.background_color)

    def draw_pause_menu(self):
        pr.draw_rectangle(self.menu_x,
                          self.menu_y,
                          self.menu_width,
                          self.menu_height,
                          self.menu_color)

        pr.draw_rectangle_lines_ex(
            pr.Rectangle(self.menu_x,
                         self.menu_y,
                         self.menu_width,
                         self.menu_height),
            4,
            self.menu_border_color
        )

    def update(self) -> str:
        self.draw_background_color()
        self.draw_pause_menu()
        super().update()
        result = self.next_state
        self.next_state = PAUSE_MENU
        return result
