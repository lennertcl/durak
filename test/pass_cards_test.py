import pytest

from website.durak_game.card import Card
from website.durak_game.player import Player
from website.durak_game.durak import DurakGame

from .fixtures import game


# POSSIBLE


def test_possible_pass_on_possible(game):
    """ Passing on the cards is possible """
    game.start_game()
    p = game.current_player

    cards = [Card(Card.CLUBS, Card.SEVEN)]
    p.add_cards(cards)

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None}

    assert game.is_possible_pass_on(p, cards)

def test_possible_pass_on_possible_trump(game):
    """ Passing on the cards is possible using the trump card """
    game.start_game()
    p = game.current_player

    p.add_cards([Card(Card.CLUBS, Card.SEVEN)])

    game.trump = Card.CLUBS

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None}

    assert game.is_possible_pass_on(p, [])


def test_possible_pass_on_not_current(game):
    """ Passing on cards by a player not the current player """
    game.start_game()
    p = game.next_player(game.current_player)

    cards = [Card(Card.CLUBS, Card.SEVEN)]
    p.add_cards(cards)

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None}

    assert not game.is_possible_pass_on(p, cards)
 
def test_possible_pass_on_too_much_cards(game):
    """ Passing on too much cards for the next player to break """
    game.start_game()
    p1 = game.current_player
    p2 = game.next_player(game.current_player)

    cards = [Card(Card.CLUBS, Card.SEVEN)]
    p1.add_cards(cards)
    p2.cards = [Card(Card.HEARTS, Card.NINE)]

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None}

    assert not game.is_possible_pass_on(p1, cards)

def test_possible_pass_on_already_broken(game):
    """ Passing on when there is already a top card on one of the cards """
    game.start_game()
    p = game.current_player

    cards = [Card(Card.CLUBS, Card.SEVEN)]
    p.add_cards(cards)

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): Card(Card.SPADES, Card.SEVEN)}

    assert not game.is_possible_pass_on(p, cards)


# LEGAL


# PERFORMING PASSING ON
