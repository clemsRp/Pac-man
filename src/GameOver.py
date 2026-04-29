
import time
import json
import pyray as pr
from .Interfaces import Interface, Button
from .Constants import GAME_OVER, MAIN_MENU

FONT_SIZE = 50


class GameOver(Interface):

    def __init__(
                self,
                screen_width: int,
                screen_height: int,
                config: dict,
                scores: dict
            ):
        super().__init__()

        global FONT_SIZE
        FONT_SIZE = int(0.06 * min([
            screen_width,
            screen_height
        ]))

        self.state = GAME_OVER

        self.score = 0
        self.pseudo = ""

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.config: dict = config
        self.scores: dict = scores

        self.all_scores = {
            player["score"] for player in scores["players"]
        }
        self.all_scores.add(self.score)
        self.all_scores = sorted(list(self.all_scores), reverse=True)

        self.rank = self.all_scores.index(self.score) + 1

        self.last_key_time: float = 0
        self.cursor: bool = False

        input_width: int = max([
            int(0.1 * self.screen_width),
            int(pr.measure_text(
                " " * 18, FONT_SIZE
            ))
        ])
        btn_width: int = int(input_width / 2)

        save_button: Button = Button(
            int(0.5 * (self.screen_width - input_width)),
            int(2 / 3 * self.screen_height + 2.2 * FONT_SIZE),
            btn_width - 5,
            2 * FONT_SIZE,
            "Save", pr.RED, self.save_data
        )
        skip_button: Button = Button(
            int(0.5 * self.screen_width),
            int(2 / 3 * self.screen_height + 2.2 * FONT_SIZE),
            btn_width,
            2 * FONT_SIZE,
            "Skip", pr.RED, self.skip
        )

        self.add_button(save_button)
        self.add_button(skip_button)

    def save_data(self):
        if self.pseudo == "":
            return
        self.scores["players"].append({
            "pseudo": self.pseudo,
            "score": self.score
        })

        try:
            with open(self.config["highscore_filename"], 'w') as f:
                output = "[\n"
                content: str = json.dumps(self.scores, indent=4)
                for line in content.split("\n"):
                    output += f"\t{line}\n"
                output += "]"

                f.write(output)

        except Exception as e:
            print(e)

        self.state = MAIN_MENU

    def skip(self):
        self.state = MAIN_MENU

    def set_assets(self, assets: dict):
        super().set_assets(assets)

    def update_pseudo(self):
        key = pr.get_char_pressed()

        while key > 0:
            if 32 <= key <= 125:
                lettre = chr(key)
                if (lettre.isalpha() or lettre.isspace()) and \
                        len(self.pseudo) < 10:
                    self.pseudo += lettre
                    self.last_key_time = time.time()

            key = pr.get_char_pressed()

        if pr.is_key_pressed_repeat(pr.KEY_BACKSPACE) or \
                pr.is_key_pressed(pr.KEY_BACKSPACE):
            self.last_key_time = time.time()
            self.pseudo = self.pseudo[:-1]

        if pr.is_key_pressed(pr.KEY_ENTER):
            self.save_data()

    def draw_game_over(self):
        font_size = int(3.5 * FONT_SIZE)
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

        texture = self.assets["skull"]
        scale = font_size / texture.width

        pr.draw_texture_pro(
            texture,
            pr.Rectangle(
                0, 0,
                texture.width,
                texture.height
            ),
            pr.Rectangle(
                int(
                    self.screen_width / 2 -
                    center_title / 2 + int(0.1 * font_size) +
                    pr.measure_text(
                        "GAME ", int(font_size * 0.92)
                    )
                ),
                int(
                    self.screen_height / 3 -
                    font_size / 2 -
                    (texture.height * scale - font_size) / 2
                ),
                int(texture.width * scale),
                int(texture.height * scale)
            ),
            pr.Vector2(0, 0),
            0, pr.WHITE
        )

    def draw_score_rank(self) -> None:
        text1: str = f"Score: {self.score}, Rank: {self.rank}"
        center_text1 = pr.measure_text(
            text1, FONT_SIZE
        )

        pr.draw_text(
            text1,
            int(0.5 * self.screen_width - center_text1 / 2),
            int(0.5 * self.screen_height - 0.7 * FONT_SIZE),
            FONT_SIZE,
            pr.WHITE
        )

        percent_rank = round(
            self.rank / len(self.all_scores) * 100,
            1
        )

        text2: str = f"Top {percent_rank}% best score"
        center_text2 = pr.measure_text(
            text2, FONT_SIZE
        )

        pr.draw_text(
            text2,
            int(0.5 * self.screen_width - center_text2 / 2),
            int(0.5 * self.screen_height + 0.7 * FONT_SIZE),
            FONT_SIZE,
            pr.WHITE
        )

    def draw_pseudo(self) -> None:
        # draw box

        border: int = max(1, int(FONT_SIZE * 0.1))

        input_width: int = max([
            int(0.1 * self.screen_width),
            int(pr.measure_text(
                " " * 18, FONT_SIZE
            ))
        ])

        pr.draw_rectangle(
            int(0.5 * (self.screen_width - input_width)),
            int(2 / 3 * self.screen_height),
            input_width,
            2 * FONT_SIZE,
            pr.RED
        )

        pr.draw_rectangle(
            int(0.5 * (self.screen_width - input_width) + border),
            int(2 / 3 * self.screen_height + border),
            input_width - 2 * border,
            2 * (FONT_SIZE - border),
            pr.WHITE
        )

        center_pseudo: int = pr.measure_text(
            self.pseudo, FONT_SIZE
        )

        start_pseudo_x: int = int(
            0.45 * self.screen_width +
            0.05 * self.screen_width -
            center_pseudo / 2
        )
        start_pseudo_y: int = int(
                2 / 3 * self.screen_height +
                FONT_SIZE / 2
            )

        # draw pseudo
        pr.draw_text(
            self.pseudo,
            start_pseudo_x,
            start_pseudo_y,
            FONT_SIZE,
            pr.BLACK
        )

        if pr.get_time() % 2 <= 1 or self.cursor:
            pr.draw_rectangle(
                start_pseudo_x + center_pseudo + max(1, int(FONT_SIZE * 0.1)),
                start_pseudo_y,
                max(1, int(FONT_SIZE * 0.1)), FONT_SIZE, pr.BLACK
            )

    def update(self):
        if time.time() - self.last_key_time <= 0.7:
            self.cursor = True
        else:
            self.cursor = False

        self.update_pseudo()
        self.draw_game_over()
        self.draw_score_rank()
        self.draw_pseudo()

        super().update()

        return self.state
