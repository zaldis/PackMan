import threading
import curses


GAME_OBJECTS_PRESENTATION = {
    ' ': '🔳',
    '.': '☕',
    'P': '🐱',
    'G': '👻',
    'W': '🛑',
    'B': '💎',
    'D': '🚪'
}

ARENA_WIN_H = 30
ARENA_WIN_W = 50

STATISTIC_WIN_H = 15
STATISTIC_WIN_W = 30


class ConsolePresentation:
    @classmethod
    def load(cls):
        cls.screen = curses.initscr()
        arena_start_x = curses.COLS // 2 - ARENA_WIN_W
        cls.arena_win = curses.newwin(ARENA_WIN_H + 1, ARENA_WIN_W + 1, 0, arena_start_x)
        cls.statistic_win = curses.newwin(STATISTIC_WIN_H, STATISTIC_WIN_W, 0, arena_start_x + ARENA_WIN_W + 40)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        cls.screen.keypad(True)

    @classmethod
    def close(cls):
        curses.nocbreak()
        cls.screen.keypad(False)
        curses.echo()
        curses.endwin()
        curses.curs_set(1)

    @classmethod
    def show_arena(cls, arena):
        with threading.Lock():
            cls.arena_win.clear()

            for h in range(len(arena)):
                for w in range(len(arena[0])):
                    cls.arena_win.addstr(h, w, f"{GAME_OBJECTS_PRESENTATION[arena[h][w]]}")

            cls.arena_win.refresh()

    @classmethod
    def show_status(cls, status: dict):
        cls.statistic_win.clear()
        level_number = status['level_number']
        cls.statistic_win.addstr(0, 0, f"Level: {level_number}")
        remain_dots = status['remain_dots']
        cls.statistic_win.addstr(1, 0, f"Remain dots: {remain_dots}")

        score = status['score']
        cls.statistic_win.addstr(3, 0, f"Score: {score}")
        lives = status['lives']
        cls.statistic_win.addstr(4, 0, f"Lives: {'♥ ' * lives}")

        cls.statistic_win.addstr(6, 0, "Bonuses:")
        bonuses = status['bonuses']
        for i, bonus in enumerate(bonuses):
            cls.statistic_win.addstr(7 + i, 0, f"{bonus}")

        cls.statistic_win.refresh()

    @classmethod
    def create_key_controller(cls, next_player_step):
        key_controller = KeyController(cls.arena_win, next_player_step)
        return key_controller


class KeyController(threading.Thread):
    def __init__(self, arena_win, next_player_step):
        super().__init__()
        self.arena_win = arena_win
        self.next_layer_step = next_player_step
        self.is_running = True

    def stop(self):
        self.is_running = False

    def run(self):
        while self.is_running:
            c = self.arena_win.getch()
            if c == ord('`'):
                self.stop()

            self.next_layer_step(c)
            curses.flushinp()
