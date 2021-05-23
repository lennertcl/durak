from website.durak_game.card import Card
from website.durak_game.player import Player
from website.durak_game.durak import DurakGame

from .fixtures import game


# IS POSSIBLE


def test_possible_throw_possible(game):
    """Test a possible throw"""
    game.start_game()
    p1 = game.prev_player(game.current_player)
    card = p1.cards[0]

    assert game.is_possible_throw_cards([card])

def test_possible_throw_impossible_too_much(game):
    """Too much cards for the player to break"""
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.current_player

    # Give p2 limited number of cards
    p2.cards = [Card(Card.HEARTS, Card.SEVEN)]
    p1.cards = [Card(Card.HEARTS, Card.EIGHT), 
                Card(Card.CLUBS, Card.EIGHT),
                Card(Card.SPADES, Card.EIGHT)]
    
    assert not game.is_possible_throw_cards(p1.cards)


# IS LEGAL


def test_legal_throw_legal_first_player(game):
    """ The first player throws the first card legally """
    game.start_game()
    p = game.prev_player(game.current_player)
    card = Card(Card.HEARTS, Card.SEVEN)
    p.add_cards([card])

    assert game.is_legal_throw_cards(p, [card], is_first_throw=True)

def test_legal_throw_legal_not_first_player(game):
    """ The other neighbor throws a card legally """
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.next_player(game.current_player)
    card_1 = Card(Card.HEARTS, Card.SEVEN)
    card_2 = Card(Card.CLUBS, Card.SEVEN)
    p1.add_cards([card_1])
    p2.add_cards([card_2])
    game.throw_cards(p1, [card_1])

    assert game.is_legal_throw_cards(p2, [card_2], is_first_throw=False)

def test_legal_throw_illegal_no_cards(game):
    """No cards are thrown"""
    game.start_game()
    p = game.prev_player(game.current_player)

    assert not game.is_legal_throw_cards(p, [], is_first_throw=True)

def test_legal_throw_illegal_player(game):
    """ The first card is thrown from an illegal player"""
    game.start_game()
    p = game.next_player(game.current_player)
    card = p.cards[0]

    assert not game.is_legal_throw_cards(p, [card], is_first_throw=True)

def test_legal_throw_illegal_different_cards(game):
    """ Two different symbol cards are thrown """
    game.start_game()
    p = game.prev_player(game.current_player)
    cards = [Card(Card.HEARTS, Card.SEVEN),
             Card(Card.CLUBS, Card.EIGHT)]
    p.add_cards(cards)

    assert not game.is_legal_throw_cards(p, cards, is_first_throw=True)

def test_legal_throw_illegal_not_present(game):
    """ The symbol that was thrown is not present """
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.next_player(game.current_player)
    card_1 = Card(Card.HEARTS, Card.SEVEN)
    card_2 = Card(Card.CLUBS, Card.EIGHT)
    p1.add_cards([card_1])
    p2.add_cards([card_2])
    game.throw_cards(p1, [card_1])

    assert not game.is_legal_throw_cards(p2, [card_2], is_first_throw=False)

def test_legal_throw_illegal_not_neighbor(game):
    """ The throwing player is not a neighbor of the current player """
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.next_player(game.next_player(game.current_player))
    card_1 = Card(Card.HEARTS, Card.SEVEN)
    card_2 = Card(Card.CLUBS, Card.SEVEN)
    p1.add_cards([card_1])
    p2.add_cards([card_2])
    game.throw_cards(p1, [card_1])

    assert not game.is_legal_throw_cards(p2, [card_2], is_first_throw=False)


# PERFORMING THROW


def test_throw_legal_first(game):
    """ Legal throw of the first card """
    game.start_game()
    p1 = game.prev_player(game.current_player)
    card = p1.cards[0]
    is_thrown = game.throw_cards(p1, [card])

    assert is_thrown
    assert card in game.table_cards
    assert p1.get_card_count() == 5

def test_throw_impossible_first(game):
    """ Impossible throw of first card """
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.current_player

    # Give p2 limited number of cards
    p2.cards = [Card(Card.HEARTS, Card.SEVEN)]
    p1.cards = [Card(Card.HEARTS, Card.EIGHT), 
                Card(Card.CLUBS, Card.EIGHT),
                Card(Card.SPADES, Card.EIGHT)]
    
    is_thrown = game.throw_cards(p1, p1.cards)

    assert not is_thrown
    assert p1.get_card_count() == 3
    for card in p1.cards:
        assert card not in game.table_cards