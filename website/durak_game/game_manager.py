from time import time
from apscheduler.schedulers.background import BackgroundScheduler

from .durak import DurakGame

# Class to manage current games for the site
class GameManager:

    # Maximum ID of a game (restarts at 1)
    MAX_ID = 10000
    # Time a game can last in seconds before it gets
    # removed by the garbage collector
    GAME_TIME = 3600
    # Interval in minutes after which games are removed 
    # by the garbage collector
    GARBAGE_COLLECTOR_INTERVAL = 60

    # Initialize the game manager
    def __init__(self):
        # 4 digit integer id
        #   Random initial id
        self.current_id = 3865
        # Dictionary of current games
        #   key: id, value: game
        self.current_games = {}
        # Start the garbage collector removing
        # games that have outlived the game time
        self.start_garbage_collector()

    # Create a new DurakGame
    def create_game(self, name):
        # Increment the id
        id = self.current_id
        self.current_id = (self.current_id + 1) % GameManager.MAX_ID
        # Create the game and add to current games
        game = DurakGame(id, name)
        self.current_games[id] = game
        return game

    # Delete a game
    def remove_game(self, game_id):
        del self.current_games[game_id]

    # Remove all games that were started more than one
    # hour ago
    def collect_garbage(self):
        print("Removing garbage games")
        print(self.current_games)
        curr_time = time()
        for game_id, game in list(self.current_games.items()):
            print(game.timestamp)
            print(curr_time)
            if (game.timestamp + GameManager.GAME_TIME < curr_time):
                del self.current_games[game_id]
        print(self.current_games)

    # Schedules a background job to delete games
    # at set interval
    def start_garbage_collector(self):
        sched = BackgroundScheduler(daemon=True)
        sched.add_job(self.collect_garbage, trigger="interval",
                      minutes=GameManager.GARBAGE_COLLECTOR_INTERVAL)
        sched.start()