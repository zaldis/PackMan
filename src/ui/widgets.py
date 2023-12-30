from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol


class Widget(Protocol):
    parent: Optional['Widget'] = None

    def render(self) -> None:
        ...


@dataclass
class REPLCommand:
    name: str
    handler: Callable

class REPLWidget:
    parent: Optional['Widget'] = None

    def __init__(
        self,
        commands: list[REPLCommand],
        stop_command_name: str,
        render_help: Callable[[], Any],
        get_member_input: Callable[[], str],
        parent: Optional[Widget]=None,
    ) -> None:
        self._parent = parent
        self._handlers = { command.name: command.handler for command in commands }
        self._render_help = render_help
        self._get_member_input = get_member_input
        self._stop_command_name = stop_command_name

    @property
    def member_input_call(self) -> Callable[[], str]:
        return self._get_member_input

    @member_input_call.setter
    def member_input_call(self, new_call: Callable[[], str]) -> None:
        self._get_member_input = new_call

    def render(
        self,
    ) -> None:
        command = self._get_member_input()
        while command != self._stop_command_name:
            if handler := self._handlers.get(command):
                handler()
            else:
                self._render_help()
            command = self._get_member_input()

