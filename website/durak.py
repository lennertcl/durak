from random import shuffle

# Class representing a playing card
class Card():
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

    # Init a card
    # @param suit
    #   The suit of the card
    #   Card.HEARTS, Card.CLUBS, Card.DIAMONDS, Card.CLUBS
    # @param symbol
    #   The symbol/number of the card
    #   Card.TWO, Card.TEN, Card.JACK, Card.QUEEN,
    #   Card.KING, Card.ACE
    def __init__(self, suit, symbol):
        self.suit = suit
        self.symbol = symbol
    
    # String representation of the card
    def __repr__(self):
        return "Card {0} of {1}".format(
                    self.symbol, self.suit)

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

    # Return the image file of this card
    # e.g. '7H.png' for 7 of hearts
    def get_image(self):
        return "{0}{1}.png".format(self.symbol, self.suit)


# Class representing a deck of cards
class Deck():

    # Initialize a deck of cards with symbols
    # greater than or equal to the given lowest
    # card
    # @param lowest_card
    #   Member of Card.SYMBOLS
    #   The lowest card in the deck
    def __init__(self, lowest_card):
        self.cards = []
        for suit in Card.SUITS:
            for symbol in Card.SYMBOLS:
                if symbol >= lowest_card:
                    self.cards.append(Card(suit, symbol))
    
    # Return the amount of cards in this deck
    def get_card_count(self):
        return len(self.cards)

    # Shuffle the deck
    def shuffle(self):
        shuffle(self.cards)


# Class representing a player of the game
class Player():

    # Initialize a player
    # @param name
    #   The name of the player
    # @param id
    #   The id of the player
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.cards = []

    # Add the given cards to the player's cards
    def add_cards(self, new_cards):
        self.cards += new_cards


# Class representing a game of Durak
class DurakGame():

    # Initialize a game
    # @param lowest_card
    #   Like Deck.__init__ lowest_card
    def __init__(self, lowest_card):
        self.deck = Deck(lowest_card)
        self.players = []

    # Return the number of players in the game
    def get_player_count(self):
        return len(self.players)

    # Add a player to the game
    # @param player
    #   The player to add
    def add_player(self, player):
        self.players.append(player)

    # Start a game of durak
    # @param cards_per_player
    #   Initial amount of cards per player
    def start_game(self, cards_per_player=6):
        # Make sure there are enough cards
        if (self.get_player_count() * cards_per_player
            > self.deck.get_card_count()):
            raise ValueError("Too many cards per player")

        self.deck.shuffle()

        #Distribute the cards
        for player in self.players:
            cards = [self.deck.cards.pop() 
                     for _ in range(cards_per_player)]
            player.add_cards(cards)