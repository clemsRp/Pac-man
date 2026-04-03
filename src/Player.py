from .Physics import CircleBox


class Player:
    def __init__(self, x: int = 60, y: int = 60,
                 radius: int = 30, speed: int = 5):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.box: CircleBox = CircleBox(x, y, radius)

    def update_collision_box(self):
        if isinstance(self.box, CircleBox):
            self.box.center_x = self.x
            self.box.center_y = self.y
