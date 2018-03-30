import json
from modules.obj_types import Type
from modules import game_config
from modules.classes import Obj, PlayerFragment, Coord, Move
import sys


class Strategy:
    visible_objects = []
    food = []
    viruses = []
    players_fragments = []
    move = Move(0, 0, '', False, False, {})
    way_points = []
    next_way_point = 0

    def __init__(self, config: dict):
        self.mine = []
        self.update_config(config)
        self.debug(str(config))

    def run(self):
        while True:
            data = json.loads(input())
            cmd = self.on_tick(data)
            print(json.dumps(cmd))
            self.debug(json.dumps(cmd))

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
        if len(self.players_fragments) > 0:
            for fragment in self.players_fragments:
                for my_frag in self.mine:
                    if fragment.mass / 1.2 > my_frag.mass:
                        self.go_to(my_frag.find_vector_move_from(fragment))
                        return
                if fragment.mass < self.mine[0].mass / 1.2:
                    self.go_to(self.mine[0].find_vector_move_to(fragment))
                    self.debug('has fragments')
                    return
        if len(self.food) > 0:
            nearest = self.find_nearest_object(self.food)
            self.go_to(self.mine[0].find_vector_move_to(nearest))
        else:
            if self.mine[0].get_distance_to(self.way_points[self.next_way_point]) < 10:
                self.next_way_point = (self.next_way_point + 1) % len(self.way_points)
            self.go_to(self.way_points[self.next_way_point])

    def generate_way_points(self):
        step = game_config.GAME_WIDTH / 4
        return [Coord(step, step), Coord(step, 3 * step), Coord(3 * step, 3 * step), Coord(3 * step, step)]

    def prepare_data(self):
        self.food = [obj for obj in self.visible_objects if obj.obj_type == Type.FOOD]
        self.viruses = [obj for obj in self.visible_objects if obj.obj_type == Type.VIRUS]
        self.players_fragments = [obj for obj in self.visible_objects if obj.obj_type == Type.PLAYER]
        self.way_points = self.generate_way_points()

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

    @staticmethod
    def debug(string: str):
        with open('aicups.log', 'a') as file:
            file.write(string + '\n')


if __name__ == '__main__':
    with open('aicups.log', 'w') as file:
        file.write('')
    conf = json.loads(input())
    strategy = Strategy(conf)
    try:
        strategy.run()
    except Exception as e:
        Strategy.debug(str(e) + sys.exc_info()[0])
