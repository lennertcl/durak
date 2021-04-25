from time import time

# Class containing information about a cheat
class Cheat():

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

    # Initialize a cheat
    def __init__(self, cheat_type, revert_info):
        # The time after which the cheat cannot
        # be reverted anymore
        self.finish_time = time() + Cheat.DURATION
        self.cheat_type = cheat_type
        self.revert_info = revert_info


# NECESSARY REVERT INFO

# STEALING TRUMP CARD
#   Revert info contains only the
#   old trump card
# PUTTING CARDS INTO THE DECK
#   Revert info is a list of cards
#   put into the deck

# TODO These cheats can have follow up cheats
# THROWING ILLEGAL CARDS
# PASSING WITH ILLEGAL CARDS
# PASSING WITHOUT HAVING TRUMP
# BREAKING WITH ILLEGAL CARDS