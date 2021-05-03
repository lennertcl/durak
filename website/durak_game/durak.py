from .card import Card
from .player import Player
from .deck import Deck
from .cheat import Cheat

# Class representing a game of Durak
class DurakGame:

    # Initialize a game
    # @param id
    #   4 digit int id of the game
    # @param name
    #   The name given to the game
    def __init__(self, id, name):
        self.cards_per_player = 0
        self.id = id
        self.name = name
        self.deck = None
        self.lobby = [] # The players in the lobby
        self.players = [] # The players currently playing
        self.trump = None
        self.trump_card = None
        # The player currently receiving cards
        self.current_player = None
        # The cards currently on the table
        self.table_cards = {} 
        # Indicates whether the first card(s) of
        # the round have already been thrown
        self.throwing_started = False
        # Dict of cheaters with the cheat they
        # have performed
        self.cheating = {}
        # Indicates whether the previous and
        # next player have indicated that
        # they won't throw any more cards 
        # so the current player can break
        self.next_allows_break = False
        self.prev_allows_break = False

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

        # Initialize the deck
        self.deck = Deck(self.get_lowest_card())
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
        self.throwing_started = False

        self.next_allows_break = False
        self.prev_allows_break = False

    # If the deck is not empty, new cards are distributed
    # If the deck is empty, players that are finished are
    # transfered to the lobby
    # The current player is set to the next player
    # @param next_player
    #   Indicates whether the current player should
    #   be set to the next player
    def finish_round(self, has_broken=True):
        self.table_cards.clear()
        if not self.deck.is_empty():
            self.distribute_new_cards()
        # No else: need to check again because
        # the deck might have become empty
        if self.deck.is_empty():
            self.transfer_finished_players()
        if self.is_finished():
            # TODO ?
            pass
        # Update the current player
        if has_broken:
            # The current player has broken the cards,
            # it's his turn to throw cards
            self.current_player = self.next_player(
                self.current_player)
        else:
            # The current player has taken, he is not
            # allowed to throw cards
            self.current_player = self.next_player(
                self.next_player(self.current_player))
        # At the beginning of each round the throwing
        # has not started yet
        self.throwing_started = False
        # All cheats are cleared when the round finished
        # TODO Breaking cards cheat
        self.cheating.clear()
        # Reset the breaking allowed flags
        self.next_allows_break = False
        self.prev_allows_break = False

    # As long as there are cards in the deck, every
    # player gets back up to the starting amount of
    # cards
    def distribute_new_cards(self):
        player = self.current_player
        done = False
        while not done:
            while player.get_card_count() < self.cards_per_player and self.deck.cards:
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
        if not self.is_possible_throw_cards(cards):
            return False
        is_first_throw = False
        if not self.throwing_started:
            # At the beginning of each round, only the
            # player before the current receiving player
            # can throw cards
            if player == self.prev_player(self.current_player):
                is_first_throw = True
            else:
                return False
        if not self.is_legal_throw_cards(player, cards, is_first_throw):
            # TODO the player has cheated
            print("Illegal throw by {}".format(player))
            return False # Illegal for now
        # Goes here because first throw could have been 
        # illegal
        self.throwing_started = True
        # Throw the cards
        player.remove_cards(cards)
        for card in cards:
            self.table_cards[card] = None
        return True

    # It is not possible to throw more cards if the
    # player doesn't have enough cards to break them
    def is_possible_throw_cards(self, cards):
        cards_to_break = (sum([1 for card in self.table_cards
                              if not self.table_cards[card]])
                              + len(cards))
        return (cards_to_break
                <= self.current_player.get_card_count())

    # Test whether the given player can throw the
    # given cards without cheating
    # The player has to be one of the neighbors of
    # the current player and the symbol of each card 
    # to be thrown has to be present already
    def is_legal_throw_cards(self, player, cards, is_first_throw=False):
        if is_first_throw:
            # The player can only throw cards of the same symbol
            return (player == self.prev_player(self.current_player)
                and all(card.symbol == cards[0].symbol for card in cards))
        else:
            # A card with the same symbol has to be on the
            # table already
            for card in cards:
                if not(any((card.symbol == bottom_card.symbol 
                    or (top_card and card.symbol == top_card.symbol))
                    for bottom_card, top_card in self.table_cards.items())): 
                    return False
        # Only the neighbors can legally throw cards
        return (self.next_player(self.current_player) == player or
                self.prev_player(self.current_player) == player)


    # BREAKING CARDS


    #break a card on table that is not yet broken
    #@param bottom_card
    #   the to be broken card on the table
    #@param top_card
    #   the card that breaks the bottom card
    def break_card(self, bottom_card, top_card):
        # Breaking must be possible
        if not(self.is_possible_break_card(bottom_card, top_card)):
            return False
        self.table_cards[bottom_card] = top_card
        self.current_player.remove_cards([top_card])
        return True

    # Test whether the bottom card can break the top card
    # with the current board position
    def is_possible_break_card(self, bottom_card, top_card):
        # There may not already be another card on top
        return (bottom_card in self.table_cards 
            and (self.table_cards.get(bottom_card) is None))


    # Player breaks the cards on the table:
    # Clear the table
    def break_cards(self):
        if not self.is_possible_break_cards():
            return False
        if not self.is_legal_break_cards():
            # TODO this player has cheated
            print("Illegal breaking")
            return False # Illegal for now
        self.finish_round(has_broken=True)
        return True

    # Indicate that the given player has confirmed
    # that the current player can break
    def allow_break_cards(self, player):
        if player == self.next_player(self.current_player):
            self.next_allows_break = True
        if player == self.prev_player(self.current_player):
            self.prev_allows_break = True

    # Checks if the neighboring players of
    # the current player have confirmed that
    # the current player can break
    def is_possible_break_cards(self):
        return (self.next_allows_break and
                self.prev_allows_break)
    
    # Checks if a set of the played cards can 
    # break the cards on table
    def is_legal_break_cards(self):
        for bottom_card, top_card in self.table_cards.items():
            if not top_card:
                # There has to be a top card
                return False
            elif self.is_trump(top_card):
                # A trump card can break any card except a
                # higher trump card
                if (self.is_trump(bottom_card)
                    and bottom_card > top_card):
                    return False
            else:
                # A non trump card can only break lower
                # cards of the same suit
                if (bottom_card.get_suit() != top_card.get_suit()
                 or (bottom_card > top_card)):
                    return False
        return True

    # Move a top card to another bottom card
    def move_top_card(self, top_card, new_bottom_card):
        if not self.is_possible_move_top_card(top_card, new_bottom_card):
            return False
        # Get the old bottom card and remove it's top card
        bottom_card = list(self.table_cards.keys())[
            list(self.table_cards.values()).index(top_card)]
        self.table_cards[bottom_card] = None
        # Put the card on top of the new bottom card
        self.table_cards[new_bottom_card] = top_card
        return True

    # Test whether it is possible to move the given
    # top card to the new bottom card
    # The given top card must be a top card, the
    # bottom card must be a bottom card without
    # a top card on top
    def is_possible_move_top_card(self, top_card, new_bottom_card):
        return (top_card in self.table_cards.values() and
                new_bottom_card in self.table_cards and
                not self.table_cards[new_bottom_card])


    # TAKING CARDS


    # Player takes the cards on table:
    # Add the given cards to the player's current cards
    # and clear the table
    def take_cards(self):
        if not self.is_possible_take_cards():
            return False
        cards = []
        for bottom, top in self.table_cards.items():
            cards.append(bottom)
            if top:
                cards.append(top)
        self.current_player.add_cards(cards)
        self.finish_round(has_broken=False)
        return True

    # Taking cards is only possible if there is
    # at least 1 card on the table
    def is_possible_take_cards(self):
        return self.get_table_cards_count() > 0


    # PASSING ON


    #pass on the cards with given cards of the players own cards
    def pass_on(self, cards):
        if not self.is_possible_pass_on(cards):
            return False
        if not self.is_legal_pass_on(cards):
            # TODO cheated
            print("Illegal passing on")
            return False # Illegal for now
        for card in cards:
            self.table_cards[card] = None
        self.current_player.remove_cards(cards)
        self.current_player = self.next_player(self.current_player)
        return True

    # Pass on the cards making use of the trump card, without
    # passing on the trump card
    def pass_on_using_trump(self):
        if not self.is_possible_pass_on([]):
            return False
        if not self.is_legal_pass_on_using_trump():
            # TODO cheated
            print("Illegal passing on (trump)")
            return False # Illegal for now
        self.current_player = self.next_player(self.current_player)
        return True

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
    # There should be at least 1 card
    # The given cards and the cards on the table should all
    # be cards with the same symbol
    # There should be no broken cards
    def is_legal_pass_on(self, cards):
        if not cards:
            return False
        symbol = cards[0].symbol
        return (all(card.symbol == symbol for card in cards) and
                all(bottom_card.symbol == symbol and top_card is None 
                for bottom_card, top_card in self.table_cards.items()))

    # Test whether the current player can pas on the cards
    # to the next player using the trump card without cheating
    # All cards on the table should have the same symbol and
    # the current player should have the trump card of this
    # symbol
    def is_legal_pass_on_using_trump(self):
        if not self.table_cards:
            return False
        symbol = next(iter(self.table_cards)).symbol
        # Only cards of this type should be on the table
        if not all(bottom_card.symbol == symbol and top_card is None 
               for bottom_card, top_card in self.table_cards.items()):
            return False
        # Current player should have trump of this symbol
        return Card(self.trump, symbol) in self.current_player.cards


    # CHEATING


    # Players replaces the trump card with
    # one of his own cards
    def steal_trump_card(self, player, card):
        cheat = Cheat(Cheat.STEAL_TRUMP, self.trump_card)
        player.remove_cards([card])
        player.add_cards([self.trump_card])
        self.trump_card = card
        deck.add_card(card)
        self.cheating[player] = cheat

    # Player puts cards into the deck
    def put_into_deck(self, player, cards):
        cheat = Cheat(Cheat.PUT_INTO_DECK, cards)
        player.remove_cards(cards)
        self.deck.insert_cards(cards)
        self.cheating[player] = cheat


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

    # Get the lowest card for this game
    # The card is picked so that it is always
    # possible to give every player enough cards
    # but there are not too many cards in the deck
    def get_lowest_card(self):
        count = self.get_player_count()
        if count < 6:
            return Card.EIGHT - count
        return Card.TWO