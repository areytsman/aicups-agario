import numpy
from modules.classes import *
from modules import game_config
from typing import List


class PotentialField:
    def __init__(self, crop_factor: int, food: List[Obj]):
        self.crop_factor = crop_factor
        self.field = numpy.zeros(shape=[game_config.GAME_WIDTH // crop_factor + 1, game_config.GAME_HEIGHT // crop_factor + 1])
        self.calc_field(food)

    def calc_field(self, food: List[Obj]):
        for f in food:
            x = f.x // self.crop_factor
            y = f.y // self.crop_factor
            self.field[x, y] += 1

    def get_max_value_coord(self):
        ind = numpy.unravel_index(numpy.argmax(self.field, axis=None), self.field.shape)
        x = ind[0] * self.crop_factor + self.crop_factor / 2
        y = ind[1] * self.crop_factor + self.crop_factor / 2
        return Coord(x, y)
