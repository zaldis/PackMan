import copy
import random
import threading
import time

from .unit import _Point
from .unit import Dot
from .unit import Space
from .unit import PackMan
from .unit import Ghost
from .unit import Wall
from .unit import Door
from .unit import Bonus
from .unit import SpeedBonus
from .unit import HungryBonus
from .unit import DIRECTIONS


GAME_OBJECTS = {
    Space: ' ',
    Dot: '.',
    Wall: 'W',
    Door: 'D',
    PackMan: 'P',
    Ghost: 'G',
    Bonus: 'B'
}


class Arena:
    def __init__(self, width=30, height=30):
        self._dots = []
        self._spaces = []
        self._ghosts = []
        self._ghost_runners = []
        self._bonus_generator = BonusGenerator(self)
        self._player = PackMan(position=_Point(x=0, y=0))

        self._all_bonuses = []
        self.bonus_runners = []
        self._width = width
        self._height = height
        self.running_game = True
        self.opened_door = False
        self._objects_map = [[None] * width for h in range(height)]
        self._back_arena = [[Dot] * width for h in range(height)]
        self._player.position.x = 0
        self._player.position.y = 0
        self._objects_map[0][0] = PackMan
        self._ghosts.append(Ghost(position=_Point(width - 1, height - 1)))
        self._objects_map[height - 1][width - 1] = Ghost

    def load_from_file(self, path):
        self.reset()
        self.running_game = True
        self.opened_door = False

        with open(path, 'r') as fhandle:
            width, height = map(int, fhandle.readline().split())
            self._width = width
            self._height = height
            self._objects_map = [[Space] * width for h in range(height)]
            self._back_arena = [[Space] * width for h in range(height)]

            for y, line in enumerate(fhandle):
                for x, ch in enumerate(line.strip()):
                    if ch == GAME_OBJECTS[PackMan]:
                        self._player.position = _Point(x, y)
                        self._objects_map[y][x] = PackMan
                    if ch == GAME_OBJECTS[Dot]:
                        self._dots.append(Dot(_Point(x, y)))
                        self._objects_map[y][x] = Dot
                    if ch == GAME_OBJECTS[Ghost]:
                        self._ghosts.append(Ghost(_Point(x, y), code=len(self._ghosts)))
                        self._objects_map[y][x] = Ghost
                    if ch == GAME_OBJECTS[Wall]:
                        self._objects_map[y][x] = Wall
                    if ch == GAME_OBJECTS[Space]:
                        self._objects_map[y][x] = Space

        for ghost in self._ghosts:
            runner = RunnerGhost(ghost, self)
            runner.start()
            self._ghost_runners.append(runner)

        self._bonus_generator = BonusGenerator(self)
        self._bonus_generator.start()

    def reset(self):
        self._all_bonuses = [HungryBonus, SpeedBonus]
        self._dots.clear()
        self._spaces.clear()
        self._ghosts.clear()
        self._ghost_runners.clear()
        self._player.position = _Point(0, 0)

    def stop(self):
        for runner in self._ghost_runners:
            runner.stop()
        self._bonus_generator.stop()

        while self._bonus_generator.is_alive():
            pass

        for runner in self.bonus_runners:
            runner.stop()

    @property
    def player(self):
        return copy.deepcopy(self._player)

    @property
    def arena(self):
        res = [[None] * self._width for _ in range(self._height)]
        for y, line in enumerate(self._objects_map):
            for x, el in enumerate(line):
                if issubclass(el, Bonus):
                    res[y][x] = GAME_OBJECTS[Bonus]
                else:
                    res[y][x] = GAME_OBJECTS[el]

        return res

    @property
    def count_dots(self):
        cnt_dots = 0
        for line in self._objects_map:
            for el in line:
                if issubclass(el, Dot):
                    cnt_dots += 1

        return cnt_dots

    @property
    def spaces(self):
        cnt_spaces = 0
        for line in self._objects_map:
            for el in line:
                if issubclass(el, Space):
                    cnt_spaces += 1

        return cnt_spaces

    @property
    def player_lives(self):
        return self._player.lives

    @property
    def player_pause(self):
        return self._player.pause

    @property
    def space_position(self):
        with threading.Lock():
            for y, line in enumerate(self._objects_map):
                for x, el in enumerate(line):
                    if issubclass(el, Space):
                        return _Point(x, y)

            return None

    @property
    def score(self):
        return self._player.score

    @property
    def bonuses(self):
        return self._player.bonuses

    def move_player(self, direction):
        self.move_unit(self._player, direction)
        if self.count_dots == 0 and not self.opened_door:
            self.create_door()
            self.opened_door = True

    def create_door(self):
        space_position = self.space_position
        self._objects_map[space_position.y][space_position.x] = Door

    def move_ghost(self, ghost_code):
        with threading.Lock():
            direction = random.choice(DIRECTIONS)
            return self.move_unit(self._ghosts[ghost_code], direction)

    def move_bonus(self, bonus):
        with threading.Lock():
            direction = random.choice(DIRECTIONS)
            return self.move_unit(bonus, direction)

    def move_unit(self, unit, direction):
        with threading.Lock():
            unit.direction = direction
            start_position = copy.deepcopy(unit.position)
            unit.move()

            if unit.position.x < 0:
                unit.position.x = self._width - 1
            if unit.position.y < 0:
                unit.position.y = self._height - 1
            if unit.position.x >= self._width:
                unit.position.x = 0
            if unit.position.y >= self._height:
                unit.position.y = 0

            # if player cross with ghost
            if issubclass(self._objects_map[self._player.position.y][self._player.position.x], Ghost):
                if not self._player.is_hungry():
                    self._player.lives -= 1
                    self._player.position = self.space_position
                    self._objects_map[self._player.position.y][self._player.position.x] = PackMan
                else:
                    self.stop_ghost_runner(position=_Point(self._player.position.x, self._player.position.y))

            # ghosts and bonuses don't cross
            if isinstance(unit, (Ghost, )) or issubclass(type(unit), Bonus):
                if self._objects_map[unit.position.y][unit.position.x] == Ghost or \
                        self._objects_map[unit.position.y][unit.position.x] == Dot or \
                        self._objects_map[unit.position.y][unit.position.x] == Door or \
                        self._objects_map[unit.position.y][unit.position.x] == PackMan or \
                        issubclass(self._objects_map[unit.position.y][unit.position.x], Bonus):
                    unit.position = start_position
                    return False

            if isinstance(unit, (PackMan, )):
                if self._objects_map[unit.position.y][unit.position.x] == Wall or \
                        self._back_arena[unit.position.y][unit.position.x] == Wall:
                    unit.position = start_position
                    return False
                self._player.score += self._objects_map[unit.position.y][unit.position.x].score
                if issubclass(self._objects_map[unit.position.y][unit.position.x], Bonus):
                    bonus = (self._objects_map[unit.position.y][unit.position.x])(
                        packman=self._player,
                        position=_Point(unit.position.x, unit.position.y)
                    )
                    self.stop_bonus_runner(_Point(bonus.position.x, bonus.position.y))
                    if not self._player.have_bonus(type(bonus)):
                        applier = BonusApplier(bonus)
                        applier.start()
                if issubclass(self._objects_map[unit.position.y][unit.position.x], Door):
                    self.running_game = False

            if not isinstance(unit, (PackMan, )):
                self._objects_map[start_position.y][start_position.x] = \
                    self._back_arena[start_position.y][start_position.x]
                if self._objects_map[unit.position.y][unit.position.x] != PackMan and \
                   self._objects_map[unit.position.y][unit.position.x] != Ghost:
                        self._back_arena[unit.position.y][unit.position.x] = \
                            self._objects_map[unit.position.y][unit.position.x]
                self._objects_map[unit.position.y][unit.position.x] = type(unit)
            else:
                self._objects_map[start_position.y][start_position.x] = Space
                self._objects_map[unit.position.y][unit.position.x] = PackMan

            return True

    def stop_ghost_runner(self, position: _Point):
        for runner in self._ghost_runners:
            if runner.ghost.position.x == position.x and runner.ghost.position.y == position.y:
                runner.stop()

    def stop_bonus_runner(self, position: _Point):
        for runner in self.bonus_runners:
            if runner.bonus.position.x == position.x and runner.bonus.position.y == position.y:
                runner.stop()


