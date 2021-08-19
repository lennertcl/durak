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
        game: DurakGame
            The game where the cheat has occurred
    """

    # Seconds before a cheat cannot be reverted anymore
    DURATION = 5

    def __init__(self, player: Player, game: DurakGame):
        """ Initialize a cheat """
        self.player = player
        self.finish_time = time() + Cheat.DURATION
        self.cheated_cards = {}
        self.game = game

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

    def can_rollback(self):
        return time() < self.finish_time

    def rollback(self):
        """ Rollback the cheat and all follow up cheats

        The cheated cards are added back into the player's hand
        The cheated cards are removed from the table cards
        """
        all_cheated_cards = []
        for player, cheated_cards in self.cheated_cards:
            player.add_cards(cheated_cards)
            all_cheated_cards += cheated_cards
        
        new_table_cards = {}
        for bottom_card, top_card in self.game.table_cards.items():
            contains_bottom = bottom_card in all_cheated_cards
            contains_top = top_card in all_cheated_cards

            if contains_bottom and contains_top:
                new_table_cards[bottom_card] = top_card
            elif contains_bottom:
                new_table_cards[bottom_card] = None

        self.game.table_cards = new_table_cards


    def __repr__(self):
        return f"Cheat ({self.player})"


class StealTrumpCard(Cheat):
    """ Class representing the stealing trump card cheat

    Attributes:
        old_trump_card: Card
            The old (stolen) trump card
    """

    def __init__(self, player: Player, game: DurakGame, old_trump_card: Card):
        Cheat.__init__(self, player, game)
        self.old_trump_card = old_trump_card

    def __repr__(self):
        return Cheat.__repr__(self) + " (steal trump card)"

    def rollback(self):
        """ Rollback the cheat

        The cheat is rolled back like a regular cheat
        The old trump card is replaced with the player's card
        """
        Cheat.rollback(self)
        self.player.add_cards(self.game.trump_card)
        self.game.trump_card = self.old_trump_card


class PutIntoDeck(Cheat):
    """ Class representing the putting cards into the deck cheat

    Attributes:
        cards_in_deck: list[Card]
            The cards put into the deck
    """

    def __init__(self, player: Player, game: DurakGame, cards_in_deck: list[Card]):
        Cheat.__init__(self, player, game)
        self.cards_in_deck = cards_in_deck

    def __repr__(self):
        return Cheat.__repr__(self) + " (put into deck)"

    def rollback(self):
        """ Rollback the cheat

        The cheat is rolled back like a regular cheat
        The cheated cards are removed from the deck
        The cheated cards are added to the player's hand
        """
        Cheat.rollback(self)
        self.game.deck.cards = [card for card in self.game.deck.cards 
                                if card not in self.cards_in_deck]
        self.player.add_cards(self.cards_in_deck)


class ThrowIllegalCards(Cheat):
    """ Class representing the throwing illegal cards cheat """

    def __init__(self, player: Player, game: DurakGame, cards: list[Card]):
        Cheat.__init__(self, player, game)
        self.cheated_cards[player] = cards

    def __repr__(self):
        return Cheat.__repr__(self) + " (throw illegal cards)"


class PassIllegalCards(Cheat):
    """ Class representing the passing with illegal cards cheat """

    def __init__(self, player: Player, game: DurakGame, cheated_cards: list[Card]):
        Cheat.__init__(self, player, game)
        self.cheated_cards[player] = cheated_cards

    def __repr__(self):
        return Cheat.__repr__(self) + " (pass illegal cards)"
