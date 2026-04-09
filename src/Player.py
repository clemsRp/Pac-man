from .Physics import CircleBox, RectangleBox, CollisionBox


class Player:
    def __init__(self, x: float = 60, y: float = 60,
                 radius: float = 30,
                 box_width: int = 60,
                 box_height: int = 60):
        self.x: float = x
        self.y: float = y
        self.radius = radius
        self.box: CollisionBox
        self.hitbox = CircleBox(x, y, radius)
        self.box = RectangleBox(
            x - box_width // 2,
            y - box_height // 2,
            box_width,
            box_height
        )

        self.direction: tuple[int, int] = (0, 0)
        self.try_direction: tuple[int, int] = (0, 0)

    def update_collision_box(self):
        # update circle box
        self.hitbox.center_x = self.x
        self.hitbox.center_y = self.y
        self.hitbox.radius = self.radius

        # update rectangle box
        self.box.x = self.x - self.box.width // 2
        self.box.y = self.y - self.box.height // 2
