import curses
import os
import threading
import time
from logic.arena import Arena
from presentation.console_presentation import ConsolePresentation


class LevelController:
    LEVEL_PATH = os.path.join('.', 'levels')

    def __init__(self):
        self.level_number = 1
        self.arena = Arena()
        self.screen = curses.initscr()
        self.statistic_win = curses.newwin(4, 30, 10, 60)
        self.key_controller = KeyController(self.screen, self.statistic_win, self.arena)
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
                                        self.arena.dots,
                                        self.arena.player_lives)
        self.key_controller.start()

    def next_level(self):
        level_path = os.path.join(LevelController.LEVEL_PATH, f'{self.level_number}.lvl')
        self.key_controller.start()

        while self.level_number <= 2 and self.arena.player_lives > 0:
            self.arena.load_from_file(level_path)
            while self.arena.player_lives > 0 and \
                    self.key_controller.is_alive() and \
                    self.arena.dots > 0:
                ConsolePresentation.show_arena(self.screen, self.arena.arena)
                ConsolePresentation.show_status(self.statistic_win,
                                                self.arena.spaces,
                                                self.arena.dots,
                                                self.arena.player_lives)
                time.sleep(0.1)

            ConsolePresentation.show_status(self.statistic_win,
                                            self.arena.spaces,
                                            self.arena.dots,
                                            self.arena.player_lives)

            self.arena.stop()
            self.level_number += 1
            level_path = os.path.join(LevelController.LEVEL_PATH, f'{self.level_number}.lvl')

        self.arena.stop()
        self.key_controller.stop()

    def close(self):
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()


class KeyController(threading.Thread):
    def __init__(self, screen, statistic_win, arena):
        super().__init__()
        self.screen = screen
        self.statistic_win = statistic_win
        self.arena = arena
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        while self.is_running:
            c = self.screen.getch()
            if c == ord('a'):
                self.arena.move_player("LEFT")
                ConsolePresentation.show_arena(self.screen, self.arena.arena)

            if c == ord('d'):
                self.arena.move_player("RIGHT")
                ConsolePresentation.show_arena(self.screen, self.arena.arena)

            if c == ord('w'):
                self.arena.move_player("UP")
                ConsolePresentation.show_arena(self.screen, self.arena.arena)

            if c == ord('s'):
                self.arena.move_player("DOWN")
                ConsolePresentation.show_arena(self.screen, self.arena.arena)

            if c == ord('`'):
                self.stop()
                self.arena.stop()

            ConsolePresentation.show_status(self.statistic_win,
                                            self.arena.spaces,
                                            self.arena.dots,
                                            self.arena.player_lives)

