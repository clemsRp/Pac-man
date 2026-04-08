NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

SPEED = 2.0

GAME_LOGIC = "gamelogic"
MAIN_MENU = "mainmenu"
EXIT = "exit"

DELTA: dict[int, tuple[int, int]] = {
    NORTH: (-1, 0),
    SOUTH: (1, 0),
    WEST: (0, -1),
    EAST: (0, 1),
}
