# Class representing a player of the game
class Player:

    # Initialize a player
    # @param username
    #   The username of the player
    def __init__(self, username):
        self.username = username
        self.cards = []

    def __repr__(self):
        return "Player {}".format(self.username)

    def __str__(self):
        return "{}".format(self.username)

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