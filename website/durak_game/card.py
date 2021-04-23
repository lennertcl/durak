# Class representing a playing card
class Card:
    # Constants representing suits
    #   'H' for hearts, 'D' for diamonds,
    #   'C' for clubs, 'S' for spades
    HEARTS = "H"
    CLUBS = "C"
    DIAMONDS = "D"
    SPADES = "S"

    SUITS = [HEARTS, CLUBS, DIAMONDS, SPADES]

    # Constants representing symbols
    #   2-10, 11 for Jack, 12 for Queen
    #   13 for King, 14 for Ace
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

    # Init a card from a string representation
    @classmethod
    def from_str(cls, card_str):
        card_str = card_str.upper().replace("CARD", "")
        suit = card_str[-1]
        symbol = int(card_str[:-1])
        return cls(suit, symbol)

    # Init a card
    # @param suit
    #   The suit of the card
    #   Card.HEARTS, Card.CLUBS, Card.DIAMONDS, Card.CLUBS
    # @param symbol
    #   The symbol/number of the card
    #   Card.TWO,.., Card.TEN, Card.JACK, Card.QUEEN,
    #   Card.KING, Card.ACE
    def __init__(self, suit, symbol):
        self.suit = suit
        self.symbol = symbol
    
    # Representation of the card
    def __repr__(self):
        return "Card {0} of {1}".format(
                    self.symbol, self.suit)

    # String notation of the card
    def __str__(self):
        return "{0}{1}".format(self.symbol,
                               self.suit)

    # Equal if both symbol and suit are equal
    def __eq__(self, other):
        return (self.symbol == other.symbol and
                self.suit == other.suit)

    # Less than
    # A card is less than another if its symbol is
    # less than the other card's symbol
    def __lt__(self, other):
        return self.symbol < other.symbol

    # Less than or equal
    # A card is less than or equal to another if 
    # its symbol is less than or equal to the other
    # card's symbol
    def __le__(self, other):
        return self.symbol <= other.symbol
    
    # Greater than
    # A card is greater than another if its symbol is
    # greater than the other card's symbol
    def __gt__(self, other):
        return self.symbol > other.symbol

    # Greater than or equal
    # A card is greater than or equal to another if 
    # its symbol is greater than or equal to the other
    # card's symbol
    def __ge__(self, other):
        return self.symbol >= other.symbol

    def __hash__(self):
        return hash(self.suit) + hash(self.symbol)
    
    #return the suit of the card
    def get_suit(self):
        return self.suit
    
    #return the symbol of the card
    def get_symbol(self):
        return self.symbol
    
    # Return the image file of this card
    # e.g. '7H.png' for 7 of hearts
    def get_image(self):
        return "{0}{1}.png".format(self.symbol, self.suit)