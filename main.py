from typing import Any, Callable

from src.controllers.level_controller import LevelController
from src.ui import console as console_ui
from src.models import Player
from src.repos.statistic import StatisticRepo, FileBasedStatisticRepo


class Runner:
    RUN = 'run'
    NAME = 'name'
    STATISTIC = 'stat'
    HELP = 'help'
    EXIT = 'exit'

    def __init__(
        self,
        display_message: Callable[[str], Any],
        get_member_input: Callable[[str], str],
        format_statistic: Callable[[list[Player], int], str],
        statistic_repo: StatisticRepo,
    ) -> None:
        self.name = 'anonym'

        self._display_message = display_message
        self._get_member_input = get_member_input
        self._format_statistic = format_statistic
        self._statistic_repo = statistic_repo

        self._menu_handlers= {
            Runner.RUN: (lambda: self._run_game()),
            Runner.NAME: (lambda: self._read_name()),
            Runner.HELP: (lambda: self._display_help()),
            Runner.STATISTIC: (lambda: self._display_statistic()),
        }

    def run(self):
        command = self._get_member_input(self.name)
        while command != Runner.EXIT:
            if handler := self._menu_handlers.get(command):
                handler()
            else:
                self._display_help()
            command = self._get_member_input(self.name)
        self._display_message('Bye ;)')

    def _read_name(self):
        self.name = self._get_member_input('Enter your name: ')

    def _display_help(self):
        message = (
            f"All commands:\n"
            f"\trun - start a new game\n"
            f"\texit - close the program\n"
            f"\tname - change name of the player\n"
            f"\tstat - call statistic of games\n"
            f"\thelp - call helper\n"
        )
        self._display_message(message)

    def _display_statistic(self):
        statistic_records = self._statistic_repo.get_records()
        self._display_message(
            self._format_statistic(statistic_records, 5)
        )

    def _run_game(self):
        level_controller = LevelController()
        score = level_controller.run_game()
        new_player = Player(self.name, score) 
        self._statistic_repo.add_record(new_player)


runner = Runner(
    display_message=console_ui.display_console_message,
    get_member_input=console_ui.get_member_input_from_console,
    format_statistic=console_ui.get_statistic_in_ascii,
    statistic_repo=FileBasedStatisticRepo()
)
runner.run()
