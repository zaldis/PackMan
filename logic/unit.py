import random
import threading


class _Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class GameObject:
    def __init__(self, position: _Point):
        self.position = position


DIRECTIONS = ['LEFT', 'RIGHT', 'UP', 'DOWN']


class _Unit(GameObject):
    pause = 3

    def __init__(self, position: _Point):
        super().__init__(position)
        self.direction = random.choice(DIRECTIONS)

    def pause_up(self, delta):
        self.pause += delta

    def pause_down(self, delta):
        self.pause_up(-delta)

    def move(self):
        if self.direction == 'LEFT':
            self.position.x -= 1
        if self.direction == 'RIGHT':
            self.position.x += 1
        if self.direction == 'UP':
            self.position.y -= 1
        if self.direction == 'DOWN':
            self.position.y += 1


class PackMan(_Unit):
    score = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lives = 3
        self.pause = 0.1
        self.score = 0
        self.bonuses = set()
        self.bonuses.add(SmartOpponentBonus(self, _Point(5, 7)))
        self.state = _NormalPackManState()

    def have_bonus(self, bonus_type):
        equal_bonuses = [y for y in filter(lambda x: type(x) == bonus_type, [x for x in self.bonuses])]
        return len(equal_bonuses) > 0

    def add_bonus(self, bonus):
        self.bonuses.add(bonus)

    def delete_bonus(self, bonus_type):
        target_bonuses = []
        for bonus in self.bonuses:
            if type(bonus) == bonus_type:
                target_bonuses.append(bonus)

        for bonus in target_bonuses:
            self.bonuses.remove(bonus)

    def to_normal(self):
        self.state = _NormalPackManState

    def to_hungry(self):
        self.state = _HungryPackManState

    def is_hungry(self):
        return isinstance(self.state, _HungryPackManState)


class _NormalPackManState:
    def __init__(self):
        self.eat = [Dot, Bonus]
        self.danger = [Ghost]


class _HungryPackManState:
    def __init__(self):
        self.eat = [Dot, Bonus, Ghost]
        self.danger = []


class Ghost(_Unit):
    score = 5

    def __init__(self, *args, code=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.pause = 1
        self.code = code


class _CounterMix(object):
    count_objects = 0

    def __init__(self):
        _CounterMix.count_objects += 1


class Bonus(_Unit, _CounterMix):
    score = 2

    def __init__(self, packman, *args, **kwargs):
        super(_Unit, self).__init__(*args, **kwargs)
        super(_CounterMix, self).__init__()
        self.packman = packman

    def apply(self):
        raise NotImplementedError()

    def destroy(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"I am bonus ;)"


class SpeedBonus(Bonus):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_pause = self.packman.pause

    def apply(self):
        with threading.Lock():
            self.packman.add_bonus(self)
            self.packman.pause = 1

    def destroy(self):
        with threading.Lock():
            self.packman.pause = self.initial_pause
            self.packman.delete_bonus(type(self))

    def __repr__(self):
        return f"slow speed bonus"


class HungryBonus(Bonus):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def apply(self):
        with threading.Lock():
            self.packman.add_bonus(self)
            self.packman.state = _HungryPackManState()

    def destroy(self):
        with threading.Lock():
            self.packman.state = _NormalPackManState()
            self.packman.delete_bonus(type(self))

    def __repr__(self):
        return f"hungry bonus"


class EnergizerBonus(Bonus):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def apply(self):
        with threading.Lock():
            self.packman.add_bonus(self)

    def destroy(self):
        with threading.Lock():
            self.packman.delete_bonus(type(self))


class LifeBonus(Bonus):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def apply(self):
        with threading.Lock():
            self.packman.lives += 1

    def destroy(self):
        pass


class SmartOpponentBonus(Bonus):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def apply(self):
        with threading.Lock():
            self.packman.add_bonus(self)

    def destroy(self):
        with threading.Lock():
            self.packman.delete_bonus(type(self))


class Dot(GameObject):
    score = 1


class Space(GameObject):
    score = 0


class Wall(GameObject):
    pass


class Door(GameObject):
    score = 10
