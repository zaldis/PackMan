import os
import time

from src.logic.arena import Arena
from src.presentation.console_presentation import ConsolePresentation
from src.presentation.console_presentation import ARENA_WIN_H
from src.presentation.console_presentation import ARENA_WIN_W


class LevelController:
    LEVEL_PATH = os.path.join('.', 'src', 'levels')

    def __init__(self):
        self.level_number = 1
        self.arena = Arena()
        self.shower = ConsolePresentation
        self.boundary = None
        self.key_controller = None
        ConsolePresentation.load()

    def run_game(self):
        level_path = os.path.join(LevelController.LEVEL_PATH, f'{self.level_number}.lvl')
        level_files = [x for x in filter(lambda x: x[-4:] == '.lvl', os.listdir(LevelController.LEVEL_PATH))]
        self.find_boundary()
        self.key_controller = self.shower.create_key_controller(self.next_player_step)
        self.key_controller.start()

        while self.level_number <= len(level_files) and self.arena.player_lives > 0 and self.key_controller.is_alive():
            self.arena.load_from_file(level_path)
            while self.arena.player_lives > 0 and \
                    self.key_controller.is_alive() and \
                    self.arena.running_game:
                self.show_arena()
                self.print_status()
                time.sleep(0.1)

            self.print_status()
            self.arena.stop()
            self.level_number += 1
            level_path = os.path.join(LevelController.LEVEL_PATH, f'{self.level_number}.lvl')

        self.arena.stop()
        self.key_controller.stop()
        self.shower.close()
        return self.arena.player.score

    def next_player_step(self, button):
        if button == ord('a'):
            self.arena.move_player("LEFT")

        if button == ord('d'):
            self.arena.move_player("RIGHT")

        if button == ord('w'):
            self.arena.move_player("UP")

        if button == ord('s'):
            self.arena.move_player("DOWN")

        if button == ord('`'):
            self.arena.stop()
            self.shower.close()
            self.key_controller.stop()
        time.sleep(self.arena.player_pause)

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
        ConsolePresentation.show_status(status)
