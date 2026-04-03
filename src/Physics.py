class CollisionBox:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def collides_with(self, other: "CollisionBox"):
        return (
            self.x < other.x + other.width and
            self.x + self.width > other.x and
            self.y < other.y + other.height and
            self.y + self.height > other.y
        )

    @staticmethod
    def check_collision(box1: "CollisionBox", box2: "CollisionBox"):
        return box1.collides_with(box2)

# def CircleBox(CollisionBox):
#     def __init__(self, x: int, y: int, radius: int):
#         super().__init__(x, y, radius * 2, radius * 2)

#     def collides_with(self, other: "CollisionBox"):
#         closest_x = max(self.x, min(cx, self.x + self.width))
#         closest_y = max(self.y, min(cy, self.y + self.height))

#         dx = cx - closest_x
#         dy = cy - closest_y

#         return (dx * dx + dy * dy) < (self.radius * self.radius)
