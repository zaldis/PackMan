from controllers.level_controller import LevelController


PATH_STAT = 'stat.txt'


class Player(object):
    def __init__(self, name='anonym', score=0):
        self.name = name
        self.score = score


def read_players():
    players = []
    with open(PATH_STAT, 'r', encoding='utf-8') as file:
        for line in file:
            if line:
                name, score = line.split(',')
                players.append(Player(name=name, score=int(score)))

    return players


class Runner(object):
    RUN = 'run'
    NAME = 'name'
    STATISTIC = 'stat'
    HELP = 'help'
    EXIT = 'exit'

    def __init__(self):
        self.status = ''
        self.name = 'anonym'
        self.score = 0
        self.players = read_players()

    def run(self):
        status = input(f"({self.name})> ")
        while status != Runner.EXIT:
            if status == Runner.RUN:
                self._run_game()
                self.players.append(Player(self.name, self.score))
            elif status == Runner.NAME:
                self._read_name()
            elif status == Runner.HELP:
                self._print_help()
            elif status == Runner.STATISTIC:
                self.players.sort(key=lambda x: x.score, reverse=True)
                self._print_stat()

            status = input(f"({self.name})> ")

        self.players.sort(key=lambda x: x.score, reverse=True)
        with open(PATH_STAT, 'w', encoding='utf-8') as file:
            for ind in range(min(10, len(self.players))):
                file.write(f"{self.players[ind].name},{self.players[ind].score}\n")
        print('Bye ;)')

    def _read_name(self):
        self.name = input('Enter your name: ')

    def _print_help(self):
        print(f"All commands:\n"
              f"\trun - start a new game\n"
              f"\texit - close the program\n"
              f"\tname - change name of the player\n"
              f"\tstat - call statistic of games\n"
              f"\thelp - call helper\n")

    def _print_stat(self):
        for ind in range(min(10, len(self.players))):
            print(f"{ind + 1:>3}) {self.players[ind].name:<20} {self.players[ind].score:<5}")


    def _run_game(self):
        level_controller = LevelController()
        self.score = level_controller.run_game()


runner = Runner()
runner.run()
