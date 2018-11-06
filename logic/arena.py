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
        self._arena = [[GAME_OBJECTS[Dot]] * width for h in range(height)]
        self._back_arena = [[GAME_OBJECTS[Dot]] * width for h in range(height)]
        self._player.position.x = 0
        self._player.position.y = 0
        self._arena[0][0] = GAME_OBJECTS[PackMan]
        self._ghosts.append(Ghost(position=_Point(width - 1, height - 1)))
        self._arena[height - 1][width - 1] = GAME_OBJECTS[Ghost]

    def load_from_file(self, path):
        self.reset()

        with open(path, 'r') as fhandle:
            width, height = map(int, fhandle.readline().split())
            self.width = width
            self.height = height
            self._arena = [[GAME_OBJECTS[Dot]] * width for h in range(height)]
            self._back_arena = [[GAME_OBJECTS[Space]] * width for h in range(height)]

            for y, line in enumerate(fhandle):
                for x, ch in enumerate(line.strip()):
                    if ch == GAME_OBJECTS[PackMan]:
                        self._player.position = _Point(x, y)
                    if ch == GAME_OBJECTS[Dot]:
                        self._dots.append(Dot(_Point(x, y)))
                    if ch == GAME_OBJECTS[Ghost]:
                        self._ghosts.append(Ghost(_Point(x, y), code=len(self._ghosts)))

                    self._arena[y][x] = ch

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
        return self._arena

    @property
    def dots(self):
        cnt_dots = 0
        for line in self._arena:
            for ch in line:
                if ch == GAME_OBJECTS[Dot]:
                    cnt_dots += 1

        return cnt_dots

    @property
    def spaces(self):
        cnt_dots = 0
        for line in self._arena:
            for ch in line:
                if ch == GAME_OBJECTS[Space]:
                    cnt_dots += 1

        return cnt_dots

    @property
    def player_lives(self):
        return self._player.lives

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

            if self._arena[self._player.position.y][self._player.position.x] == GAME_OBJECTS[Ghost]:
                if not self._player.is_hungry():
                    self._player.lives -= 1
                    self._player.position = _Point(0, 0)
                    self._arena[self._player.position.y][self._player.position.x] = GAME_OBJECTS[PackMan]

            if isinstance(unit, (Ghost, )):
                if self._arena[unit.position.y][unit.position.x] == GAME_OBJECTS[Ghost] or \
                        self._arena[unit.position.y][unit.position.x] == GAME_OBJECTS[Dot]:
                    unit.position = start_position
                    return False

            if isinstance(unit, (PackMan, )):
                if self._arena[unit.position.y][unit.position.x] == GAME_OBJECTS[Wall]:
                    unit.position = start_position
                    return False

            if not isinstance(unit, (PackMan, )):
                self._arena[start_position.y][start_position.x] = self._back_arena[start_position.y][start_position.x]
                self._back_arena[unit.position.y][unit.position.x] = self._arena[unit.position.y][unit.position.x]
                self._arena[unit.position.y][unit.position.x] = GAME_OBJECTS[type(unit)]
            else:
                self._arena[start_position.y][start_position.x] = GAME_OBJECTS[Space]
                self._arena[unit.position.y][unit.position.x] = GAME_OBJECTS[PackMan]
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
            time.sleep(1)
