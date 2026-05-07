from .Interfaces import Interface, Button
from .Constants import INSTRUCTIONS_MENU, MAIN_MENU
import pyray as pr


class InstructionsMenu(Interface):
    def __init__(self,
                 window_width: int,
                 window_height: int) -> None:
        super().__init__()
        self.next_state = INSTRUCTIONS_MENU
        self.window_width = window_width
        self.window_height = window_height

        self.menu_width = int(self.window_width // 1.5)
        self.menu_height = int(self.window_height // 1.5)
        self.menu_color = pr.fade(pr.BLACK, 0.8)
        self.menu_border_color = pr.Color(0, 180, 255, 255)
        self.background_color = pr.fade(pr.BLACK, 0.3)
        self.menu_x = (self.window_width - self.menu_width) // 2
        self.menu_y = (self.window_height - self.menu_height) // 2

        buttons_width = self.menu_width // 5
        buttons_height = self.menu_height // 15
        padding_bottom = int(self.menu_height * 0.05)

        back_button_x = int(self.menu_x + (self.menu_width - buttons_width) / 2)
        back_button_y = int(self.menu_y + self.menu_height - buttons_height - padding_bottom)

        back_button = Button(back_button_x,
                             back_button_y,
                             buttons_width,
                             buttons_height,
                             "Back",
                             pr.RED,
                             self.go_back)

        self.add_button(back_button)

    def go_back(self):
        self.next_state = MAIN_MENU

    def draw_background_color(self):
        pr.draw_rectangle(0,
                          0,
                          self.window_width,
                          self.window_height,
                          self.background_color)

    def draw_menu(self):
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

        font_size = int(self.menu_height * 0.05)
        title = "Instructions"
        title_width = pr.measure_text(title, font_size)
        pr.draw_text(title,
                     self.menu_x + (self.menu_width - title_width) // 2,
                     self.menu_y + int(self.menu_height * 0.05),
                     font_size,
                     pr.GOLD)

        instructions = [
            ("Up Arrow : Move Up", "pacman", 0),
            ("Down Arrow : Move Down", "pacman", 180),
            ("Left Arrow : Move Left", "pacman", -90),
            ("Right Arrow : Move Right", "pacman", 90),
            ("Left Click : Shoot", "ak47", 0),
            ("Escape : Quit Game", "skull", 0)
        ]

        start_y = self.menu_y + int(self.menu_height * 0.2)
        spacing = int(self.menu_height * 0.11)
        item_font_size = int(self.menu_height * 0.04)

        for i, (text, img_type, rotation) in enumerate(instructions):
            y_pos = start_y + i * spacing
            pr.draw_text(text,
                         self.menu_x + int(self.menu_width * 0.15),
                         y_pos + int(spacing * 0.3),
                         item_font_size,
                         pr.WHITE)

            img_center_x = self.menu_x + int(self.menu_width * 0.8)
            img_center_y = y_pos + spacing // 2

            if img_type == "pacman":
                texture = self.assets["pacman"][0]
                scale = (spacing * 0.8) / texture.width
                
                pr.draw_texture_pro(
                    texture,
                    pr.Rectangle(0, 0, texture.width, texture.height),
                    pr.Rectangle(img_center_x, img_center_y,
                                 texture.width * scale, texture.height * scale),
                    pr.Vector2((texture.width * scale) / 2.0, (texture.height * scale) / 2.0),
                    float(rotation),
                    pr.WHITE
                )
            elif img_type == "ak47":
                texture = self.assets["ak47"]
                scale = (spacing * 0.8) / texture.height
                
                pr.draw_texture_pro(
                    texture,
                    pr.Rectangle(0, 0, texture.width, texture.height),
                    pr.Rectangle(img_center_x, img_center_y,
                                 texture.width * scale, texture.height * scale),
                    pr.Vector2((texture.width * scale) / 2.0, (texture.height * scale) / 2.0),
                    float(rotation),
                    pr.WHITE
                )
            elif img_type == "skull":
                texture = self.assets["skull"]
                scale = (spacing * 0.8) / texture.height
                
                pr.draw_texture_pro(
                    texture,
                    pr.Rectangle(0, 0, texture.width, texture.height),
                    pr.Rectangle(img_center_x, img_center_y,
                                 texture.width * scale, texture.height * scale),
                    pr.Vector2((texture.width * scale) / 2.0, (texture.height * scale) / 2.0),
                    float(rotation),
                    pr.WHITE
                )


    def update(self) -> str:
        self.draw_background_color()
        self.draw_menu()
        super().update()
        result = self.next_state
        self.next_state = INSTRUCTIONS_MENU
        return result
