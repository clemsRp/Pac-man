from abc import ABC, abstractmethod
from math import sin, cos, radians


class CollisionBox(ABC):
    """
    Abstract base class for all collision boxes.
    """

    @abstractmethod
    def __init__(self, x: float, y: float, width: float, height: float):
        """
        Initialize the collision box.

        Args:
            x
                float: The x coordinate.
            y
                float: The y coordinate.
            width
                float: The width of the box.
            height
                float: The height of the box.
        """
        ...

    @abstractmethod
    def collides_with(self, other: "CollisionBox") -> bool:
        """
        Check if this collision box collides with another.

        Args:
            other
                CollisionBox: The other collision box to check against.

        Returns:
            bool: True if they collide, False otherwise.
        """
        ...

    @staticmethod
    def check_collision(box1: "CollisionBox", box2: "CollisionBox") -> bool:
        """
        Static method to check collision between two boxes.

        Args:
            box1
                CollisionBox: The first collision box.
            box2
                CollisionBox: The second collision box.

        Returns:
            bool: True if they collide, False otherwise.
        """
        return box1.collides_with(box2)


class RectangleBox(CollisionBox):
    """
    A rectangular collision box.
    """

    def __init__(self, x: float, y: float, width: float, height: float):
        """
        Initialize the RectangleBox.

        Args:
            x
                float: The x coordinate of the top-left corner.
            y
                float: The y coordinate of the top-left corner.
            width
                float: The width of the rectangle.
            height
                float: The height of the rectangle.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def collides_with(self, other: "CollisionBox") -> bool:
        """
        Check if this rectangle collides with another collision box.

        Args:
            other
                CollisionBox: The other collision box.

        Returns:
            bool: True if they collide, False otherwise.
        """
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
    """
    A circular collision box.
    """

    def __init__(self, center_x: float, center_y: float, radius: float):
        """
        Initialize the CircleBox.

        Args:
            center_x
                float: The x coordinate of the center.
            center_y
                float: The y coordinate of the center.
            radius
                float: The radius of the circle.
        """
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

    def collides_with(self, other: "CollisionBox") -> bool:
        """
        Check if this circle collides with another collision box.

        Args:
            other
                CollisionBox: The other collision box.

        Returns:
            bool: True if they collide, False otherwise.
        """
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
    """
    A bullet entity represented as a circular collision box.
    """

    def __init__(self, center_x: float, center_y: float,
                 radius: float,
                 angle: float = 0.0,
                 speed: float = 10.0,
                 bounces: int = 3):
        """
        Initialize the Bullet.

        Args:
            center_x
                float: The x coordinate of the bullet's center.
            center_y
                float: The y coordinate of the bullet's center.
            radius
                float: The radius of the bullet.
            angle
                float: The angle of movement in degrees.
            speed
                float: The speed of the bullet.
            bounces
                int: The remaining number of bounces before disappearing.
        """
        super().__init__(center_x, center_y, radius)
        self.angle = radians(angle)
        self.speed = speed
        self.remaining_bounces = bounces

    def update(self) -> None:
        """
        Update the position of the bullet based on its speed and angle.

        Returns:
            None: No return value.
        """
        x = self.center_x + self.speed * cos(self.angle)
        y = self.center_y + self.speed * sin(self.angle)

        self.center_x = x
        self.center_y = y
