from math import *
from modules.obj_types import Type
from modules import game_config


class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Obj(Coord):
    def __init__(self, x: float, y: float, mass: float, radius: float, obj_type: Type = Type.FOOD, oid: str = None):
        super().__init__(x, y)
        self.mass = mass
        self.radius = radius
        self.obj_type = obj_type
        self.oid = oid

    def get_distance_to(self, obj):
        return sqrt(abs(self.x - obj.x) ** 2 + abs(self.y - obj.y) ** 2)

    @staticmethod
    def from_dict(obj: dict):
        obj_type = Type(obj['T'])
        x = obj['X']
        y = obj['Y']
        if obj_type == Type.FOOD:
            mass = game_config.FOOD_MASS
        elif obj_type == Type.EJECT:
            mass = game_config.EJECT_MASS
        else:
            mass = obj['M']
        if obj_type == Type.VIRUS:
            radius = game_config.VIRUS_RADIUS
        elif obj_type == Type.FOOD or obj_type == Type.EJECT:
            radius = game_config.FOOD_RADIUS
        else:
            radius = obj['R']
        if obj_type == Type.FOOD:
            oid = None
        elif obj_type == Type.EJECT:
            oid = obj['pId']
        else:
            oid = obj['Id']
        return Obj(x, y, mass, radius, obj_type, oid)


class PlayerFragment(Obj):
    def __init__(self, x: float, y: float, mass: float, radius: float, oid: str, speed_x: float, speed_y: float,
                 time_to_fade: int = None):
        super().__init__(x, y, mass, radius, Type.PLAYER, oid)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.time_to_fade = time_to_fade
        self.max_speed = game_config.SPEED_FACTOR / sqrt(mass)
        self.split_dist = self.calc_split_dist()
        self.speed_angle = self.get_angle_to(Coord(self.x + speed_x, self.y + speed_y))

    def get_angle_to(self, coord: Coord):
        return atan2(coord.y - self.y, coord.x - self.x)

    @staticmethod
    def from_dict(mine: dict):
        x = mine['X']
        y = mine['Y']
        mass = mine['M']
        radius = mine['R']
        oid = mine['Id']
        speed_x = mine['SX']
        speed_y = mine['SY']
        if 'TTF' in mine.keys():
            time_to_fade = mine['TTF']
        else:
            time_to_fade = None
        return PlayerFragment(x, y, mass, radius, oid, speed_x, speed_y, time_to_fade)

    def calc_split_dist(self):
        # Game accelerate formula
        k = 1 / game_config.SPLIT_SPEED
        u_vector = game_config.SPLIT_SPEED * k
        a = (u_vector * (game_config.SPLIT_SPEED / (sqrt(self.mass) / 2)) - game_config.SPLIT_SPEED) * game_config.INERTION_FACTOR / (self.mass / 2)
        # Finding time to zeroring speed
        t = -game_config.SPLIT_SPEED / a
        dist = game_config.SPLIT_SPEED * t + a * (t ** 2) / 2
        return dist

    def calc_time_to_go(self, coord: Coord):
        vector = self.find_vector_move_to(coord)
        vector_len = sqrt((self.x - vector.x) ** 2 + (self.y - vector.y) ** 2)
        time = vector_len / self.max_speed
        return time

    def find_vector_move_to(self, coord: Coord):
        # Finding unit vector
        vector_len = sqrt(self.speed_x ** 2 + self.speed_y ** 2)
        if vector_len < 1:
            k = 0
        else:
            k = 1 / vector_len
        u_vector_x = self.x + self.speed_x * k
        u_vector_y = self.y + self.speed_y * k
        # Game accelerate formula
        ax = (u_vector_x * self.max_speed - self.speed_x) * game_config.INERTION_FACTOR / self.mass
        ay = (u_vector_y * self.max_speed - self.speed_y) * game_config.INERTION_FACTOR / self.mass
        # Finding time to zeroring speed
        t = -self.speed_x / ax
        # Finding coordinate where speed will zero
        x0 = self.x + self.speed_x * t + ax * (t ** 2) / 2
        y0 = self.y + self.speed_y * t + ay * (t ** 2) / 2
        # Find delta
        dx = self.x - x0
        dy = self.y - y0
        return Coord(coord.x + dx, coord.y + dy)

    def find_vector_move_from(self, coord: Coord):
        opposite_coord = Coord(2 * self.x - coord.x, 2 * self.y - coord.y)
        return self.find_vector_move_to(opposite_coord)


class Move(Coord):
    def __init__(self, x: float, y: float, debug: str, split: bool = False, eject: bool = False, sprite: dict = None):
        super().__init__(x, y)
        self.debug = debug
        self.sprite = sprite
        self.split = split
        self.eject = eject

    def to_dict(self):
        return {'X': self.x, 'Y': self.y, 'Debug': self.debug, 'Split': self.split, 'Eject': self.eject,
                'Sprite': self.sprite}


class Vector(Coord):
    def __init__(self, angle, length):
        super().__init__(length * cos(angle), length * sin(angle))
        self.length = length
        self.angle = angle

    def __add__(self, other: Coord):
        x = self.x + other.x
        y = self.y + other.y
        length = sqrt(x ** 2 + y ** 2)
        angle = atan2(y, x)
        return Vector(angle, length)

    @staticmethod
    def shift(coord1: Coord, coord2: Coord):
        return Vector(coord2.x - coord1.x, coord2.y - coord1.y)

    def add_by_coord(self, coord1: Coord, coord2: Coord):
        return self + self.shift(coord1, coord2)

