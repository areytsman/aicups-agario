import json
from modules.obj_types import Type
from modules import game_config
from modules.simulation import Simulation
from modules.classes import *
from random import randint
import math
import numpy


class Strategy:
    visible_objects = []
    food = []
    viruses = []
    enemy_fragments = {}
    ejects = []
    move = Move(0, 0, '', False, False, {})
    tick = 0
    split_lock = False
    need_consolidate = False

    def __init__(self, config: dict):
        self.mine = []
        self.update_config(config)
        self.way_point = Coord(randint(50, game_config.GAME_WIDTH - 50), randint(50, game_config.GAME_HEIGHT - 50))
        self.move.debug = str(config)

    def run(self):
        while True:
            data = json.loads(input())
            cmd = self.on_tick(data)
            print(json.dumps(cmd))

    def find_nearest_object(self, objects: list):
        nearest = None
        time_to_go = game_config.GAME_TICKS
        for obj in objects:
            obj_time_to_go = self.mine[0].calc_time_to_go(obj)
            if nearest is None:
                nearest = obj
                time_to_go = obj_time_to_go
            else:
                if obj_time_to_go < time_to_go:
                    nearest = obj
                    time_to_go = obj_time_to_go
        return nearest

    def go_to(self, coord: Coord):
        self.move.x = coord.x
        self.move.y = coord.y

    def find_vector_to_move(self):
        for angle in numpy.linspace(0, math.pi * 2, 64):
            sim = Simulation(angle, self.mine, list(self.enemy_fragments.values()), self.food, self.ejects)
        self.go_to(Coord(0, 0))

    def update_enemy_fragments(self):
        new_fragments = {f.oid: EnemyFragment(f) for f in self.visible_objects if f.obj_type == Type.PLAYER}
        if len(self.enemy_fragments) == 0:
            self.enemy_fragments = new_fragments
            return
        to_delete = []
        for key in self.enemy_fragments.keys():
            if key in new_fragments.keys():
                self.enemy_fragments[key].update(new_fragments[key])
            else:
                to_delete.append(key)
        for key in to_delete:
            self.enemy_fragments.pop(key)
        for key in new_fragments.keys():
            if key not in self.enemy_fragments.keys():
                self.enemy_fragments[key] = new_fragments[key]

    def prepare_data(self):
        self.food = [obj for obj in self.visible_objects if obj.obj_type == Type.FOOD or obj.obj_type == Type.EJECT]
        self.viruses = [obj for obj in self.visible_objects if obj.obj_type == Type.VIRUS]
        self.update_enemy_fragments()
        if self.mine[0].get_distance_to(self.way_point) < 10:
            self.way_point = Coord(randint(50, game_config.GAME_WIDTH - 50), randint(50, game_config.GAME_HEIGHT - 50))
        self.move.eject = False
        if self.tick > 2:
            self.move.debug = ''
        self.split_lock = False
        if len(self.mine) == 1:
            self.need_consolidate = False

    @staticmethod
    def update_config(config: dict):
        game_config.GAME_TICKS = config['GAME_TICKS']
        game_config.GAME_WIDTH = config['GAME_WIDTH']
        game_config.GAME_HEIGHT = config['GAME_HEIGHT']
        game_config.FOOD_MASS = config['FOOD_MASS']
        game_config.MAX_FRAGS_CNT = config['MAX_FRAGS_CNT']
        game_config.TICKS_TIL_FUSION = config['TICKS_TIL_FUSION']
        game_config.VIRUS_RADIUS = config['VIRUS_RADIUS']
        game_config.VIRUS_SPLIT_MASS = config['VIRUS_SPLIT_MASS']
        game_config.VISCOSITY = config['VISCOSITY']
        game_config.INERTION_FACTOR = config['INERTION_FACTOR']
        game_config.SPEED_FACTOR = config['SPEED_FACTOR']

    def on_tick(self, data):
        self.tick += 1
        mine, objects = data['Mine'], data['Objects']
        if mine:
            self.visible_objects = []
            fragments = []
            for fragment in mine:
                fragments.append(PlayerFragment.from_dict(fragment))
            self.mine = fragments
            for obj in objects:
                self.visible_objects.append(Obj.from_dict(obj))
            self.prepare_data()
            self.find_vector_to_move()
            if self.tick % 250 == 0 and not self.split_lock:
                self.move.split = True
            else:
                self.move.split = False
        return self.move.to_dict()


if __name__ == '__main__':
    conf = json.loads(input())
    strategy = Strategy(conf)
    strategy.run()
