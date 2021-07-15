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


def test_finish_round_has_broken(game):
    """Test finishing of a round when a player has broken the cards"""
    game.start_game()
    p1 = game.current_player
    p2 = game.prev_player(p1)
    p3 = game.next_player(p1)

    p2.add_cards([Card(Card.HEARTS, Card.SEVEN)])
    p1.add_cards([Card(Card.HEARTS, Card.EIGHT)])

    game.throw_cards(p2, [Card(Card.HEARTS, Card.SEVEN)])
    game.break_card(p1, Card(Card.HEARTS, Card.SEVEN), Card(Card.HEARTS, Card.EIGHT))

    game.finish_round(has_broken=True)

    assert not game.table_cards

    assert game.current_player == p3

    for player in game.players:
        assert player.get_card_count() == 6

    assert not game.next_allows_break
    assert not game.prev_allows_break
    assert not game.throwing_started

    # TODO this might need a fix when cheats happened right at the end of a round
    assert not game.cheating


def test_finish_round_has_taken(game):
    """Test finishing of a round when a player has taken the cards"""
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.current_player
    p3 = game.next_player(game.next_player(p2))

    card = p1.cards[0]

    game.throw_cards(p1, [card])
    game.finish_round(has_broken=False)

    assert not game.table_cards

    assert game.current_player == p3

    for player in game.players:
        # This is also true for current player because we did not execute take cards
        assert player.get_card_count() == 6

    assert not game.next_allows_break
    assert not game.prev_allows_break
    assert not game.throwing_started

    # TODO this might need a fix when cheats happened right at the end of a round
    assert not game.cheating

def test_finish_round_deck_empty(game):
    """Test finishing a round where the deck has become empty"""
    pass

def test_finish_round_game_finished(game):
    """Test finishing a round where the game has finished"""
    pass

# REMOVE PLAYERS
# TODO