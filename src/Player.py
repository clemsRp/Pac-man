from .Physics import CircleBox, RectangleBox


class Player:
    def __init__(self, x: int = 60, y: int = 60,
                 radius: int = 30, speed: int = 5):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.box: CircleBox = CircleBox(x, y, radius)
        self.direction: tuple[int, int] = (0, 0)

    def update_collision_box(self):
        if isinstance(self.box, CircleBox):
            self.box.center_x = self.x
            self.box.center_y = self.y
        elif isinstance(self.box, RectangleBox):
            self.box.x = self.x
            self.box.y = self.y
            self.box.width = self.radius * 2
            self.box.height = self.radius * 2
