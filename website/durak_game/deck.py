from random import shuffle

from .card import Card

class Deck:
    """Class representing a deck of cards
    
    Attributes:
        cards: List[Card]
            The cards in the deck
    """

    def __init__(self, lowest_card: int = Card.SIX):
        """Initialize the deck

        Only cards with symbols greater than or equal to the lowest card are
        created.

        Args:
            lowest_card: int
                The lowest card in the deck
        """
        self.cards = []
        for suit in Card.SUITS:
            for symbol in Card.SYMBOLS:
                if symbol >= lowest_card:
                    self.cards.append(Card(suit, symbol))
    
    def get_card_count(self) -> int:
        return len(self.cards)

    def shuffle(self):
        shuffle(self.cards)
        
    def add_card(self, card: Card):
        """Add a card to the bottom of the deck """
        self.cards.insert(0, card)

    def insert_cards(self, cards):
        """Insert cards at the top of the deck """
        self.cards += cards

    def is_empty(self) -> bool:
        return self.get_card_count() == 0