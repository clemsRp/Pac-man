from .Physics import CircleBox, RectangleBox


class Player:
    def __init__(self, x: float = 60, y: float = 60,
                 radius: float = 30,
                 box_width: int = 60,
                 box_height: int = 60):
        """
        Initialize the Player instance.

        Args:
            x
                float: The initial x coordinate of the player.
            y
                float: The initial y coordinate of the player.
            radius
                float: The radius of the player's circular hitbox.
            box_width
                int: The width of the player's rectangular collision box.
            box_height
                int: The height of the player's rectangular collision box.
        """
        self.x: float = x
        self.y: float = y
        self.radius = radius
        self.box: RectangleBox
        self.hitbox = CircleBox(x, y, radius)
        self.box = RectangleBox(
            x - box_width // 2,
            y - box_height // 2,
            box_width,
            box_height
        )

        self.direction: tuple[int, int] = (0, 0)
        self.try_direction: tuple[int, int] = (0, 0)

    def update_collision_box(self) -> None:
        """
        Update the position of the player's collision boxes based on
        its coordinates.

        Returns:
            None: No return value.
        """
        # update circle box
        self.hitbox.center_x = self.x
        self.hitbox.center_y = self.y
        self.hitbox.radius = self.radius

        # update rectangle box
        self.box.x = self.x - self.box.width // 2
        self.box.y = self.y - self.box.height // 2
