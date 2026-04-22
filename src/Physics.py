from abc import ABC, abstractmethod
from math import sin, cos, radians


class CollisionBox(ABC):
    @abstractmethod
    def __init__(self, x: float, y: float, width: float, height: float):
        ...

    @abstractmethod
    def collides_with(self, other: "CollisionBox") -> bool:
        ...

    @staticmethod
    def check_collision(box1: "CollisionBox", box2: "CollisionBox") -> bool:
        return box1.collides_with(box2)


class RectangleBox(CollisionBox):
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def collides_with(self, other: "CollisionBox") -> bool:
        if isinstance(other, CircleBox):
            return other.collides_with(self)
        elif isinstance(other, RectangleBox):
            return (
                self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y
            )
        else:
            raise TypeError("Unknown collision box type")


class CircleBox(CollisionBox):
    def __init__(self, center_x: float, center_y: float, radius: float):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

    def collides_with(self, other: "CollisionBox") -> bool:
        if isinstance(other, CircleBox):
            dist_sq = (self.center_x - other.center_x) ** 2 + \
                      (self.center_y - other.center_y) ** 2
            return dist_sq < (self.radius + other.radius) ** 2

        elif isinstance(other, RectangleBox):
            closest_x = max(other.x, min(self.center_x,
                                         other.x + other.width))
            closest_y = max(other.y, min(self.center_y,
                                         other.y + other.height))
            dx = self.center_x - closest_x
            dy = self.center_y - closest_y
            return (dx * dx + dy * dy) < (self.radius * self.radius)
        else:
            raise TypeError("Unknown collision box type")


class Bullet(CircleBox):
    def __init__(self, center_x: float, center_y: float,
                 radius: float, angle: float = 0.0, speed: float = 10.0):
        super().__init__(center_x, center_y, radius)
        self.angle = angle
        self.speed = speed

    def update(self) -> None:
        angle_rad = radians(self.angle)
        x = self.center_x + self.speed * cos(angle_rad)
        y = self.center_y + self.speed * sin(angle_rad)

        self.center_x = x
        self.center_y = y
