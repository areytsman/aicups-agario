from enum import Enum


class Type(Enum):
    VIRUS = 'V'
    PLAYER = 'P'
    FOOD = 'F'
    EJECT = 'E'
    MINE = None
