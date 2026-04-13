from .Interfaces import Interface, Button, Checkbox, Spinner
from .Constants import (PAUSE_MENU,
                        GAME_LOGIC,
                        INVINCIBILITY,
                        REMOVE_COLLISIONS,
                        LEVEL_SKIP,
                        FREEZE_GHOSTS,
                        BONUS_LIVES)
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

        self.cheats_gui: dict[str, Checkbox | Spinner] = {}
        self.cheats: dict[str, bool | int] = {INVINCIBILITY: False,
                                              REMOVE_COLLISIONS: False,
                                              LEVEL_SKIP: False,
                                              FREEZE_GHOSTS: False,
                                              BONUS_LIVES: 0}
        self.add_button(resume_button)

        checkbox_texts = [
            INVINCIBILITY,
            REMOVE_COLLISIONS,
            LEVEL_SKIP,
            FREEZE_GHOSTS,
        ]

        spinner_texts = [
            BONUS_LIVES
        ]

        checkbox_size = 50
        start_y = int(self.menu_y + 100)
        box_x = int(self.menu_x + self.menu_width - 100)

        for _, text in enumerate(checkbox_texts):
            checkbox_sep_size = checkbox_size + 30
            cb = Checkbox(box_x,
                          start_y,
                          checkbox_size,
                          text,
                          pr.RAYWHITE)
            self.add_checkbox(cb, text)
            start_y += checkbox_sep_size

        spinner_width = 130
        spinner_height = 50
        box_x = int(self.menu_x + self.menu_width - spinner_width - 50)
        for _, text in enumerate(spinner_texts):
            spinner_sep_size = spinner_height + 30
            sp = Spinner(box_x,
                         start_y,
                         spinner_width,
                         spinner_height,
                         text,
                         0,
                         100,
                         0,
                         pr.RAYWHITE)
            self.add_spinner(sp, text)
            start_y += spinner_sep_size

        # Calculate bounding box for the cheats frame
        max_cb_width = max(pr.measure_text(t, checkbox_size) for t
                           in checkbox_texts)
        max_sp_width = max(pr.measure_text(t, spinner_height) for t
                           in spinner_texts)

        cb_left = int(self.menu_x + self.menu_width - 100) - max_cb_width - 10
        sp_left = (
            int(self.menu_x + self.menu_width - spinner_width - 50)
            - max_sp_width - 10
        )

        left_edge = min(cb_left, sp_left) - 30
        right_edge = int(self.menu_x + self.menu_width - 20)

        frame_x = left_edge
        frame_y = int(self.menu_y + 70)
        frame_width = right_edge - left_edge
        frame_height = start_y - frame_y

        self.cheats_frame_rect = pr.Rectangle(frame_x,
                                              frame_y,
                                              frame_width,
                                              frame_height)
        self.cheats_text_x = frame_x + 20
        self.cheats_text_y = frame_y - 45

    def add_checkbox(self, checkbox: Checkbox,
                     checkbox_name: str = "") -> None:
        self.cheats_gui[checkbox_name] = checkbox
        super().add_checkbox(checkbox)

    def add_spinner(self, spinner: Spinner,
                    spinner_name: str = "") -> None:
        self.cheats_gui[spinner_name] = spinner
        super().add_spinner(spinner)

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

        # Draw cheats frame and "Cheats" text
        pr.draw_rectangle_lines_ex(self.cheats_frame_rect, 3, pr.RAYWHITE)
        pr.draw_text("Cheats",
                     int(self.cheats_text_x),
                     int(self.cheats_text_y),
                     40,
                     pr.RAYWHITE)

    def update_cheats(self):
        for cheat_name, gui_element in self.cheats_gui.items():
            if isinstance(gui_element, Checkbox):
                self.cheats[cheat_name] = gui_element.checked
            elif isinstance(gui_element, Spinner):
                self.cheats[cheat_name] = gui_element.value

    def update(self) -> str:
        self.draw_background_color()
        self.draw_pause_menu()
        super().update()
        self.update_cheats()
        result = self.next_state
        self.next_state = PAUSE_MENU
        return result
