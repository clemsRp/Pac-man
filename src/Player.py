from .Physics import CollisionBox


class Player:
    def __init__(self, x: int = 60, y: int = 60,
                 radius: int = 30, speed: int = 5):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.box = CollisionBox(x, y, 2 * radius, 2 * radius)

    def update_collision_box(self):
        self.box.x = self.x
        self.box.y = self.y
        self.box.width = self.radius * 2
        self.box.height = self.radius * 2
