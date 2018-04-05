from typing import List
from modules.classes import *
from modules import game_config
from copy import deepcopy


class Simulation:
    def __init__(self, destination: Coord, mine: List[PlayerFragment], enemy: List[EnemyFragment],
                 food: List[Obj], ejects: List[Obj]):
        self.destination = self.crop_destination(destination)
        self.mine = deepcopy(mine)
        self.enemy = deepcopy(enemy)
        self.food = deepcopy(food)
        self.ejects = deepcopy(ejects)
        self.tick = 0
        self.score = 0

    @staticmethod
    def crop_destination(destination):
        if destination.x < 0:
            destination.x = 0
        if destination.y < 0:
            destination.y = 0
        if destination.x > game_config.GAME_WIDTH:
            destination.x = game_config.GAME_WIDTH
        if destination.y > game_config.GAME_HEIGHT:
            destination.y = game_config.GAME_HEIGHT
        return destination

    def calc_score(self, num_ticks: int, rate: int=1):
        for i in range(num_ticks // rate):
            self.simulate(rate)
        return self.score

    def calc_split_score(self, num_ticks: int, rate: int=1):
        new_fragments = []
        for fragment in self.mine:
            if fragment.mass > 120:
                splitted = fragment.split()
                new_fragments.append(splitted)
        for fragment in new_fragments:
            self.mine.append(fragment)
        return self.calc_score(num_ticks, rate)

    def simulate(self, rate: int):
        def eating():
            my_frag_to_delete = set()
            enemy_to_delete = set()
            for my_frag in self.mine:
                for enemy in self.enemy:
                    if my_frag.mass > enemy.mass:
                        if my_frag.get_distance_to(enemy) < my_frag.radius - enemy.radius * 2/3:
                            self.score += 50
                            my_frag.eat(enemy)
                            enemy_to_delete.add(enemy)
                    else:
                        if my_frag.get_distance_to(enemy) < enemy.radius - my_frag.radius * 2/3:
                            self.score -= 200
                            enemy.eat(my_frag)
                            my_frag_to_delete.add(my_frag)
            for frag in my_frag_to_delete:
                self.mine.remove(frag)
            for frag in enemy_to_delete:
                self.enemy.remove(frag)
            my_frag_to_delete.clear()
            enemy_to_delete.clear()

        def check_hard_intersections(fragment):
            if fragment.x - fragment.radius < 0:
                fragment.x = fragment.radius
            if fragment.x + fragment.radius > game_config.GAME_WIDTH:
                fragment.x = game_config.GAME_WIDTH - fragment.radius
            if fragment.y - fragment.radius < 0:
                fragment.y = fragment.radius
            if fragment.y + fragment.radius > game_config.GAME_HEIGHT:
                fragment.y = game_config.GAME_HEIGHT - fragment.radius

        self.tick += rate
        self_frags_to_delete = set()
        food_to_delete = set()
        ejects_to_delete = set()
        for my_frag in self.mine:
            def check_other_my_fragments_intersections(fragment: PlayerFragment):
                for fr in [f for f in self.mine if f != fragment and not f.fused]:
                    if fragment.get_distance_to(fr) < fragment.radius + fr.radius:
                        if fr.time_to_fade is not None or fragment.time_to_fade is not None:
                            fragment.x += (fragment.radius - fr.radius) * cos(fragment.get_angle_to(fr))
                            fragment.y += (fragment.radius - fr.radius) * sin(fragment.get_angle_to(fr))
                        else:
                            fr.fuse(fragment)
                            self_frags_to_delete.add(fragment)
                            fragment.fused = True

            current_angle = my_frag.get_angle_to(self.destination)
            nx = cos(current_angle)
            ny = sin(current_angle)
            dx = rate * (nx * my_frag.max_speed - my_frag.speed_x) * game_config.INERTION_FACTOR / my_frag.mass
            dy = rate * (ny * my_frag.max_speed - my_frag.speed_y) * game_config.INERTION_FACTOR / my_frag.mass
            my_frag.speed_x += dx
            my_frag.speed_y += dy
            my_frag.x += my_frag.speed_x
            my_frag.y += my_frag.speed_y
            check_hard_intersections(my_frag)
            check_other_my_fragments_intersections(my_frag)
            for food in self.food:
                if my_frag.get_distance_to(food) < my_frag.radius - food.radius * 2/3:
                    self.score += 1
                    my_frag.eat(food)
                    food_to_delete.add(food)
            for eject in self.ejects:
                if my_frag.get_distance_to(eject) < my_frag.radius - eject.radius * 2/3:
                    self.score += 1
                    my_frag.eat(eject)
                    ejects_to_delete.add(eject)
            for food in food_to_delete:
                self.food.remove(food)
            for eject in ejects_to_delete:
                self.ejects.remove(eject)
            food_to_delete.clear()
            ejects_to_delete.clear()
        for frag in self_frags_to_delete:
            self.mine.remove(frag)
        self_frags_to_delete.clear()
        for enemy in self.enemy:
            enemy.x += enemy.speed_x
            enemy.y += enemy.speed_y
            for food in self.food:
                if enemy.get_distance_to(food) < enemy.radius + food.radius * 1 / 4:
                    self.score += 1
                    enemy.eat(food)
                    food_to_delete.add(food)
            for eject in self.ejects:
                if enemy.get_distance_to(eject) < enemy.radius + eject.radius * 1 / 4:
                    self.score += 1
                    enemy.eat(eject)
                    ejects_to_delete.add(eject)
        for food in food_to_delete:
            self.food.remove(food)
        for eject in ejects_to_delete:
            self.ejects.remove(eject)
        food_to_delete.clear()
        ejects_to_delete.clear()
        eating()
