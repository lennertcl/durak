from __future__ import annotations
from time import time


class Cheat():
    """ Abstract class containing information about a cheat

    Attributes:
        player: Player
            The player performing the cheat
        finish_time: int
            The time in seconds after which a cheat cannot be reverted anymore
        cheated_cards: dict(Player: list[Card])
            Dictionary holding information about every card that was thrown
            as a follow up cheat to this cheat (or follow ups of this cheat...)
    """

    # Seconds before a cheat cannot be reverted anymore
    DURATION = 5

    def __init__(self, player: Player):
        """ Initialize a cheat """
        self.player = player
        self.finish_time = time() + Cheat.DURATION
        self.cheated_cards = {}

    def add_follow_up_cards(self, player: Player, cards: list[Card]):
        """ Add cards to the dict of cards as follow up cheats for the cheat

        The cards are added into the dict of cheated cards.

        Args:
            player: Player
                The player throwing the cards
            cards: list[Card]
                The cards the player has thrown
        """
        if self.cheated_cards[player]:
            self.cheated_cards[player] += cards
        else:
            self.cheated_cards[player] = cards

    def __repr__(self):
        return f"Cheat ({self.player})"


class StealTrumpCard(Cheat):
    """ Class representing the stealing trump card cheat

    Attributes:
        old_trump_card: Card
            The old (stolen) trump card
    """

    def __init__(self, player: Player, old_trump_card: Card):
        Cheat.__init__(self, player)
        self.old_trump_card = old_trump_card

    def __repr__(self):
        return Cheat.__repr__(self) + " (steal trump card)"


class PutIntoDeck(Cheat):
    """ Class representing the putting cards into the deck cheat

    Attributes:
        cards_in_deck: list[Card]
            The cards put into the deck
    """

    def __init__(self, player: Player, cards_in_deck: list[Card]):
        Cheat.__init__(self, player)
        self.cards_in_deck = cards_in_deck

    def __repr__(self):
        return Cheat.__repr__(self) + " (put into deck)"


class ThrowIllegalCards(Cheat):
    """ Class representing the throwing illegal cards cheat """

    def __init__(self, player: Player, cards: list[Card]):
        Cheat.__init__(self, player)
        self.cheated_cards[player] = cards

    def __repr__(self):
        return Cheat.__repr__(self) + " (throw illegal cards)"


class PassIllegalCards(Cheat):
    """ Class representing the passing with illegal cards cheat """

    def __init__(self, player: Player, cheated_cards: list[Card]):
        Cheat.__init__(self, player)
        self.cheated_cards[player] = cheated_cards

    def __repr__(self):
        return Cheat.__repr__(self) + " (pass illegal cards)"


class BreakIllegalCards(Cheat):
    """ Class representing the breaking with illegal cards cheat

    Attributes:
        table_cards: dict(Card: Card)
            The table cards of the game on the moment of breaking cards
    """

    def __init__(self, player: Player, table_cards: dict[Card, Card]):
        Cheat.__init__(self, player)
        self.table_cards = table_cards

    def __repr__(self):
        return Cheat.__repr__(self) + " (break illegal cards)"
