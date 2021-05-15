from time import time

class Cheat():
    """ Class containing information about a cheat 

    Attributes:
        finish_time: int
            The time in seconds after which a cheat cannot be reverted anymore
        cheat_type: int
            The type of the cheat
        revert_info : TODO
            Information necessary to revert this cheat
    """

    # Different types of cheats
    STEAL_TRUMP = 1
    PUT_INTO_DECK = 2
    THROW = 3
    PASS_CARD = 4
    PASS_TRUMP = 5
    BREAK = 6

    # Seconds before a cheat cannot be reverted
    # anymore
    DURATION = 5

    def __init__(self, cheat_type: int, revert_info):
        """ Initialize a cheat """
        self.finish_time = time() + Cheat.DURATION
        self.cheat_type = cheat_type
        self.revert_info = revert_info


"""
NECESSARY REVERT INFO

STEALING TRUMP CARD
    Revert info initially contains only the old trump card
    If this card is thrown into the game, further info is needed about
    other cards being thrown into the game
PUTTING CARDS INTO THE DECK
    Revert info is a list of cards
    put into the deck
THROWING ILLEGAL CARDS
PASSING WITH ILLEGAL CARDS
PASSING WITHOUT HAVING TRUMP
BREAKING WITH ILLEGAL CARDS
"""