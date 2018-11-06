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
from .unit import DIRECTIONS


GAME_OBJECTS = {
    Space: ' ',
    Dot: '.',
    Wall: 'W',
    PackMan: 'P',
    Ghost: 'G'
}


class Arena:
    def __init__(self, width=30, height=30):
        self._dots = []
        self._spaces = []
        self._ghosts = []
        self._ghost_runners = []
        self._player = PackMan(position=_Point(x=0, y=0))

        self.width = width
        self.height = height
        self._objects_map = [[None] * width for h in range(height)]
        self._back_arena = [[Dot] * width for h in range(height)]
        self._player.position.x = 0
        self._player.position.y = 0
        self._objects_map[0][0] = PackMan
        self._ghosts.append(Ghost(position=_Point(width - 1, height - 1)))
        self._objects_map[height - 1][width - 1] = Ghost

    def load_from_file(self, path):
        self.reset()

        with open(path, 'r') as fhandle:
            width, height = map(int, fhandle.readline().split())
            self.width = width
            self.height = height
            self._objects_map = [[None] * width for h in range(height)]
            self._back_arena = [[Dot] * width for h in range(height)]

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

    def reset(self):
        self._dots.clear()
        self._spaces.clear()
        self._ghosts.clear()
        self._ghost_runners.clear()
        self._player.position = _Point(0, 0)

    def stop(self):
        for runner in self._ghost_runners:
            runner.stop()

    @property
    def arena(self):
        res = [[None] * self.width for _ in range(self.height)]
        for y, line in enumerate(self._objects_map):
            for x, el in enumerate(line):
                res[y][x] = GAME_OBJECTS[el]

        return res

    @property
    def dots(self):
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

    def move_player(self, direction):
        self.move_unit(self._player, direction)

    def move_ghost(self, ghost_code):
        with threading.Lock():
            direction = random.choice(DIRECTIONS)
            return self.move_unit(self._ghosts[ghost_code], direction)

    def move_unit(self, unit, direction):
        with threading.Lock():
            unit.direction = direction
            start_position = copy.deepcopy(unit.position)
            unit.move()

            if unit.position.x < 0:
                unit.position.x = self.width - 1
            if unit.position.y < 0:
                unit.position.y = self.height - 1
            if unit.position.x >= self.width:
                unit.position.x = 0
            if unit.position.y >= self.height:
                unit.position.y = 0

            # if player cross with ghost
            if issubclass(self._objects_map[self._player.position.y][self._player.position.x], Ghost):
                if not self._player.is_hungry():
                    self._player.lives -= 1
                    self._player.position = _Point(0, 0)
                    self._objects_map[self._player.position.y][self._player.position.x] = PackMan

            if isinstance(unit, (Ghost, )):
                if self._objects_map[unit.position.y][unit.position.x] == Ghost or \
                        self._objects_map[unit.position.y][unit.position.x] == Dot:
                    unit.position = start_position
                    return False

            if isinstance(unit, (PackMan, )):
                if self._objects_map[unit.position.y][unit.position.x] == Wall:
                    unit.position = start_position
                    return False

            if not isinstance(unit, (PackMan, )):
                self._objects_map[start_position.y][start_position.x] = self._back_arena[start_position.y][start_position.x]
                if self._objects_map[unit.position.y][unit.position.x] != PackMan and \
                   self._objects_map[unit.position.y][unit.position.x] != Ghost:
                        self._back_arena[unit.position.y][unit.position.x] = \
                            self._objects_map[unit.position.y][unit.position.x]
                self._objects_map[unit.position.y][unit.position.x] = type(unit)
            else:
                self._objects_map[start_position.y][start_position.x] = Space
                self._objects_map[unit.position.y][unit.position.x] = PackMan

            return True


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
