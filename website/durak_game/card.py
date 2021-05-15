from __future__ import annotations

class Card:
    """Class representing a playing card

        Attributes:
            suit: str
                The suit of the card
            symbol: int
                The symbol of the card
    """
    # Constants representing suits
    HEARTS = "H"
    CLUBS = "C"
    DIAMONDS = "D"
    SPADES = "S"

    SUITS = [HEARTS, CLUBS, DIAMONDS, SPADES]

    # Constants representing symbols
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14 # Card.ACE > Card.KING

    SYMBOLS = [TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT,
               NINE, TEN, JACK, QUEEN, KING, ACE]

    @classmethod
    def from_str(cls, card_str: str) -> self:
        """Initialize a card from a string

        Examples: 
            Card.from_str("7H") == Card(Card.HEARTS, Card.SEVEN)
            Card.from_str("Card7H") == Card(Card.HEARTS, Card.SEVEN)
        
        Args:
            card_str: str
                String representation of the card

        Returns: Card
        """
        card_str = card_str.upper().replace("CARD", "")
        suit = card_str[-1]
        symbol = int(card_str[:-1])
        return cls(suit, symbol)

    def __init__(self, suit: str, symbol: int):
        """Initialize a card

        Args:
            suit: str
                The suit of the card
            symbol: int
                The symbol of the card
        """
        self.suit = suit
        self.symbol = symbol
    
    def __repr__(self) -> str:
        return "Card {0} of {1}".format(
                    self.symbol, self.suit)

    def __str__(self) -> str:
        """Return a string representation of the card

        Example: Card(Card.HEARTS, Card.SEVEN) -> '7H'
        """
        return "{0}{1}".format(self.symbol, self.suit)

    def __eq__(self, other: Card) -> bool:
        """Test for equality

        True if suit and symbol are equal
        """
        if isinstance(other, Card):
            return (self.symbol == other.symbol and
                    self.suit == other.suit)
        return False

    def __lt__(self, other: Card) -> bool:
        """Test for less than

        True if symbol is less than the other symbol
        """
        return self.symbol < other.symbol

    def __le__(self, other):
        """Test for less than or equal

        True if symbol is less than or equal to the other symbol
        """
        return self.symbol <= other.symbol
    
    def __gt__(self, other):
        """Test for greater than

        True if symbol is greater than the other symbol
        """
        return self.symbol > other.symbol

    def __ge__(self, other):
        """Test for greater than or equal

        True if symbol is greater than or equal to the other symbol
        """
        return self.symbol >= other.symbol

    def __hash__(self):
        return hash(self.suit) + hash(self.symbol)
    
    def get_suit(self):
        return self.suit
    
    def get_symbol(self):
        return self.symbol
    
    def get_image(self):
        """Return the image file of this card

        Example: Card(Card.HEARTS, Card.SEVEN) -> '7H.png'
        """
        return "{0}{1}.png".format(self.symbol, self.suit)