# Class representing a player of the game
class Player:

    # Mapping the number of players on the table to
    # the positions the players should be at
    POSITIONS = {
        1: (4,),
        2: (2, 6),
        3: (2, 4, 6),
        4: (1, 3, 5, 7),
        5: (1, 2, 4, 6, 7),
        6: (1, 2, 3, 5, 6, 7),
        7: (1, 2, 3, 4, 5, 6, 7),
    }

    # Initialize a player
    # @param username
    #   The username of the player
    def __init__(self, username):
        self.username = username
        self.cards = []
        # This gets set when user joins a game
        self.sid = None

    def __repr__(self):
        return "Player {}".format(self.username)

    def __str__(self):
        return "{}".format(self.username)
    
    # Usernames are unique
    def __eq__(self, other):
        return self.username == other.username

    # Add the given cards to the player's cards
    # @param new_cards
    #   List of cards to add
    def add_cards(self, new_cards):
        self.cards += new_cards

    # Remove the given cards from the player's
    # cards
    # @param cards
    #   List of cards to remove
    def remove_cards(self, cards):
        for card in cards:
            self.cards.remove(card)

    # Get the amount of cards of this player
    def get_card_count(self):
        return len(self.cards)

    # Get the players and their seat number for the game
    # in correct order
    def get_players_in_position(self, game):
        # The player should have the correct neighbors
        offset = game.players.index(self) + 1
        player_count = game.get_player_count()
        # Seat positions for this game
        positions = Player.POSITIONS[player_count - 1]
        other_players = []
        # Add every player and their seat number
        for i in range(0, player_count - 1):
            idx = (offset + i) % player_count
            other_players.append((game.players[idx], 
                                  positions[i]))
        return other_players