class RunnerGhost(threading.Thread):
    def __init__(self, ghost, arena):
        super().__init__()
        self._is_running = True
        self.ghost = ghost
        self.arena = arena

    def stop(self):
        self._is_running = False

    def run(self):
        while self._is_running:
            cnt = 40
            while not self.arena.move_ghost(self.ghost.code) and cnt > 0:
                cnt -= 1

            time.sleep(self.ghost.pause)


class BonusGenerator(threading.Thread):
    def __init__(self, arena):
        super().__init__()
        self.arena = arena
        self._is_running = True
        self.sleeper = threading.Event()

    def stop(self):
        self.sleeper.set()
        self._is_running = False

    def run(self):
        while self._is_running:
            self.sleeper.wait(timeout=40)

            space_position = self.arena.space_position
            if space_position:
                bonus_type = random.choice(self.arena._all_bonuses)
                speed_bonus = bonus_type(position=space_position, packman=self.arena.player)
                bonus_runner = BonusRunner(self.arena, bonus=speed_bonus)
                self.arena._objects_map[space_position.y][space_position.x] = SpeedBonus
                self.arena.bonus_runners.append(bonus_runner)
                bonus_runner.start()


class BonusRunner(threading.Thread):
    def __init__(self, arena, bonus):
        super().__init__()
        self.arena = arena
        self.bonus = bonus
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        while self._is_running:
            cnt = 40
            while not self.arena.move_bonus(self.bonus) and cnt > 0:
                cnt -= 1

            time.sleep(self.bonus.pause)


class BonusApplier(threading.Thread):
    def __init__(self, bonus):
        super().__init__()
        self.bonus = bonus

    def run(self):
        self.bonus.apply()
        time.sleep(10)
        self.bonus.destroy()
