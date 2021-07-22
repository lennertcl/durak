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


def test_legal_pass_on_legal(game):
    """ Passing on the cards is legal """
    game.start_game()

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None,
                        Card(Card.CLUBS, Card.SEVEN): None}

    cards = [Card(Card.SPADES, Card.SEVEN)]

    assert game.is_legal_pass_on(cards)

def test_legal_pass_on_illegal_no_cards(game):
    """ There are no cards given to pass on with """
    game.start_game()

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None,
                        Card(Card.CLUBS, Card.SEVEN): None}

    cards = []

    assert not game.is_legal_pass_on(cards)

def test_legal_pass_on_illegal_empty_table(game):
    """ There are no cards on the table """
    game.start_game()

    game.table_cards = dict()

    cards = [Card(Card.SPADES, Card.SEVEN)]

    assert not game.is_legal_pass_on(cards)

def test_legal_pass_on_illegal_different_symbol_table(game):
    """ Not all cards on the table have the same symbol """
    game.start_game()

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None,
                        Card(Card.CLUBS, Card.EIGHT): None}

    cards = [Card(Card.SPADES, Card.SEVEN)]

    assert not game.is_legal_pass_on(cards)

def test_legal_pass_on_illegal_different_symbol_given(game):
    """ Not all given cards have the same symbol as the cards on the table"""
    game.start_game()

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None,
                        Card(Card.CLUBS, Card.SEVEN): None}

    cards = [Card(Card.SPADES, Card.SEVEN), Card(Card.DIAMONDS, Card.EIGHT)]

    assert not game.is_legal_pass_on(cards)


# LEGAL USING TRUMP


def test_legal_pass_on_using_trump_legal(game):
    """ Passing on the cards is legal """
    game.start_game()
    p = game.current_player

    game.trump = Card.DIAMONDS

    p.add_cards([Card(Card.DIAMONDS, Card.SEVEN)])

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None,
                        Card(Card.CLUBS, Card.SEVEN): None}

    assert game.is_legal_pass_on_using_trump()

def test_legal_pass_on_using_trump_illegal_empty_table(game):
    """ There are no cards on the table """
    game.start_game()
    p = game.current_player

    game.trump = Card.DIAMONDS

    p.add_cards([Card(Card.DIAMONDS, Card.SEVEN)])

    game.table_cards = dict()

    assert not game.is_legal_pass_on_using_trump()

def test_legal_pass_on_using_trump_illegal_different_symbol_table(game):
    """ Not all cards on the table have the same symbol """
    game.start_game()
    p = game.current_player

    game.trump = Card.DIAMONDS

    p.add_cards([Card(Card.DIAMONDS, Card.SEVEN)])

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None,
                        Card(Card.CLUBS, Card.EIGHT): None}

    assert not game.is_legal_pass_on_using_trump()

def test_legal_pass_on_illegal_no_trump(game):
    """ The current player does not have the trump card of the symbol on the table"""
    game.start_game()
    p = game.current_player

    game.trump = Card.DIAMONDS

    p.cards = [Card(Card.DIAMONDS, Card.EIGHT), Card(Card.SPADES, Card.SEVEN)]

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None,
                        Card(Card.CLUBS, Card.SEVEN): None}

    assert not game.is_legal_pass_on_using_trump()


# PERFORMING PASSING ON


def test_pass_on(game):
    """ Passing on the cards """
    game.start_game()
    p = game.current_player

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None,
                        Card(Card.CLUBS, Card.SEVEN): None}

    card = Card(Card.SPADES, Card.SEVEN)
    p.cards = [card]

    is_passed_on = game.pass_on(p, [card])

    assert is_passed_on
    assert card in game.table_cards
    assert card not in p.cards
    assert game.current_player == game.next_player(p)

def test_pass_on_using_trump(game):
    """ Passing on the cards using trump """
    game.start_game()
    p = game.current_player

    game.trump = Card.DIAMONDS

    p.add_cards([Card(Card.DIAMONDS, Card.SEVEN)])

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): None,
                        Card(Card.CLUBS, Card.SEVEN): None}

    is_passed_on = game.pass_on_using_trump(p)
    
    assert is_passed_on
    assert game.current_player == game.next_player(p)
