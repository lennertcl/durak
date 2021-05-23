from website.durak_game.card import Card
from website.durak_game.player import Player
from website.durak_game.durak import DurakGame

from .fixtures import game


# POSSIBLE


def test_possible_take_cards_possible(game):
    """ Taking the cards is possible """
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.current_player
    
    game.throw_cards(p1, [p1.cards[0]])

    assert game.is_possible_take_cards(p2)

def test_possible_take_cards_impossible_player(game):
    """ The player taking the cards is not the current player """
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.current_player
    
    game.throw_cards(p1, [p1.cards[0]])

    assert not game.is_possible_take_cards(p1)

def test_possible_take_cards_impossible_no_cards(game):
    """ There are no cards on the table """
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.current_player
    
    assert not game.is_possible_take_cards(p2)


# PERFORMING TAKE CARDS


def test_take_no_top(game):
    """ There are no top cards """
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.current_player
    card = p1.cards[0]
    game.throw_cards(p1, [card])
    game.take_cards(p2)

    assert not game.table_cards

    assert p2.get_card_count() == 7
    assert p1.get_card_count() == 6