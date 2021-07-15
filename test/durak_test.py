import pytest

from website.durak_game.card import Card
from website.durak_game.player import Player
from website.durak_game.durak import DurakGame

from .fixtures import game


# START GAME


def test_start_game(game):
    """ Test correct starting of game """
    game.start_game()

    assert game.cards_per_player == 6

    assert game.get_lobby_count() == 0
    assert game.get_player_count() == 4

    assert game.deck is not None

    for player in game.players:
        assert player.get_card_count() == game.cards_per_player

    assert game.trump is not None
    assert game.trump in Card.SUITS
    assert game.trump_card is not None
    assert game.trump_card.get_suit() == game.trump

    assert game.current_player is not None

    assert not game.throwing_started
    assert not game.next_allows_break
    assert not game.prev_allows_break

    assert game.is_in_progress


# FINISH ROUND
# TODO


# REMOVE PLAYERS
# TODO