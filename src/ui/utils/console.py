from src.models import Player


def display_console_message(message: str) -> None:
    print(message)


def get_member_input_from_console(prompt: str = '') -> str:
    return input(f'({prompt})> ')


def get_statistic_in_ascii(players: list[Player], cnt: int = 3) -> str:
    top_players = sorted(players, key=lambda x: x.score, reverse=True)
    output = [
        f"{ind + 1:>3}) {top_players[ind].name:<20} {top_players[ind].score:<5}"
        for ind in range(min(cnt, len(top_players)))
    ]
    return "\n".join(output)
