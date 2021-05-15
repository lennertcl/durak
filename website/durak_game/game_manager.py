from time import time
from apscheduler.schedulers.background import BackgroundScheduler

from .durak import DurakGame

class GameManager:
    """ Class to manage current games for the site 

    Attributes:
        current_id: int
            The current id for the next game
        current_games: dict(int, DurakGame)
            Key: id, Value: game
            The current games for the site
    """

    # Maximum ID of a game (restarts at 1)
    MAX_ID = 10000
    # Time a game can last in seconds before it gets
    # removed by the garbage collector
    GAME_TIME = 3600
    # Interval in minutes after which games are removed 
    # by the garbage collector
    GARBAGE_COLLECTOR_INTERVAL = 60

    def __init__(self):
        """ Initialize a game manager """
        self.current_id = 3865
        self.current_games = {}
        self.start_garbage_collector()

    def create_game(self, name: str) -> DurakGame:
        """ Create a new durakgame with given name 

        Updates the current id.
        Creates the game, adds it to the current games and returns it.

        Returns: DurakGame
        """
        id = self.current_id
        self.current_id = (self.current_id + 1) % GameManager.MAX_ID
        game = DurakGame(id, name)
        self.current_games[id] = game
        return game

    def remove_game(self, game_id: int):
        del self.current_games[game_id]

    def collect_garbage(self):
        """ Removes all games that have passed the lifetime threshold """
        curr_time = time()
        for game_id, game in list(self.current_games.items()):
            if (game.timestamp + GameManager.GAME_TIME < curr_time):
                del self.current_games[game_id]

    def start_garbage_collector(self):
        """ Schedule a background job to delete games at set interval """
        sched = BackgroundScheduler(daemon=True)
        sched.add_job(self.collect_garbage, trigger="interval",
                      minutes=GameManager.GARBAGE_COLLECTOR_INTERVAL)
        sched.start()