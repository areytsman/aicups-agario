import json
from modules.simulation import Simulation
from modules.classes import *
from random import randint, choice
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
        self.way_points = [Coord(100, 100), Coord(100, game_config.GAME_HEIGHT - 100),
                            Coord(game_config.GAME_WIDTH - 100, 100),
                            Coord(game_config.GAME_WIDTH - 100, game_config.GAME_HEIGHT - 100),
                            Coord(game_config.GAME_WIDTH / 2, game_config.GAME_HEIGHT / 2)]
        self.way_point = self.way_points[randint(0, len(self.way_points) - 1)]
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

    def calc_vector_to_go(self):
        vector = Vector(0, 0)
        frag = self.mine[0]
        avoid_viruses = False
        hyperbolic_focus = 2 * sqrt(sum([f.mass for f in self.mine]))
        hyperbolic_coefficient = 4

        for my_frag in self.mine:
            my_frag_vector = Vector(0, 0)
            for fragment in self.enemy_fragments.values():
                if (fragment.mass + game_config.FOOD_MASS * 5) / 1.2 > my_frag.mass and my_frag.get_distance_to(
                        fragment) < fragment.split_dist:
                    angle = my_frag.get_angle_to(fragment)
                    length = 2000 * my_frag.mass / (my_frag.get_distance_to(fragment) - fragment.radius * 0.7)
                    map_center = Coord(game_config.GAME_WIDTH / 2, game_config.GAME_HEIGHT / 2)
                    my_frag_vector += Vector(angle - math.pi, length) + Vector(my_frag.get_angle_to(map_center), length / 1.5)
                if my_frag.mass / 2 < fragment.mass * 1.2 < my_frag.mass:
                    length = 3000 / my_frag.get_distance_to(fragment)
                    angle = my_frag.get_angle_to(fragment)
                    my_frag_vector += Vector(angle, length)
                if fragment.mass * 1.2 < my_frag.mass / 2:
                    length = 5000 / my_frag.get_distance_to(fragment)
                    angle = my_frag.get_angle_to(fragment)
                    my_frag_vector += Vector(angle, length)
                if game_config.MAX_FRAGS_CNT != len(self.mine):
                    if fragment.mass * 1.2 > my_frag.mass / (game_config.MAX_FRAGS_CNT - len(self.mine)):
                        avoid_viruses = True
            for piece in self.food:
                if piece.x * piece.y < hyperbolic_coefficient * hyperbolic_focus ** 2 or \
                   (game_config.GAME_WIDTH - piece.x) * piece.y < hyperbolic_coefficient * hyperbolic_focus ** 2 or \
                   piece.x * (game_config.GAME_HEIGHT - piece.y) < hyperbolic_coefficient * hyperbolic_focus ** 2 or \
                   (game_config.GAME_WIDTH - piece.x) * (game_config.GAME_HEIGHT - piece.y) < hyperbolic_coefficient * hyperbolic_focus ** 2:
                    continue
                angle_between_speed_and_piece = atan2(my_frag.speed_y, my_frag.speed_x) - atan2(piece.y - my_frag.y, piece.x - my_frag.x)
                a = -math.pi / 4
                b = math.pi / 4
                if angle_between_speed_and_piece < a or angle_between_speed_and_piece > b:
                    continue
                length = 200 / my_frag.get_distance_to(piece)
                angle = my_frag.get_angle_to(piece)
                my_frag_vector += Vector(angle, length)
            if my_frag_vector.length == 0:
                my_frag_vector += Vector(my_frag.get_angle_to(self.way_point), my_frag.radius)
            if avoid_viruses or self.split_lock:
                for virus in [v for v in self.viruses if my_frag.get_distance_to(v) < my_frag.radius * 1.1 + v.radius]:
                    if my_frag.mass > game_config.VIRUS_BANG_MASS and my_frag.radius > virus.radius:
                        angle = my_frag.get_angle_to(virus)
                        length = 1000 / my_frag.get_distance_to(virus)
                        my_frag_vector += Vector(angle - math.pi, length)
            if my_frag.x * my_frag.y < hyperbolic_coefficient * hyperbolic_focus ** 2:
                can_corner = False
                for fragment in self.enemy_fragments.values():
                    if fragment.x * fragment.y < hyperbolic_coefficient * hyperbolic_focus ** 2:
                        can_corner = True
                if not can_corner:
                    length = hyperbolic_coefficient * hyperbolic_focus ** 2 / my_frag.x * my_frag.y - 1
                    angle = my_frag.get_angle_to(Coord(game_config.GAME_HEIGHT / 2, game_config.GAME_WIDTH / 2))
                    my_frag_vector += Vector(angle, length)
            if (game_config.GAME_WIDTH - my_frag.x) * my_frag.y < hyperbolic_coefficient * hyperbolic_focus ** 2:
                can_corner = False
                for fragment in self.enemy_fragments.values():
                    if (game_config.GAME_WIDTH - fragment.x) * fragment.y < hyperbolic_coefficient * hyperbolic_focus ** 2:
                        can_corner = True
                if not can_corner:
                    length = hyperbolic_coefficient * hyperbolic_focus ** 2 / (
                                game_config.GAME_WIDTH - my_frag.x) * my_frag.y - 1
                    angle = my_frag.get_angle_to(Coord(game_config.GAME_HEIGHT / 2, game_config.GAME_WIDTH / 2))
                    my_frag_vector += Vector(angle, length)
            if my_frag.x * (game_config.GAME_HEIGHT - my_frag.y) < hyperbolic_coefficient * hyperbolic_focus ** 2:
                can_corner = False
                for fragment in self.enemy_fragments.values():
                    if fragment.x * (game_config.GAME_HEIGHT - fragment.y) < hyperbolic_coefficient * hyperbolic_focus ** 2:
                        can_corner = True
                if not can_corner:
                    length = hyperbolic_coefficient * hyperbolic_focus ** 2 / my_frag.x * (
                                game_config.GAME_HEIGHT - my_frag.y) - 1
                    angle = my_frag.get_angle_to(Coord(game_config.GAME_HEIGHT / 2, game_config.GAME_WIDTH / 2))
                    my_frag_vector += Vector(angle, length)
            if (game_config.GAME_WIDTH - my_frag.x) * (
                    game_config.GAME_HEIGHT - my_frag.y) < hyperbolic_coefficient * hyperbolic_focus ** 2:
                can_corner = False
                for fragment in self.enemy_fragments.values():
                    if (game_config.GAME_WIDTH - fragment.x) * (
                            game_config.GAME_HEIGHT - fragment.y) < hyperbolic_coefficient * hyperbolic_focus ** 2:
                        can_corner = True
                if not can_corner:
                    length = hyperbolic_coefficient * hyperbolic_focus ** 2 / (game_config.GAME_WIDTH - my_frag.x) * (
                                game_config.GAME_HEIGHT - my_frag.y) - 1
                    angle = my_frag.get_angle_to(Coord(game_config.GAME_HEIGHT / 2, game_config.GAME_WIDTH / 2))
                    my_frag_vector += Vector(angle, length)
            if my_frag_vector.length > vector.length:
                vector = my_frag_vector
                frag = my_frag
        if vector.length < 2 * frag.radius:
            vector.length = 2 * frag.radius
        return self.crop_vector(vector, frag), frag

    def crop_vector(self, vector: Vector, coord: Coord):
        def is_dest_valid(dest: Coord):
            if dest.x > game_config.GAME_WIDTH \
                    or dest.y > game_config.GAME_HEIGHT \
                    or dest.x < 0 \
                    or dest.y < 0:
                return False
            return True
        dest_coord = Coord(coord.x + vector.x, coord.y + vector.y)
        while not is_dest_valid(dest_coord):
            vector = Vector(vector.angle, vector.length / 2)
            dest_coord = Coord(coord.x + vector.x, coord.y + vector.y)
        return vector

    def find_vector_to_move(self):
        if len(self.enemy_fragments.values()) > 0:
            for fragment in self.enemy_fragments.values():
                for my_frag in self.mine:
                    if fragment.mass > my_frag.mass * 1.2 and \
                            my_frag.get_distance_to(fragment) < fragment.split_dist * 1.2:
                        self.move.split = False
                        self.need_consolidate = True
                        self.split_lock = True
                        revert_vector = self.crop_vector(Vector(my_frag.speed_angle - math.pi, my_frag.radius * 3), my_frag)
                        self.way_point = Coord(revert_vector.x, revert_vector.y)
                        break
                    elif fragment.mass * 1.2 < my_frag.mass / 2 and fragment.ticks_visible > 0:
                        if my_frag.get_distance_to(fragment) < my_frag.split_dist:
                            if not self.split_lock and len(self.mine) < game_config.MAX_FRAGS_CNT / 2:
                                destination_x = my_frag.x + cos(my_frag.speed_angle) * my_frag.radius
                                destination_y = my_frag.y + sin(my_frag.speed_angle) * my_frag.radius
                                destination = Coord(destination_x, destination_y)
                                sim = Simulation(destination, self.mine, list(self.enemy_fragments.values()), self.food,
                                                 self.ejects, self.viruses)
                                sim.calc_split_score(30, 3)
                                if len(sim.enemy) < len(self.enemy_fragments):
                                    self.move.split = True
                                    self.need_consolidate = True
                    elif fragment.mass * 1.2 > my_frag.mass / 2:
                        self.move.split = False
                        self.need_consolidate = True
                        self.split_lock = True
            vector_to_go, frag = self.calc_vector_to_go()
            if len(self.mine) < 5 and len(self.visible_objects) < 25 and len(self.enemy_fragments) < 5:
                best_destination = None
                best_score = -99999
                max_frag = max(self.mine, key=lambda x: x.mass)
                for angle in numpy.linspace(vector_to_go.angle - math.pi / 8, vector_to_go.angle + math.pi / 8, 5):
                    destination_x = max_frag.x + cos(angle) * vector_to_go.length
                    destination_y = max_frag.y + sin(angle) * vector_to_go.length
                    destination = Coord(destination_x, destination_y)
                    sim = Simulation(destination, self.mine, list(self.enemy_fragments.values()), self.food, self.ejects,
                                     self.viruses)
                    score = sim.calc_score(40, len(self.mine))
                    if score > best_score:
                        best_score = score
                        best_destination = destination
                for angle in numpy.linspace(max_frag.speed_angle - math.pi / 16, max_frag.speed_angle + math.pi / 16, 3):
                    destination_x = max_frag.x + cos(angle) * 2 * sqrt(max_frag.mass)
                    destination_y = max_frag.y + sin(angle) * 2 * sqrt(max_frag.mass)
                    destination = Coord(destination_x, destination_y)
                    sim = Simulation(destination, self.mine, list(self.enemy_fragments.values()), self.food,
                                     self.ejects, self.viruses)
                    score = sim.calc_score(40, len(self.mine))
                    if score > best_score:
                        best_score = score
                        best_destination = destination
                self.go_to(best_destination)
            else:
                self.go_to(frag.find_vector_move_to(Coord(frag.x + vector_to_go.x, frag.y + vector_to_go.y)))
        elif len(self.food) > 0:
            dest_coord = self.find_nearest_object(self.food)
            self.go_to(dest_coord)
        else:
            self.go_to(self.way_point)

    def update_enemy_fragments(self):
        new_fragments = {f.oid: EnemyFragment(f) for f in self.visible_objects if f.obj_type == Type.PLAYER}
        if len(self.enemy_fragments) == 0:
            self.enemy_fragments = new_fragments
            return
        to_delete = []
        for key in self.enemy_fragments.keys():
            if key in new_fragments.keys():
                self.enemy_fragments[key].update(new_fragments[key])
                self.enemy_fragments[key].ticks_visible += 1
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
        max_frag = max(self.mine, key=lambda x: x.mass)
        if self.mine[0].get_distance_to(self.way_point) < 2 * max_frag.radius:
            self.way_point = self.way_points[randint(0, len(self.way_points) - 1)]
        if self.way_point not in self.way_points:
            self.way_point = self.way_points[randint(0, len(self.way_points) - 1)]
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
            if not self.split_lock and self.tick % 100 == 0:
                self.move.split = True
            else:
                self.move.split = False
            self.find_vector_to_move()

        return self.move.to_dict()


if __name__ == '__main__':
    conf = json.loads(input())
    strategy = Strategy(conf)
    strategy.run()
