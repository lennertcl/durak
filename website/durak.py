from random import shuffle


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


# Class representing a deck of cards
class Deck:

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
        
    #add a card to the bottom of the deck
    def add_card(self, card):
        self.cards.insert(0, card)


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


# Class representing a game of Durak
class DurakGame:

    # Initialize a game
    # @param id
    #   4 digit int id of the game
    # @param name
    #   The name given to the game
    # @param lowest_card
    #   Like Deck.__init__ lowest_card
    def __init__(self, id, name, lowest_card=2):
        self.id = id
        self.name = name
        self.deck = Deck(lowest_card)
        self.lobby = [] # The players in the lobby
        self.players = [] # The players currently playing
        self.trump = None
        self.current_player = None
        self.table_cards = {} # The cards currently on the table

    # Return the number of players in the lobby
    def get_lobby_count(self):
        return len(self.lobby)

    # Return the number of players in the game
    def get_player_count(self):
        return len(self.players)

    # Get player by username
    def get_player(self, username):
        for player in self.players:
            if player.username == username:
                return player

    # Add a player to the lobby of the game by username
    # @param username
    #   The usename of the player to add
    def add_player(self, username):
        # Only add the player if the player is not in the game yet
        if not(any(p.username == username for p in self.players)):
            player = Player(username)
            self.lobby.append(player)

    # Start a game of durak
    # @param cards_per_player
    #   Initial amount of cards per player
    def start_game(self, cards_per_player=6):
        self.cards_per_player = cards_per_player

        # Transfer players from the lobby
        self.players += self.lobby
        self.lobby = []

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

        #Get the trump card and set the trump of the game
        self.trump_card = self.deck.cards.pop()
        self.trump = self.trump_card.get_suit()
        self.deck.add_card(self.trump_card)

        # Pick the first player (has lowest trump card)
        starting_player = self.players[0]
        lowest_trump = Card.ACE + 1
        for player in self.players:
            for card in player.cards:
                if (card.suit == self.trump and
                    card.symbol < lowest_trump):
                    starting_player = player
        self.current_player = starting_player

    # When the round is finished, as long as there
    # are cards in the deck, every player gets 
    # back up to the starting amount of cards
    # The current player is set to the next player
    def finish_round(self):
        player = self.current_player
        done = False
        while not done:
            while (player.get_card_count() < self.cards_per_player and self.deck):
                player.cards.append(self.deck.cards.pop())
            player = self.next_player(player)
            done = player == self.current_player
        self.current_player = self.next_player(self.current_player)
    
    #break a card on table that is not yet broken
    #@param bottom_card
    #   the to be broken card on the table
    #@param top_card
    #   the card that breaks the bottom card
    def break_card(self, bottom_card, top_card):
    try:
        assert bottom_card in list(self.table_cards.keys()) and (self.table_cards.get(bottom_card) is None):
        newdict = {bottom_card: top_card}
        self.table_card.update(newdict)
        sel.current_player.remove_cards([top_card])
    except AssertionError:
        print("Bottom card not on table or card already broken")
        
    # Player throws cards on table:
    # Remove the given cards from the player's
    # current cards and add the cards to the
    # cards on the table
    # @param player
    #   Player to remove cards of
    # @param cards
    #   List of cards to remove
    def throw_cards(self, player, cards):
        player.remove_cards(cards)
        for card in cards:
            self.table_cards[card] = None

    # Player takes the cards on table:
    # Add the given cards to the player's current cards
    # and clear the table
    # @param player
    #   Player to add cards to
    def take_cards(self, player):
        player.cards += self.table_cards.keys()
        self.table_cards.clear()
        self.finish_round()

    # Player breaks the cards on the table:
    # Clear the table
    def break_cards(self):
        try:
            assert can_break():
            self.table_cards.clear()
            self.finish_round()
        except AsserttionError:
            print("not all cards are broken")
    
    #checks if a set of the played cards can break the cards on table
    def can_break(self):
        breakable = True
        for i in self.table_cards.items():
            if i[1] is None:
                breakable = False
                break
            #legal way of breaking, may be removed to allow cheating
            elif not self.is_trump(i[1]):
                if (i[0].get_suit() != i[1].get_suit()) or (i[0].__lt__(i[1])):
                    breakable = False
                    break
        return breakable

    #checks if a card is a trump
    def is_trump(self, card):
        return card.get_suit() == self.trump
    
    #pass on the cards with a given cards of the players own cards
    def pass_on(self, cards):
        for card in cards:
            self.table_cards[card] = None
        self.current_player.remove_cards([cards])
        self.current_player = self.next_player(self.current_player)
    
    # Return the player playing after the given player
    def next_player(self, player):
        idx = self.players.index(player)
        return self.players[(idx + 1) % len(self.players)]


# Class to manage current games for the site
class GameManager:

    MAX_ID = 10000

    # Initialize the game manager
    def __init__(self):
        # 4 digit integer id
        #   Random initial id
        self.current_id = 3865
        # Dictionary of current games
        #   key: id, value: game
        self.current_games = {}

    # Create a new DurakGame
    def create_game(self, name, lowest_card):
        # Increment the id
        id = self.current_id
        self.current_id = (self.current_id + 1) % GameManager.MAX_ID
        # Create the game and add to current games
        game = DurakGame(id, name, lowest_card)
        self.current_games[id] = game
        return game
