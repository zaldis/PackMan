from typing import Any, Callable, cast
from abc import ABC, abstractmethod

from src.controllers.level_controller import LevelController
from src.ui.utils import console as console_utils
from src.models import Player
from src.repos.statistic import StatisticRepo, FileBasedStatisticRepo
from src.ui.widgets import Widget, REPLWidget, REPLCommand


class BasePackManRunner(ABC):
    root_widget: Widget

    def __init__(
        self,
        format_statistic: Callable[[list[Player], int], str],
        statistic_repo: StatisticRepo,
    ) -> None:
        self.name = 'anonym'
        self._format_statistic = format_statistic
        self._statistic_repo = statistic_repo

        self.setup_root_widget()

    def run(self):
        self.root_widget.render()
        self.render_message('Bye ;)')

    def setup_root_widget(self):
        pass

    @abstractmethod
    def render_message(self, message: str) -> Any:
        ...

    @abstractmethod
    def get_member_input(self, prompt: str) -> str:
        ...

    def start_new_game(self):
        level_controller = LevelController()
        score = level_controller.run_game()
        new_player = Player(self.name, score) 
        self._statistic_repo.add_record(new_player)

    def setup_player_name(self):
        self.name = self.get_member_input('Enter your name: ')

    def render_help(self):
        message = (
            f"All commands:\n"
            f"\tplay - start a new game\n"
            f"\texit - close the program\n"
            f"\tname - change name of the player\n"
            f"\tchamps - returns game's champions\n"
            f"\thelp - call helper\n"
        )
        self.render_message(message)

    def render_leaderboard(self):
        statistic_records = self._statistic_repo.get_records()
        self.render_message(
            self._format_statistic(statistic_records, 5)
        )


class ConsolePackManRunner(BasePackManRunner):
    def setup_root_widget(self) -> None:
        commands = [
            REPLCommand(name='play', handler=(lambda: self.start_new_game())),
            REPLCommand(name='name', handler=(lambda: self.setup_player_name())),
            REPLCommand(name='champs', handler=(lambda: self.render_leaderboard())),
        ]
        self.root_widget = REPLWidget(
            commands=commands,
            stop_command_name='exit',
            render_help=(lambda: self.render_help()),
            get_member_input=(lambda: self.get_member_input(f'{self.name}')),
        )

    def setup_player_name(self):
        super().setup_player_name()
        cast(REPLWidget, self.root_widget).member_input_call = (
            lambda: self.get_member_input(f'{self.name}')
        )

    def render_message(self, message: str) -> Any:
        return console_utils.display_console_message(message)

    def get_member_input(self, prompt: str) -> str:
        return console_utils.get_member_input_from_console(prompt)


runner = ConsolePackManRunner(
    format_statistic=console_utils.get_statistic_in_ascii,
    statistic_repo=FileBasedStatisticRepo()
)
runner.run()
