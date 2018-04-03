from typing import List
from modules.classes import *
from modules import game_config


class Simulation:
    def __init__(self, angle: float, mine: List[PlayerFragment], enemy: List[EnemyFragment],
                 food: List[Obj], ejects: List[Obj]):
        self.angle = angle
        self.mine = mine
        self.enemy = enemy
        self.food = food
        self.ejects = ejects
        self.tick = 0
        self.score = 0

    def calc_score(self, num_ticks: int):
        pass

    def simulate(self):
        self.tick += 1
