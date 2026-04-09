NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

SPEED = 2.0

GAME_LOGIC = "gamelogic"
GAME_OVER = "gameover"
MAIN_MENU = "mainmenu"
EXIT = "exit"
PAUSE_MENU = "pausemenu"

DELTA: dict[int, tuple[int, int]] = {
    NORTH: (-1, 0),
    SOUTH: (1, 0),
    WEST: (0, -1),
    EAST: (0, 1),
}
MAX_SCORES_SHOWN = 10
PACMAN_SPRITE_QUALITY = 512
