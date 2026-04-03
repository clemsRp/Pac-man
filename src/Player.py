from .Physics import CircleBox, RectangleBox, CollisionBox


class Player:
    def __init__(self, x: float = 60, y: float = 60,
                 radius: float = 30,
                 box_width: int = 60,
                 box_height: int = 60,
                 box_type: str = "circle"):
        self.x: float = x
        self.y: float = y
        self.radius = radius
        self.box: CollisionBox
        if box_type == "circle":
            self.box = CircleBox(x, y, radius)
        else:
            self.box = RectangleBox(x - box_width // 2,
                                    y - box_height // 2,
                                    box_width, box_height)

        self.direction: tuple[int, int] = (0, 0)

    def update_collision_box(self):
        if isinstance(self.box, CircleBox):
            self.box.center_x = self.x
            self.box.center_y = self.y
            self.box.radius = self.radius
        elif isinstance(self.box, RectangleBox):
            self.box.x = self.x - self.box.width // 2
            self.box.y = self.y - self.box.height // 2

        else:
            raise TypeError("Invalid Collision Box")
