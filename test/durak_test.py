import pytest

from website.durak_game.card import Card
from website.durak_game.player import Player
from website.durak_game.durak import DurakGame

from .fixtures import game


# GAME STATUS


def test_lobby(game):
    """ Test correct game initialization """
    assert game.get_lobby_count() == 4
    assert game.get_player_count() == 0

    game.start_game()

    assert game.get_lobby_count() == 0
    assert game.get_player_count() == 4

    for player in game.players:
        assert player.get_card_count() == game.cards_per_player


# START GAME
# TODO


# FINISH ROUND
# TODO