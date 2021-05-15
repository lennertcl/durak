from __future__ import annotations

class Player:
    """Class representing players of the game

    Attributes:
        username: str
            The username of the player.
            This is unique for each player. 
        cards: List[Card]
            The cards of this player.
        sid: str
            The session id of this player.
            Gets set when player joins a game.
    """

    # Mapping the number of players on the table to
    # the positions the players should be at
    POSITIONS = {
        1: (4,),
        2: (2, 6),
        3: (2, 4, 6),
        4: (1, 3, 5, 7),
        5: (1, 2, 4, 6, 7),
        6: (1, 2, 3, 5, 6, 7),
        7: (1, 2, 3, 4, 5, 6, 7),
    }

    def __init__(self, username: str):
        """ Initialize a player """
        self.username = username
        self.cards = []

    def __repr__(self):
        return "Player {}".format(self.username)

    def __str__(self):
        return "{}".format(self.username)
    
    def __eq__(self, other):
        return self.username == other.username

    def add_cards(self, new_cards: list[Card]):
        """ Add the given cards to the player's cards """
        self.cards += new_cards

    def remove_cards(self, cards: list[Card]):
        """ Remove the given cards from the player's cards """
        for card in cards:
            self.cards.remove(card)

    def get_card_count(self) -> int:
        return len(self.cards)

    def get_players_in_position(self, game: DurakGame, spectating: bool = False
                            ) -> List[Tuple[Player, int]]:
        """ Get the players and their seat number for the game in correct order

        Args:
            game: DurakGame
                The game to position the players for
            spectating: bool, optional
                Indicates whether the player is a spectating player,
                and thus does not take a seat in the game himself
                Defaults to False.
        """
        player_count = game.get_player_count()
        if not spectating:
            # The player should have the correct neighbors
            offset = game.players.index(self) + 1
            # This player does not count as another player,
            # but he was counted as a player
            player_count -= 1
        else:
            offset = 0
        # Seat positions for this game
        positions = Player.POSITIONS[player_count]
        other_players = []
        # Add every player and their seat number
        for i in range(0, player_count):
            idx = (offset + i) % (player_count + 1)
            other_players.append((game.players[idx], 
                                  positions[i]))
        return other_players