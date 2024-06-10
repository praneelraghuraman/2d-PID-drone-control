from pygame import math


class Wall:
    def __init__(
        self,
        coordinates: list,
        c_restitution,
        is_ground=False,
    ):
        self.coordinates = coordinates
        self.normal = math.Vector2(
            coordinates[3] - coordinates[1],
            coordinates[0] - coordinates[2],
        ).normalize()
        self.c_restitution = c_restitution
        self.is_ground = is_ground
