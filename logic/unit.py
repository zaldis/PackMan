import random


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lives = 3
        self.pause = 0
        self.state = _NormalPackManState

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
    def __init__(self, *args, code=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.pause = 1
        self.code = code


class Bonus(_Unit):
    def __init__(self, packman, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.packman = packman

    def apply(self):
        raise NotImplementedError()

    def destroy(self):
        raise NotImplementedError()


class SpeedBonus(Bonus):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_pause = self.packman.pause

    def apply(self):
        self.packman.pause = 1

    def destroy(self):
        self.packman.pause = self.initial_pause


class Dot(GameObject):
    pass


class Space(GameObject):
    pass


class Wall(GameObject):
    pass


class Door(GameObject):
    pass
