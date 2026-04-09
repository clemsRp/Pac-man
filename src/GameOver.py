
import pyray as pr
from .Interfaces import Interface
from .Constants import GAME_OVER

FONT_SIZE = 15


class GameOver(Interface):

    def __init__(
                self,
                screen_width: int,
                screen_height: int
            ):
        self.pseudo = ""
        self.screen_width = screen_width
        self.screen_height = screen_height

    def set_assets(self, assets: dict):
        super().set_assets(assets)

    def update(self):
        font_size = 200
        center_title = pr.measure_text(
            "GAME   VER", font_size
        )
        pr.draw_text(
            "GAME   VER",
            int(
                self.screen_width / 2 -
                center_title / 2
            ),
            int(
                self.screen_height / 3 -
                font_size / 2
            ),
            font_size, pr.RED
        )

        pr.draw_texture(
            self.assets["skull"],
            int(
                self.screen_width / 2 -
                center_title / 2 + 575
            ),
            int(
                self.screen_height / 3 -
                font_size / 1.25
            ),
            pr.WHITE
        )

        return GAME_OVER
