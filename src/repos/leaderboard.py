from src.models import Player
from .base import Repo


class FileBasedLeaderboardRepo(Repo[Player]):
    def __init__(self, path: str = 'leaderboard.txt') -> None:
        self._path = path

    def get_records(self) -> list[Player]:
        players = []
        try:
            with open(self._path, 'r', encoding='utf-8') as file:
                for line in file:
                    if line:
                        name, score = line.split(',')
                        players.append(Player(name=name, score=int(score)))
        except FileNotFoundError:
            pass
        return players

    def add_record(self, new_record: Player) -> None:
        old_players = self.get_records()
        new_leaderboard = sorted([*old_players, new_record], key=lambda x: x.score, reverse=True)
        with open(self._path, 'w', encoding='utf-8') as file:
            for player in new_leaderboard:
                file.write(f"{player.name},{player.score}\n")
