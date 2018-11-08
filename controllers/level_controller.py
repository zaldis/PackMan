import curses
import os
import threading
import time
from logic.arena import Arena
from presentation.console_presentation import ConsolePresentation


ARENA_WIN_H = 15
ARENA_WIN_W = 30

STATISTIC_WIN_H = 10
STATISTIC_WIN_W = 30


class LevelController:
    LEVEL_PATH = os.path.join('.', 'levels')

    def __init__(self):
        self.level_number = 1
        self.arena = Arena()
        self.screen = curses.initscr()
        self.arena_win = curses.newwin(ARENA_WIN_H, ARENA_WIN_W, 0, 0)
        self.statistic_win = curses.newwin(STATISTIC_WIN_H, STATISTIC_WIN_W, 0, 35)
        self.boundary = None
        self.key_controller = None
        self.base_load()

    def base_load(self):
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)

    def random_level(self):
        self.arena = Arena()
        ConsolePresentation.show_arena(self.screen, self.arena.arena)
        ConsolePresentation.show_status(self.statistic_win,
                                        self.arena.spaces,
                                        self.arena.count_dots,
                                        self.arena.player_lives)
        self.key_controller.start()

    def run_game(self):
        level_path = os.path.join(LevelController.LEVEL_PATH, f'{self.level_number}.lvl')
        level_files = [x for x in filter(lambda x: x[-4:] == '.lvl', os.listdir(LevelController.LEVEL_PATH))]
        self.find_boundary()
        self.key_controller = KeyController(self.screen, self.arena_win, self.statistic_win, self.arena)
        self.key_controller.start()

        while self.level_number <= len(level_files) and self.arena.player_lives > 0 and self.key_controller.is_alive():
            self.arena.load_from_file(level_path)
            while self.arena.player_lives > 0 and \
                    self.key_controller.is_alive() and \
                    self.arena.running_game:
                self.show_arena()
                self.print_status()
                time.sleep(0.01)

            self.print_status()
            self.arena.stop()
            self.level_number += 1
            level_path = os.path.join(LevelController.LEVEL_PATH, f'{self.level_number}.lvl')

        self.arena.stop()
        self.key_controller.stop()

    def find_boundary(self):
        width = self.arena._width
        height = self.arena._height
        player_position = self.arena.player.position

        left = player_position.x - ARENA_WIN_W // 2
        left = max(left, 0)
        left_dist = abs(left - player_position.x)
        right = player_position.x + (ARENA_WIN_W - 2 - left_dist)
        if right > width and left > 0:
            left -= (right - width)
            right = width
            left = max(left, 0)

        up = player_position.y - ARENA_WIN_H // 2
        up = max(up, 0)
        up_dist = abs(up - player_position.y)
        down = player_position.y + (ARENA_WIN_H - 2 - up_dist)
        if down > height and up > 0:
            up -= (down - height)
            down = height
            up = max(up, 0)

        self.boundary = left, right, up, down
        return left, right, up, down

    def show_arena(self):
        self.find_boundary()
        ConsolePresentation.show_arena(
            self.arena_win,
            [line[self.boundary[0]:self.boundary[1]]
             for line in self.arena.arena][self.boundary[2]:self.boundary[3]]
        )

    def print_status(self):
        status = {
            'level_number': self.level_number,
            'remain_dots': self.arena.count_dots,
            'score': self.arena.score,
            'lives': self.arena.player_lives,
            'bonuses': [repr(x) for x in self.arena.bonuses]
        }
        ConsolePresentation.show_status(self.statistic_win, status)

    def close(self):
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()


class KeyController(threading.Thread):
    def __init__(self, screen, arena_win, statistic_win, arena):
        super().__init__()
        self.screen = screen
        self.arena_win = arena_win
        self.statistic_win = statistic_win
        self.arena = arena
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        while self.is_running:
            c = self.arena_win.getch()
            if c == ord('a'):
                self.arena.move_player("LEFT")

            if c == ord('d'):
                self.arena.move_player("RIGHT")

            if c == ord('w'):
                self.arena.move_player("UP")

            if c == ord('s'):
                self.arena.move_player("DOWN")

            if c == ord('`'):
                self.stop()
                self.arena.stop()

            time.sleep(self.arena.player_pause)
            curses.flushinp()

