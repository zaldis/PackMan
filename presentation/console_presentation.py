import threading
import time


GAME_OBJECTS_PRESENTATION = {
    ' ': '·',
    '.': '*',
    'P': '@',
    'G': 'G',
    'W': '#',
    'B': '?',
    'D': 'x'
}


class ConsolePresentation:
    @staticmethod
    def show_arena(screen, arena):
        with threading.Lock():
            screen.clear()
            height = len(arena)
            width = len(arena[0])

            for h in range(height):
                for w in range(width):
                    screen.addstr(h, w, f"{GAME_OBJECTS_PRESENTATION[arena[h][w]]}")

            screen.refresh()
            time.sleep(0.1)

    @staticmethod
    def show_status(screen, status: dict):
        screen.clear()
        level_number = status['level_number']
        screen.addstr(0, 0, f"Level: {level_number}")
        remain_dots = status['remain_dots']
        screen.addstr(1, 0, f"Remain dots: {remain_dots}")
        lives = status['lives']
        screen.addstr(2, 0, f"Lives: {'@' * lives}")
        screen.refresh()

