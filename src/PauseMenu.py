from .Interfaces import Interface, Button, Checkbox, Spinner
from .Constants import (PAUSE_MENU,
                        MAIN_MENU,
                        GAME_LOGIC,
                        INVINCIBILITY,
                        REMOVE_COLLISIONS,
                        LEVEL_SKIP,
                        FREEZE_GHOSTS,
                        BONUS_LIVES,
                        AK47_ALWAYS_ACTIVE,
                        NB_BOUNCES)
import pyray as pr
import time


class PauseMenu(Interface):
    def __init__(self,
                 scores: dict,
                 window_width: int,
                 window_height: int) -> None:
        """
        Initialize the Pause Menu interface.

        Args:
            scores
                dict: The current high scores dictionary.
            window_width
                int: The width of the game window.
            window_height
                int: The height of the game window.
        """
        super().__init__()
        self.next_state = PAUSE_MENU
        self.window_width = window_width
        self.window_height = window_height
        self.scores = scores
        PAUSE_MENU_FADE = 0.8

        self.current_score = 0
        self.menu_width = int(self.window_width // 1.5)
        self.menu_height = int(self.window_height // 1.5)
        self.menu_color = pr.fade(pr.BLACK, PAUSE_MENU_FADE)
        self.menu_border_color = pr.Color(0, 180, 255, 255)
        self.background_color = pr.fade(pr.BLACK, 0.3)
        self.menu_x = (self.window_width - self.menu_width) // 2
        self.menu_y = (self.window_height - self.menu_height) // 2

        buttons_width = self.menu_width // 5
        buttons_height = self.menu_height // 15
        padding_bottom = int(self.menu_height * 0.05)

        resume_button_x = int(
            self.menu_x + (self.menu_width / 2 - buttons_width)) - 10

        resume_button_y = int(self.menu_y +
                              self.menu_height -
                              buttons_height -
                              padding_bottom)
        return_to_main_menu_button_x = int(self.menu_x +
                                           (self.menu_width / 2)) + 10
        return_to_main_menu_button_y = int(self.menu_y +
                                           self.menu_height -
                                           buttons_height -
                                           padding_bottom)
        return_to_main_menu_button = Button(return_to_main_menu_button_x,
                                            return_to_main_menu_button_y,
                                            buttons_width,
                                            buttons_height,
                                            "Return to Main Menu",
                                            self.return_to_main_menu)
        self.add_button(return_to_main_menu_button)

        resume_button = Button(resume_button_x,
                               resume_button_y,
                               buttons_width,
                               buttons_height,
                               "Resume Game",
                               self.resume_game)

        self.cheats_gui: dict[str, Checkbox | Spinner] = {}
        self.cheats: dict[str, bool | int] = {INVINCIBILITY: False,
                                              REMOVE_COLLISIONS: False,
                                              LEVEL_SKIP: False,
                                              FREEZE_GHOSTS: False,
                                              AK47_ALWAYS_ACTIVE: False,
                                              BONUS_LIVES: 0,
                                              NB_BOUNCES: 3}
        self.add_button(resume_button)

        self.start_time: float = time.time()

        checkbox_texts = [
            INVINCIBILITY,
            REMOVE_COLLISIONS,
            LEVEL_SKIP,
            FREEZE_GHOSTS,
            AK47_ALWAYS_ACTIVE
        ]

        spinner_texts = [
            (BONUS_LIVES, 0, 100, 0),
            (NB_BOUNCES, 1, 99999, 3)
        ]

        checkbox_size = int(self.menu_height * 0.05)
        start_y = int(self.menu_y + self.menu_height * 0.15)
        box_x = int(self.menu_x + self.menu_width - self.menu_width * 0.1)

        for text in checkbox_texts:
            checkbox_sep_size = checkbox_size + int(self.menu_height * 0.02)
            cb = Checkbox(box_x,
                          start_y,
                          checkbox_size,
                          text,
                          pr.RAYWHITE)
            self.add_checkbox(cb, text)
            start_y += checkbox_sep_size

        spinner_width = int(self.menu_width * 0.07)
        spinner_height = int(self.menu_height * 0.05)
        box_x = int(
            self.menu_x +
            self.menu_width -
            spinner_width -
            self.menu_width *
            0.05)
        for text, min_val, max_val, default in spinner_texts:
            spinner_sep_size = spinner_height + int(self.menu_height * 0.02)

            sp = Spinner(box_x,
                         start_y,
                         spinner_width,
                         spinner_height,
                         text,
                         min_val,
                         max_val,
                         default,
                         pr.RAYWHITE)
            self.add_spinner(sp, text)
            start_y += spinner_sep_size

        # Calculate bounding box for the cheats frame
        max_cb_width = max(pr.measure_text(t, checkbox_size) for t
                           in checkbox_texts)
        max_sp_width = max(pr.measure_text(t[0], spinner_height) for t
                           in spinner_texts)

        cb_left = int(self.menu_x + self.menu_width - self.menu_width *
                      0.1) - max_cb_width - int(self.menu_width * 0.01)
        sp_left = (
            int(self.menu_x + self.menu_width -
                spinner_width - self.menu_width * 0.05)
            - max_sp_width - int(self.menu_width * 0.01)
        )

        left_edge = min(cb_left, sp_left) - int(self.menu_width * 0.03)
        right_edge = int(
            self.menu_x +
            self.menu_width -
            self.menu_width *
            0.02)

        frame_x = left_edge
        frame_y = int(self.menu_y + self.menu_height * 0.1)
        frame_width = right_edge - left_edge
        frame_height = start_y - frame_y

        self.cheats_frame_rect = pr.Rectangle(frame_x,
                                              frame_y,
                                              frame_width,
                                              frame_height)
        self.cheats_text_x = frame_x + int(self.menu_width * 0.02)
        self.cheats_text_y = frame_y - int(self.menu_height * 0.04)
        self.cheats_font_size = int(self.menu_height * 0.04)

    def return_to_main_menu(self) -> None:
        """
        Return to the main menu.

        Returns:
            None: No return value.
        """
        self.next_state = MAIN_MENU

    def update_score(self, score: int) -> None:
        """
        Update the current score displayed in the menu.

        Args:
            score
                int: The player's current score.

        Returns:
            None: No return value.
        """
        self.current_score = score

    def get_next_score(self) -> tuple[int, str]:
        """
        Determine the next highest score to beat based on the
        current score.

        Returns:
            tuple[int, str]: The next score and the name of the player who
                holds it.
        """
        scores = self.scores["players"]
        # print(scores)
        scores = [
            s for s in sorted(
                scores,
                key=lambda x: x["score"]) if s["score"] >= self.current_score]
        if not scores:
            return self.current_score, "You"
        next_score = scores[0]["score"]
        next_score_name = scores[0]["pseudo"]

        return next_score, next_score_name

    def draw_score(self) -> None:
        """
        Draw the current score and the next score to beat on the screen.

        Returns:
            None: No return value.
        """
        score = self.current_score
        # print(self.scores)
        score_pos_x = self.menu_x + int(0.1 * self.menu_width)
        score_pos_y = self.menu_y + int(0.1 * self.menu_height)

        score_text = "Score: "
        label_width = pr.measure_text(score_text, self.cheats_font_size)
        pr.draw_text(
            score_text,
            score_pos_x,
            score_pos_y,
            self.cheats_font_size,
            pr.WHITE
        )
        pr.draw_text(
            f"{score}",
            score_pos_x + label_width,
            score_pos_y,
            self.cheats_font_size,
            pr.YELLOW
        )

        next_score_x = score_pos_x
        next_score_y = score_pos_y + int(0.05 * self.menu_height)
        next_score, next_score_name = self.get_next_score()

        next_label = "next person to beat: "
        next_label_width = pr.measure_text(next_label, self.cheats_font_size)
        pr.draw_text(
            next_label,
            next_score_x,
            next_score_y,
            self.cheats_font_size,
            pr.WHITE
        )
        pr.draw_text(
            f"{next_score_name} ({next_score})",
            next_score_x + next_label_width,
            next_score_y,
            self.cheats_font_size,
            pr.SKYBLUE
        )

    def add_checkbox(self, checkbox: Checkbox,
                     checkbox_name: str = "") -> None:
        """
        Add a checkbox to the pause menu cheats dictionary.

        Args:
            checkbox
                Checkbox: The checkbox UI element.
            checkbox_name
                str: The name associated with the checkbox.

        Returns:
            None: No return value.
        """
        self.cheats_gui[checkbox_name] = checkbox
        super().add_checkbox(checkbox)

    def add_spinner(self, spinner: Spinner,
                    spinner_name: str = "") -> None:
        """
        Add a spinner to the pause menu cheats dictionary.

        Args:
            spinner
                Spinner: The spinner UI element.
            spinner_name
                str: The name associated with the spinner.

        Returns:
            None: No return value.
        """
        self.cheats_gui[spinner_name] = spinner
        super().add_spinner(spinner)

    def resume_game(self) -> None:
        """
        Resume the game state.

        Returns:
            None: No return value.
        """
        self.next_state = GAME_LOGIC

    def draw_background_color(self) -> None:
        """
        Draw the semi-transparent background color over the game.

        Returns:
            None: No return value.
        """
        pr.draw_rectangle(0,
                          0,
                          self.window_width,
                          self.window_height,
                          self.background_color)

    def draw_pause_menu(self) -> None:
        """
        Draw the pause menu panel, border, and the cheats frame.

        Returns:
            None: No return value.
        """
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
                     self.cheats_font_size,
                     pr.RAYWHITE)

    def update_cheats(self) -> None:
        """
        Update the cheats dictionary based on the current states of
        the UI elements.

        Returns:
            None: No return value.
        """
        for cheat_name, gui_element in self.cheats_gui.items():
            if isinstance(gui_element, Checkbox):
                self.cheats[cheat_name] = gui_element.checked
            elif isinstance(gui_element, Spinner):
                self.cheats[cheat_name] = gui_element.value

    def draw_ghost(self) -> None:
        """
        Draw an animated ghost texture on the pause menu.

        Returns:
            None: No return value.
        """
        ghost_x = self.menu_x + int(self.menu_width * 0.1)
        ghost_y = self.menu_y + int(self.menu_height * 0.3)
        index: int = int(((time.time() - self.start_time) * 6) % 3)
        scale = 4.5
        pr.draw_texture_ex(
            self.assets["pause_menu"][int(index)],
            pr.Vector2(ghost_x, ghost_y),
            0.0,
            scale,
            pr.WHITE
        )

    def update(self) -> str:
        """
        Update the logic and draw elements of the pause menu.

        Returns:
            str: The next state of the game loop.
        """
        self.draw_background_color()
        self.draw_pause_menu()
        self.draw_score()
        self.draw_ghost()
        super().update()
        self.update_cheats()
        result = self.next_state
        self.next_state = PAUSE_MENU
        return result
