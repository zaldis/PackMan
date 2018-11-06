GAME_OBJECTS_PRESENTATION = {
    ' ': '·',
    '.': '*',
    'P': '@',
    'G': 'G',
    'W': '#'
}


class ConsolePresentation:
    @staticmethod
    def show_arena(screen, arena):
        screen.clear()
        height = len(arena)
        width = len(arena[0])

        for h in range(height):
            for w in range(width):
                screen.addstr(h, w, f"{GAME_OBJECTS_PRESENTATION[arena[h][w]]:2}")

        screen.refresh()

    @staticmethod
    def show_status(screen, taken_points: int, all_points: int, lives: int):
        screen.clear()
        screen.addstr(0, 0, f"Points: {taken_points}/{all_points}")
        screen.addstr(1, 0, f"Lives: {'@' * lives}")
        screen.refresh()

