from .durak import DurakGame

# Class to manage current games for the site
class GameManager:

    MAX_ID = 10000

    # Initialize the game manager
    def __init__(self):
        # 4 digit integer id
        #   Random initial id
        self.current_id = 3865
        # Dictionary of current games
        #   key: id, value: game
        self.current_games = {}

    # Create a new DurakGame
    def create_game(self, name, lowest_card):
        # Increment the id
        id = self.current_id
        self.current_id = (self.current_id + 1) % GameManager.MAX_ID
        # Create the game and add to current games
        game = DurakGame(id, name, lowest_card)
        self.current_games[id] = game
        return game