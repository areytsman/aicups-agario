import json
from modules.obj_types import Type
from modules import game_config
from modules.classes import Obj, PlayerFragment, Coord, Move
from random import randint
import math


class Strategy:
    visible_objects = []
    food = []
    viruses = []
    players_fragments = []
    move = Move(0, 0, '', False, False, {})
    tick = 0
    split_lock = False
    need_consolidate = False

    def __init__(self, config: dict):
        self.mine = []
        self.update_config(config)
        self.way_point = Coord(randint(50, game_config.GAME_WIDTH - 50), randint(50, game_config.GAME_HEIGHT - 50))

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
        if self.need_consolidate:
            self.move.x = coord.x
            self.move.y = coord.y
        else:
            self.move.x = (coord.x - self.mine[0].x) * 100
            self.move.y = (coord.y - self.mine[0].y) * 100

    def find_vector_to_move(self):
        fragment_flag = False
        if len(self.players_fragments) > 0:
            for fragment in self.players_fragments:
                for my_frag in self.mine:
                    if fragment.mass / 1.2 > my_frag.mass:
                        self.go_to(my_frag.find_vector_move_from(fragment))
                        self.move.split = False
                        self.need_consolidate = True
                        return
                    if fragment.mass * 1.2 < my_frag.mass / 2:
                        if my_frag.get_distance_to(fragment) < my_frag.split_dist:
                            if my_frag.get_angle_to(fragment) - my_frag.speed_angle < math.pi / 12 and not self.split_lock:
                                self.move.split = True
                                self.need_consolidate = True
                    if fragment.mass * 1.2 > my_frag.mass / 2:
                        self.move.split = False
                        self.split_lock = True
                if fragment.mass < self.mine[0].mass / 1.2:
                    self.go_to(self.mine[0].find_vector_move_to(fragment))
                    fragment_flag = True
                    break
        if not fragment_flag:
            self.need_consolidate = False
            if len(self.food) > 0:
                nearest = self.find_nearest_object(self.food)
                self.go_to(self.mine[0].find_vector_move_to(nearest))
            else:
                self.go_to(self.way_point)

    def prepare_data(self):
        self.food = [obj for obj in self.visible_objects if obj.obj_type == Type.FOOD]
        self.viruses = [obj for obj in self.visible_objects if obj.obj_type == Type.VIRUS]
        self.players_fragments = [obj for obj in self.visible_objects if obj.obj_type == Type.PLAYER]
        if self.mine[0].get_distance_to(self.way_point) < 10:
            self.way_point = Coord(randint(50, game_config.GAME_WIDTH - 50), randint(50, game_config.GAME_HEIGHT - 50))
        if self.tick % 500 == 0:
            self.move.split = True
        else:
            self.move.split = False
        self.move.eject = False
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
        return self.move.to_dict()


if __name__ == '__main__':
    conf = json.loads(input())
    strategy = Strategy(conf)
    strategy.run()


