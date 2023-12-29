from dataclasses import dataclass


@dataclass
class Player:
    name: str = 'anonym'
    score: int = 0
