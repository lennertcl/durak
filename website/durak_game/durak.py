from .card import Card
from .player import Player
from .deck import Deck

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
        self.cards_per_player = 0
        self.id = id
        self.name = name
        self.deck = Deck(lowest_card)
        self.lobby = [] # The players in the lobby
        self.players = [] # The players currently playing
        self.trump = None
        self.current_player = None
        self.table_cards = {} # The cards currently on the table
        self.trump_card = None

    # Return the number of players in the lobby
    def get_lobby_count(self):
        return len(self.lobby)

    # Return the number of players in the game
    def get_player_count(self):
        return len(self.players)

    # Get player by username
    def get_player(self, username):
        for player in self.players + self.lobby:
            if player.username == username:
                return player

    # Get the amount of cards currently on the table
    # Both bottom and top cards are counted
    def get_table_cards_count(self):
        count = 0
        # There is always a bottom card, not always
        # a top card
        for _, top_card in self.table_cards.items():
            if top_card:
                count += 2
            else:
                count += 1
        return count

    # Add a player to the lobby of the game by username
    # @param username
    #   The usename of the player to add
    def add_player(self, username):
        # Only add the player if the player is not in the game yet
        if not(any(p.username == username for p in self.players)):
            player = Player(username)
            self.lobby.append(player)


    # GAME AND ROUNDS


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

    # If the deck is not empty, new cards are distributed
    # If the deck is empty, players that are finished are
    # transfered to the lobby
    # The current player is set to the next player
    def finish_round(self):
        if not(self.deck.is_empty()):
            self.distribute_new_cards()
        # No else: need to check again because
        # the deck might have become empty
        if self.deck.is_empty():
            self.transfer_finished_players()
        if self.is_finished():
            # TODO ?
            pass
        # Update the current player
        self.current_player = self.next_player(self.current_player)

    # As long as there are cards in the deck, every
    # player gets back up to the starting amount of
    # cards
    def distribute_new_cards(self):
        player = self.current_player
        done = False
        while not done:
            while player.get_card_count() < self.cards_per_player and self.deck:
                player.cards.append(self.deck.cards.pop())
            player = self.next_player(player)
            done = player == self.current_player
    
    # Players that don't have any cards left are transfered
    # to the lobby
    def transfer_finished_players(self):
        new_players = []
        for player in self.players:
            if player.get_card_count() == 0:
                self.lobby.append(player)
            else:
                new_players.append(player)
        self.players = new_players


    # BREAKING CARDS
    

    #break a card on table that is not yet broken
    #@param bottom_card
    #   the to be broken card on the table
    #@param top_card
    #   the card that breaks the bottom card
    def break_card(self, bottom_card, top_card):
        # Breaking must be possible
        if not(self.is_possible_break_card(bottom_card, top_card)):
            raise AssertionError("Bottom card not on table or card already broken")
        newdict = {bottom_card: top_card}
        self.table_cards.update(newdict)
        self.current_player.remove_cards([top_card])

    # Test whether the bottom card can break the top card
    # with the current board position
    def is_possible_break_card(self, bottom_card, top_card):
        return (bottom_card in list(self.table_cards.keys()) 
            and (self.table_cards.get(bottom_card) is None))

    # Player breaks the cards on the table:
    # Clear the table
    def break_cards(self):
        self.table_cards.clear()
        self.finish_round()
        if not self.can_break():
            # TODO this player has cheated
            print("{} has cheated".format(self.current_player))
    
    #checks if a set of the played cards can break the cards on table
    def can_break(self):
        breakable = True
        for i in self.table_cards.items():
            if i[1] is None:
                breakable = False
                break
            #legal way of breaking, may be removed to allow cheating
            elif not self.is_trump(i[1]):
                if (i[0].get_suit() != i[1].get_suit()) or (i[0] < i[1]):
                    breakable = False
                    break
        return breakable


    # THROWING CARDS


    # Player throws cards on table:
    # Remove the given cards from the player's
    # current cards and add the cards to the
    # cards on the table
    # @param player
    #   Player to remove cards of
    # @param cards
    #   List of cards to remove
    def throw_cards(self, player, cards):
        if not(self.is_possible_throw_cards(cards)):
            raise AssertionError("Too much cards thrown")
        if not self.is_legal_throw_cards(player, cards):
            # TODO the player has cheated
            pass
        player.remove_cards(cards)
        for card in cards:
            self.table_cards[card] = None

    # It is not possible to throw more cards if the
    # player doesn't have enough cards to break them
    def is_possible_throw_cards(self, cards):
        cards_to_break = sum([1 for card in self.table_cards
                              if card]) + len(cards)
        return (cards_to_break
                <= self.current_player.get_card_count())

    # Test whether the given player can throw the
    # given cards without cheating
    # The player has to be one of the neighbors of
    # the current player and the symbol of each card 
    # to be thrown has to be present already
    # TODO first move of round
    def is_legal_throw_cards(self, player, cards):
        for card in cards:
            if card not in self.table_cards:
                return False
        return (self.next_player(self.current_player) == player or
                self.prev_player(self.current_player) == player)


    # TAKING CARDS


    # Player takes the cards on table:
    # Add the given cards to the player's current cards
    # and clear the table
    def take_cards(self):
        cards = []
        for bottom, top in self.table_cards.items():
            cards.append(bottom)
            if top:
                cards.append(top)
        self.current_player.add_cards(cards)
        self.table_cards.clear()
        self.finish_round()


    # PASSING ON


    #pass on the cards with given cards of the players own cards
    def pass_on(self, cards):
        if not self.is_possible_pass_on(cards):
            raise AssertionError("Impossible pass on")
        for card in cards:
            self.table_cards[card] = None
        self.current_player.remove_cards(cards)
        self.current_player = self.next_player(self.current_player)

    # Pass on the cards making use of the trump card, without
    # passing on the trump card
    def pass_on_using_trump(self):
        if not self.is_possible_pass_on([]):
            raise AssertionError("Impossible pass on")
        self.current_player = self.next_player(self.current_player)

    # The amount of cards passed should not exceed the
    # amount of cards of the player passing to
    # There should be no top cards when passing on
    def is_possible_pass_on(self, cards):
        if (len(cards) + self.get_table_cards_count() >
           self.next_player(self.current_player).get_card_count()):
            return False
        return all(card is None for card in self.table_cards.values())

    # Test whether the current player can pass on the cards
    # to the next player without cheating
    # The given cards and the cards on the table should all
    # be cards with the same symbol
    # There should be no broken cards
    def is_legal_pass_on(self, cards):
        symbol = cards[0].symbol
        return (all(card.symbol == symbol for card in cards) and
                all(bottom_card.symbol == symbol and top_card is None 
                for bottom_card, top_card in self.table_cards))

    # Test whether the current player can pas on the cards
    # to the next player using the trump card without cheating
    # All cards on the table should have the same symbol and
    # the current player should have the trump card of this
    # symbol
    def is_legal_pass_on_using_trump(self):
        if not self.table_cards:
            return False
        symbol = self.table_cards.keys()[0].symbol
        return all(bottom_card.symbol == symbol and top_card is None 
               for bottom_card, top_card in self.table_cards)


    # HELPER FUNCTIONS


    #checks if a card is a trump
    def is_trump(self, card):
        return card.get_suit() == self.trump
    
    # Return the player playing after the given player
    def next_player(self, player):
        idx = self.players.index(player)
        return self.players[(idx + 1) % len(self.players)]

    # Return the player playing before the given player
    def prev_player(self, player):
        idx = self.players.index(player)
        return self.players[idx - 1]

    # Test whether the game is finished
    def is_finished(self):
        return self.get_player_count() == 1