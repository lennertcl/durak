from __future__ import annotations
from time import time

from .card import Card
from .player import Player
from .deck import Deck
from .cheat import (Cheat, StealTrumpCardCheat, PutIntoDeckCheat, 
                    ThrowIllegalCardsCheat, PassIllegalCardsCheat)

class DurakGame:
    """ Class representing a game of Durak 
    
        Attributes:
            id: int
                4 digit id of the game
            name: str
            deck: Deck
            players: List(Player)
                List of players currently playing
            lobby: List(Player)
                List of players currently in the lobby
            trump: str
                The current trump suit of the game
            trump_card: Card
            cards_per_player: int
            current_player: Player
                The player currently receiving cards
            table_cards: dict(Card: Card)
                Key: bottom card, Value: top card
                The cards currently on the table
            throwing_started: bool
                Indicates whether the first card(s) of the round have already
                been thrown
            cheating : dict(Player: Cheat)
                Dict of cheaters with the cheat they have performed
            next_allows_break: bool
            prev_allows_break: bool
                Indicates whether the previous and next player have indicated 
                that they won't throw any more cards so the current player can
                break
            timestamp: int
                Timestamp of start of this game 
                (used for garbage collection of old games)
            is_in_progress: bool
                Indicates whether the game is currently in progress
    """

    MAX_PLAYERS = 8

    def __init__(self, id: int, name: str):
        """ Initialize a game

        Args: 
            id: int
                4 digit id of the game
            name: str
                The name given to the game
        """
        self.id = id
        self.name = name
        self.timestamp = time()
        self.lobby = [] 
        self.players = []
        self.table_cards = {} 
        self.cheating = {}
        self.throwing_started = False
        self.next_allows_break = False
        self.prev_allows_break = False
        self.is_in_progress = False

    def get_lobby_count(self) -> int:
        return len(self.lobby)

    def get_player_count(self) -> int:
        return len(self.players)

    def get_player(self, username: str) -> Player:
        for player in self.players + self.lobby:
            if player.username == username:
                return player

    def get_table_cards_count(self) -> int:
        """ Get the amount of cards currently on the table
        Both bottom and top cards are counted

        Returns: int
        """
        count = 0
        for _, top_card in self.table_cards.items():
            if top_card:
                count += 2
            else:
                count += 1
        return count


    def add_player(self, username: str):
        """Add a player to the lobby of the game by username
        The player is only added if not in the game yet

        Args:
            username: str
                The username of the player to add
        """
        if not(any(p.username == username for p in self.players)):
            player = Player(username)
            self.lobby.append(player)


    def remove_player(self, player: Player) -> bool:
        """Remove a player from the game

        If the player was inside the lobby, he is removed from the lobby. 
        If the player was playing the current game, he is removed from
        the game.
        If the player was the current player, the round is finished as
        if the leaving player took the cards on the table

        Args:
            player: Player
                The player leaving the game

        Returns: bool
            Indicates whether the game has gone to the next round
        """
        is_next_round = False
        if player in self.lobby:
            self.lobby.remove(player)
        if player in self.players:
            if player == self.current_player:
                self.finish_round(has_broken=False)
                is_next_round = True
            self.players.remove(player)
        return is_next_round


    # GAME AND ROUNDS


    def start_game(self, cards_per_player=6):
        """Start a game of durak

        The correct amount of cards per player is set.
        All players in the lobby are transfered to players in the game.
        The deck is initialized.
        Cards are distributed to every player.
        Trump and trump card are set.
        The first player is picked, this player has the lowest trump card.
        Allow break and throwing started indicators are set to False.
        The game is set to in progress.
        
        Args: 
            cards_per_player: int, optional
                Initial amount of cards per player, defaults to 6
        """
        self.cards_per_player = cards_per_player

        self.players += self.lobby
        self.lobby = []

        self.deck = Deck(self.get_lowest_card())
        self.deck.shuffle()

        for player in self.players:
            cards = [self.deck.cards.pop() 
                    for _ in range(cards_per_player)]
            player.add_cards(cards)

        self.trump_card = self.deck.cards.pop()
        self.trump = self.trump_card.get_suit()
        self.deck.add_card(self.trump_card)

        starting_player = self.players[0]
        lowest_trump = Card.ACE + 1
        for player in self.players:
            for card in player.cards:
                if (card.suit == self.trump and
                    card.symbol < lowest_trump):
                    starting_player = player
        # Next because this is the receiving player
        self.current_player = self.next_player(starting_player)

        self.throwing_started = False
        self.next_allows_break = False
        self.prev_allows_break = False
        self.is_in_progress = True


    def finish_round(self, has_broken: bool):
        """Finishes a round of the game

        All cards are removed from the table.
        If the deck is not empty, new cards are distributed.
        If the deck is empty / has become empty, players that are finished are 
        transfered to the lobby.
        If the game is finished, the in progress indicator is set to False,
        the cards of all remaining players are removed, and every player is
        removed from the players and added to the lobby.
        Otherwise, the current player is updated: if the current player has 
        broken, he is allowed to throw cards, otherwise he is not.
        Allow break and throwing started indicators are reset to False.
        All cheats are reset.

        Args: 
            has_broken: bool
                Indicates how the round was finished
                If true, the current player has broken the cards.
                If false, the current player has taken the cards.
        """
        self.table_cards.clear()

        if not self.deck.is_empty():
            self.distribute_new_cards()
        # No else: need to check again because the deck might have become empty
        if self.deck.is_empty():
            self.transfer_finished_players()

        if self.is_finished():
            self.is_in_progress = False

            for player in self.players:
                player.cards = []
                self.lobby.append(player)

            self.players = []
        else:
            if has_broken:
                self.current_player = self.next_player(self.current_player)
            else:
                self.current_player = self.next_player(self.next_player(self.current_player))

        self.throwing_started = False
        self.next_allows_break = False
        self.prev_allows_break = False

        self.cheating.clear()


    def distribute_new_cards(self):
        """New cards are distributed to the players

        As long as there are cards in the deck, every
        player gets back up to the starting amount of
        cards.
        """
        player = self.current_player
        done = False
        while not done:
            while player.get_card_count() < self.cards_per_player and self.deck.cards:
                player.cards.append(self.deck.cards.pop())
            player = self.next_player(player)
            done = player == self.current_player
    
    def transfer_finished_players(self):
        """Transfer players without cards to the lobby"""
        new_players = []
        for player in self.players:
            if player.get_card_count() == 0:
                self.lobby.append(player)
            else:
                new_players.append(player)
        self.players = new_players


    # THROWING CARDS


    def throw_cards(self, player: Player, cards: List[Card]) -> bool:
        """Player throws cards on table

        If the throw is impossible, nothing happens and False is returned.
        This behavior can change based on throwing_started indicator: 
        The first throw can only come from the player before the current player,
        not the player after the current player. 
        If the throw is illegal, a throw cards cheat is performed if possible.
        Otherwise:
        Remove the given cards from the player's current cards. 
        Add the cards to the cards on the table (as bottom cards).

        Args: 
            player: Player
                Player that has thrown the cards
            cards: List[Card]
                List of cards the player has thrown

        Returns: bool
            True if throwing of the cards has happened succesfully
            False if throwing of the cards did not happen
        """
        if not self.is_possible_throw_cards(cards):
            return False

        is_first_throw = False
        if not self.throwing_started:
            if player == self.prev_player(self.current_player):
                is_first_throw = True
            else:
                return False

        if not self.is_legal_throw_cards(player, cards, is_first_throw):
            was_successful_cheat = self.throw_illegal_cards(player, cards)
            if not was_successful_cheat:
                return False

        self.throwing_started = True

        player.remove_cards(cards)
        for card in cards:
            self.table_cards[card] = None
        return True


    def is_possible_throw_cards(self, cards: List[Card]) -> bool:
        """Test whether throwing the given cards onto the table is possible
        False if the player doesn't have enough cards to break every card.

        Args:
            cards: List[Card]
                List of cards thrown onto the table

        Returns: bool
        """
        cards_to_break = (sum([1 for card in self.table_cards
                              if not self.table_cards[card]])
                              + len(cards))
        return (cards_to_break
                <= self.current_player.get_card_count())


    def is_legal_throw_cards(self, player: Player, cards: List[Card],
                            is_first_throw: bool = False) -> bool:
        """Test whether cards can be thrown without cheating

        False if no cards are being thrown 
        (illegal because this can change the state of the game)
        If this is a first throw, False if not all cards are of the same symbol
        Otherwise, False if the symbol of one of the cards is not present yet.
        False if the player is not one of the neighbors of the current player.

        Args:
            player: Player
                The player throwing the cards
            cards: List[Card]
                The cards being thrown
            is_first_throw: bool, optional
                Indicates whether it is the first throw of the round
                Defaults to False

        Returns: bool
        """
        if not cards:
            return False

        if is_first_throw:
            return (player == self.prev_player(self.current_player)
                and all(card.symbol == cards[0].symbol for card in cards))
        else:
            for card in cards:
                if not(any((card.symbol == bottom_card.symbol 
                    or (top_card and card.symbol == top_card.symbol))
                    for bottom_card, top_card in self.table_cards.items())): 
                    return False

        return (self.next_player(self.current_player) == player or
                self.prev_player(self.current_player) == player)


    # BREAKING CARDS


    def break_card(self, player: Player, bottom_card: Card, 
                   top_card: Card) -> bool:
        """Break 1 card on the table

        If the break is impossible, nothing happens and False is returned.
        If the break is illegal, nothing happens and False is returned. TODO
        The top card is removed from the player's hand.
        The top card for the given bottom card is set to the given top card.

        Args: 
            player: Player
                The player breaking the card
            bottom_card: Card
                The to be broken card on the table
            top_card: Card
                The card that breaks the bottom card

        Returns: bool
            True if the break has happened succesfully
            False if the break did not happen
        """
        if not self.is_possible_break_card(bottom_card, top_card):
            return False
            
        if not self.is_legal_break_card(player):
            print(f"{player} tried to break illegally")
            return False

        self.table_cards[bottom_card] = top_card
        player.remove_cards([top_card])
        return True


    def is_possible_break_card(self, bottom_card: Card, top_card: Card) -> bool:
        """Test whether a break is possible

        False if the bottom card is not on the table as a bottom card.
        False if there is already another card on top of the bottom card.

        Args: 
            bottom_card: Card
                Bottom card of the break
            top_card: Card
                Top card of the break
        
        Returns: bool
        """
        return (bottom_card in self.table_cards 
           and (self.table_cards.get(bottom_card) is None))


    def is_legal_break_card(self, player: Player) -> bool:
        """Test whether a break is legal

        True if the breaking player is the current player of the game.

        Args:
            player: Player
                The player trying to break
        
        Returns: bool
        """
        return player == self.current_player


    def break_cards(self, player: Player) -> bool:
        """Break all cards on the table

        If breaking is not possible, nothing happens and False is returned.
        If breaking is illegal, nothing happens and False is returned. TODO
        The round is finished.

        Args: 
            player: Player
                The player breaking the cards
        
        Returns: bool
            True if breaking has happened succesfully
            False if breaking did not happen
        """
        if not self.is_possible_break_cards(player):
            return False
        if not self.is_legal_break_cards():
            print("Illegal breaking")
            return False # Illegal for now
        self.finish_round(has_broken=True)
        return True


    def is_possible_break_cards(self, player: Player) -> bool: 
        """Test whether breaking the cards is possible

        False if one of the neighbors has not allowed breaking yet.
        False if the player is not the current player.

        Args: 
            player: Player
                The player breaking the cards

        Returns: bool
        """
        return (self.next_allows_break and self.prev_allows_break 
            and self.current_player == player)
    

    def is_legal_break_cards(self) -> bool:
        """Checks if a set of the played cards can break the cards on table

        False if not every bottom card has a top card.
        True if every card is correctly broken:
            A card can only be broken by a card of the same suit with higher
            symbol or a trump card
            A trump card can only be broken by a higher card

        Returns: bool
        """
        for bottom_card, top_card in self.table_cards.items():
            if not top_card:
                return False
            elif self.is_trump(top_card):
                if (self.is_trump(bottom_card)
                    and bottom_card > top_card):
                    return False
            else:
                if (bottom_card.get_suit() != top_card.get_suit()
                 or (bottom_card > top_card)):
                    return False
        return True


    def allow_break_cards(self, player: Player) -> bool:
        """ Indicate an allow break by a player

        The flag is set based on whether the player is the previous / next
        player the current player

        Args:
            player: Player
                The player allowing breaking of cards

        Returns: bool
            True if the player has succesfully allowed breaking cards
        """
        allowed_break = False
        if player == self.next_player(self.current_player):
            self.next_allows_break = True
            allowed_break = True
        # No elif: if 2 players then next == prev
        if player == self.prev_player(self.current_player):
            self.prev_allows_break = True
            allowed_break = True
        return allowed_break


    def move_top_card(self, player: Player, top_card: Card,
                      new_bottom_card: Card) -> bool:
        """Move a top card to another bottom card

        If moving is not possible, nothing happens and False is returned.
        The top card is removed from the old bottom card.
        The top card is set as top card of the new bottom card.

        Args:
            player: Player
                The player moving the top card
            top_card: Card
                The top card being moved
            new_bottom_card: Card
                The card the top card is moved to

        Returns: bool
            True if moving has happened succesfully
            False if moving did not happen
        """
        if not self.is_possible_move_top_card(player, top_card, new_bottom_card):
            return False
        bottom_card = list(self.table_cards.keys())[
            list(self.table_cards.values()).index(top_card)]
        self.table_cards[bottom_card] = None
        self.table_cards[new_bottom_card] = top_card
        return True


    def is_possible_move_top_card(self, player: Player, top_card: Card,
                                  new_bottom_card: Card) -> bool:
        """Test whether moving the card is possible

        False if the player is not the current player
        False if the top card is not on the table as a top card
        False if the bottom card is not on the table as a bottom card
        False if the bottom card already has a top card on top

        Args:
            player: Player
                The player moving the card
            top_card: Card
                The top card being moved
            new_bottom_card: Card
                The card the bottom card is moved to

        Returns: bool
        """
        return (player == self.current_player and
                top_card in self.table_cards.values() and
                new_bottom_card in self.table_cards and
                not self.table_cards[new_bottom_card])


    # TAKING CARDS


    def take_cards(self, player: Player) -> bool:
        """Player takes the cards on the table

        If taking is not possible, nothing happens and false is returned.
        Every card on the table (bottom and top) is added to the cards of
        the player.
        The round is finished.

        Args:
            player: Player
                The player taking the cards

        Returns: bool
            True if taking has happened succesfully
            False if taking did not happen
        """
        if not self.is_possible_take_cards(player):
            return False
        cards = []
        for bottom, top in self.table_cards.items():
            cards.append(bottom)
            if top:
                cards.append(top)
        self.current_player.add_cards(cards)
        self.finish_round(has_broken=False)
        return True


    def is_possible_take_cards(self, player: Player) -> bool:
        """Test whether taking the cards is possible

        False if the player is not the current player.
        False if there are no cards on the table.

        Args:
            player: Player
                The player taking the cards

        Returns: bool
        """
        return (player == self.current_player and
                self.get_table_cards_count() > 0)


    # PASSING ON


    def pass_on(self, player: Player, cards: List[Card]) -> bool:
        """Pass on the cards to the next player using cards

        If passing on is not possible, nothing happens and False is returned.
        If passing on is illegal, a passing on cheat is performed if possible.
        The cards are added to the bottom cards of the table.
        The cards are removed from the hand of the current player.
        The player is updated to the next player. 

        Args:
            player: Player
                The player passing on cards
            card: List[Card]
                The cards being passed on

        Returns: bool
            True if passing on has happened succesfully
            False if passing on did not happen
        """
        if not self.is_possible_pass_on(player, cards):
            return False

        if not self.is_legal_pass_on(cards):
            was_successful_cheat = self.pass_illegal_cards(player, cards)
            if not was_successful_cheat:
                return False

        for card in cards:
            self.table_cards[card] = None
        self.current_player.remove_cards(cards)
        self.current_player = self.next_player(self.current_player)
        return True


    def pass_on_using_trump(self, player) -> bool:
        """Pass on the cards to the next player using trump card

        If passing on is not possible, nothing happens and False is returned.
        If passing on is illegal, a passing on cheat is performed if possible.
        The player is updated to the next player. 

        Args:
            player: Player
                The player passing on cards
            card: List[Card]
                The cards being passed on

        Returns: bool
            True if passing on has happened succesfully
            False if passing on did not happen
        """
        if not self.is_possible_pass_on(player, []):
            return False

        if not self.is_legal_pass_on_using_trump():
            was_successful_cheat = self.pass_illegal_cards(player, [])
            if not was_successful_cheat:
                return False

        self.current_player = self.next_player(self.current_player)
        return True


    def is_possible_pass_on(self, player: Player, cards: List[Card]) -> bool:
        """Test whether passing on is possible

        False if the player is not the current player.
        False if the amount of cards on the table combined with the new cards
        exceeds the number of cards of the next player.
        False if there is a top card on top of one of the bottom cards.

        Args:
            player: Player
                The player taking the cards

        Returns: bool
        """
        if player != self.current_player:
            return False
        if (len(cards) + self.get_table_cards_count() >
           self.next_player(self.current_player).get_card_count()):
            return False
        return all(card is None for card in self.table_cards.values())


    def is_legal_pass_on(self, cards: List[Card]) -> bool:
        """Test whether passing on is legal

        False if no cards are given
        False if there are no cards on the table.
        False if not all cards on the table have the same symbol.
        False if not all given cards have the same symbol as cards on the table.

        Args:
            cards: List[Card]
                The cards used to pass on

        Returns: bool
        """
        if not cards:
            return False
        if not self.table_cards:
            return False
        symbol = next(iter(self.table_cards)).symbol
        return (all(card.symbol == symbol for card in cards)
            and all(bottom_card.symbol == symbol
                for bottom_card, _ in self.table_cards.items()))


    def is_legal_pass_on_using_trump(self) -> bool:
        """Test whether passing on using trump is legal

        False if there are no cards on the table.
        False if not all cards on the table have the same symbol.
        False if the player does not have the trump of this symbol.

        Returns: bool
        """
        if not self.table_cards:
            return False
        symbol = next(iter(self.table_cards)).symbol
        if not all(bottom_card.symbol == symbol and top_card is None 
               for bottom_card, top_card in self.table_cards.items()):
            return False
        return Card(self.trump, symbol) in self.current_player.cards


    # CHEATING


    def can_call_other_player_cheat(self, player: Player) -> bool:
        """Check whether a player can call somebody out for cheating"""
        return player.last_cheat_call < time() - Cheat.DURATION


    def call_other_player_cheat(self, calling_player: Player, cheating_player: Player):
        """Call out another player for cheating

        If the player was cheating and the cheat can be rolled back, the cheat
        is rolled back, otherwise the cheat is removed
        The last cheat call time of the calling player is updated

        Args:
            calling_player: Player
                The player calling the cheater out
            cheating_player: Player
                The player getting called out
        """
        if not self.can_call_other_player_cheat(calling_player):
            return

        cheat = self.cheating[cheating_player]
        if cheat and cheat.can_rollback():
            self.cheating[cheating_player].rollback()
        if cheat:
            del self.cheating[cheating_player]

        calling_player.last_cheat_call = time()


    def can_cheat(self, player: Player) -> bool:
        if player in self.cheating:
            return not self.cheating[player].can_rollback()
        return True


    def steal_trump_card(self, player: Player, card: Card) -> bool:
        """Player replaces the trump card with one of his own cards

        The cheat is added to the cheating info.
        The card is removed from the player's cards.
        The trump card is added to the player's cards.
        The trump card is set to the given card.
        The given card is added to the deck.

        Args:
            player: Player
                The player stealing the trump card
            card: Card
                The card to replace the trump card with
        
        Returns: bool
        """
        if not self.can_cheat(player):
            return False

        cheat = StealTrumpCardCheat(player, self, self.trump_card)
        self.cheating[player] = cheat

        player.remove_cards([card])
        player.add_cards([self.trump_card])

        self.trump_card = card
        self.deck.add_card(card)

        return True


    def put_into_deck(self, player: Player, cards: List[Card]) -> bool:
        """Player puts his own cards into the deck

        The cheat is added to the cheating info.
        The cards are removed from the player's cards.
        The cards are added to the deck.

        Args: 
            player: Player
                The player putting cards into the deck
            cards: List[Card]
                The cards put into the deck
        
        Returns: bool
        """
        if not self.can_cheat(player):
            return False

        cheat = PutIntoDeckCheat(player, self, cards)
        self.cheating[player] = cheat

        player.remove_cards(cards)
        self.deck.insert_cards(cards)

        return True

    
    def throw_illegal_cards(self, player: Player, cards: List[Card]) -> bool:
        """ Player throws illegal cards on the table

        This should only be called from the throw_cards function.
        The cheat is added to the cheating info.
        """
        if not self.can_cheat(player):
            return False

        cheat = ThrowIllegalCardsCheat(player, self, cards)
        self.cheating[player] = cheat

        return True

    
    def pass_illegal_cards(self, player: Player, cards: List[Card]) -> bool:
        """ Player passes on cards illegally

        This should only be called from the pass_on / pass_on_using_trump functions.
        The cheat is added to the cheating info.
        """
        if not self.can_cheat(player):
            return False

        cheat = PassIllegalCardsCheat(player, self, cards)
        self.cheating[player] = cheat

        return True


    # HELPER FUNCTIONS


    def is_trump(self, card: Card) -> bool:
        return card.get_suit() == self.trump
    
    def next_player(self, player: Player) -> Player:
        try:
            idx = self.players.index(player)
            return self.players[(idx + 1) % len(self.players)]
        except ValueError:
            return None

    def prev_player(self, player: Player) -> Player:
        try:
            idx = self.players.index(player)
            return self.players[idx - 1]
        except ValueError:
            return None

    def is_finished(self) -> bool:
        return self.get_player_count() == 1
    
    def is_full(self) -> bool:
        return (self.get_player_count() + self.get_lobby_count() >=
                DurakGame.MAX_PLAYERS)

    def get_lowest_card(self) -> int:
        """Get the lowest card for this game

        The card is picked so that it is always possible to give every player
        enough cards, but there are not too many cards in the deck

        Returns: int
            The lowest card symbol for this game
        """
        count = self.get_player_count()
        if count < 6:
            return Card.EIGHT - count
        return Card.TWO
