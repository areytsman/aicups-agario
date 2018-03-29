import json
from modules.obj_types import Type
from modules.game_config import Config
from modules.classes import Obj, PlayerFragment, Coord


class Strategy:
    visible_objects = []
    food = []
    viruses = []
    players_fragments = []
    move = {}
    way_points = []
    next_way_point = 0

    def __init__(self, config: dict):
        self.mine = []
        # for frag in config['Mine']:
        #     self.mine.append(PlayerFragment.from_dict(frag))
        self.config = Config()
        self.config.update(config)
        self.debug(str(config))

    def run(self):
        while True:
            data = json.loads(input())
            cmd = self.on_tick(data)
            print(json.dumps(cmd))
            self.debug(json.dumps(cmd))

    def find_nearest_object(self, objects: list):
        nearest = None
        distance = 99999
        for obj in objects:
            if nearest is None:
                nearest = obj
                distance = self.mine[0].get_distance_to(obj)
            else:
                if self.mine[0].get_distance_to(obj) < distance:
                    nearest = obj
                    distance = self.mine[0].get_distance_to(obj)
        return nearest

    def find_vector_to_move(self):
        if len(self.food) > 0:
            nearest = self.find_nearest_object(self.food)
            return {'X': nearest.x, 'Y': nearest.y}
        else:
            if self.mine[0].get_distance_to(self.way_points[self.next_way_point]) < 10:
                self.next_way_point = (self.next_way_point + 1) % len(self.way_points)
            return {'X': self.way_points[self.next_way_point].x, 'Y': self.way_points[self.next_way_point].y}


    def generate_way_points(self):
        step = self.config.GAME_WIDTH / 4
        return [Coord(step, step), Coord(step, 3 * step), Coord(3 * step, 3 * step), Coord(3 * step, step)]

    def prepare_data(self):
        self.food = [obj for obj in self.visible_objects if obj.obj_type == Type.FOOD]
        self.viruses = [obj for obj in self.visible_objects if obj.obj_type == Type.VIRUS]
        self.players_fragments = [obj for obj in self.visible_objects if obj.obj_type == Type.PLAYER]
        self.way_points = self.generate_way_points()

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
            return self.find_vector_to_move()
        return {'X': 0, 'Y': 0, 'Debug': 'Died'}

    @staticmethod
    def debug(string: str):
        with open('c:\\temp\\aicups.log', 'a') as file:
            file.write(string + '\n')


if __name__ == '__main__':
    with open('c:\\temp\\aicups.log', 'w') as file:
        file.write('')
    conf = json.loads(input())
    strategy = Strategy(conf)
    strategy.run()
