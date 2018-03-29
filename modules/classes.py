from math import *
from modules.obj_types import Type
from modules.game_config import Config


class Obj:
    def __init__(self, x: float, y: float, mass: float, radius: float, obj_type: Type = Type.FOOD, oid: str = None):
        self.x = x
        self.y = y
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
            mass = Config.FOOD_MASS
        else:
            mass = obj['M']
        if obj_type == Type.VIRUS:
            radius = Config.VIRUS_RADIUS
        elif obj_type == Type.FOOD:
            radius = Config.FOOD_RADIUS
        else:
            radius = obj['R']
        if obj_type == Type.FOOD:
            oid = None
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


class Move:
    def __init__(self, x: float, y: float, debug: str, sprite: dict, split: bool = False, eject: bool = False):
        pass


class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

