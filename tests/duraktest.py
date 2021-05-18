import pytest

from website.durak_game.card import Card
from website.durak_game.player import Player
from website.durak_game.durak import DurakGame

@pytest.fixture()
def game():
    game = DurakGame(3865, "testgame")
    p1 = Player("p1")
    p2 = Player("p2")
    p3 = Player("p3")
    p4 = Player("p4")
    game.add_player(p1)
    game.add_player(p2)
    game.add_player(p3)
    game.add_player(p4)

    return game


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


# THROWING


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


# BREAKING CARDS


# POSSIBLE

def test_possible_break_card_possible(game):
    """ Breaking is possible """
    game.start_game()

    game.table_cards.update({Card(Card.HEARTS, Card.SEVEN): None})

    assert game.is_possible_break_card(bottom_card=Card(Card.HEARTS, Card.SEVEN),
                                           top_card=Card(Card.HEARTS, Card.NINE))

def test_possible_break_card_impossible_not_present(game):
    """ The bottom card is not present """
    game.start_game()

    assert not game.is_possible_break_card(bottom_card=Card(Card.HEARTS, Card.SEVEN),
                                           top_card=Card(Card.HEARTS, Card.EIGHT))

def test_possible_break_card_impossible_already_broken(game):
    """ The bottom card is already broken """
    game.start_game()

    game.table_cards.update({Card(Card.HEARTS, Card.SEVEN): Card(Card.HEARTS, Card.EIGHT)})

    assert not game.is_possible_break_card(bottom_card=Card(Card.HEARTS, Card.SEVEN),
                                           top_card=Card(Card.HEARTS, Card.NINE))

# LEGAL

def test_legal_break_card_legal(game):
    """ The breaking of the card is legal """
    game.start_game()
    
    assert game.is_legal_break_card(game.current_player)

def test_legal_break_card_illegal_player(game):
    """ The breaking of the card is done by another player """
    game.start_game()
    
    assert not game.is_legal_break_card(game.prev_player(game.current_player))

# PERFORMING BREAK

"""
TODO fix these

# Test breaking a card
def test_break_legal(game):
    game.start_game()

    p1 = game.prev_player(game.current_player)
    p2 = game.current_player

    bottom_card = Card(Card.HEARTS, Card.SEVEN)
    top_card = Card(Card.HEARTS, Card.SEVEN)
    # Make sure the player can break the card
    p1.add_cards([bottom_card])
    p2.add_cards([top_card])

    game.throw_cards(p1, [bottom_card])
    game.break_card(bottom_card, top_card)

    assert game.table_cards[bottom_card] == top_card
    assert p2.get_card_count() == 6

# Test breaking a card when there is no bottom card
def test_break_no_bottom(game):
    game.start_game()
    p = game.current_player
    card = p.cards[0]

    is_broken = game.break_card(None, card)
    assert not is_broken
    assert card in p.cards
    assert not card in game.table_cards
    assert not card in list(game.table_cards.values())
    assert game.current_player == p

# Test breaking a card when there is already another
# card on top
def test_break_top_full(game):
    game.start_game()

    p1 = game.next_player(game.current_player)
    p2 = game.current_player

    bottom_card = Card(Card.HEARTS, Card.SEVEN)
    top_card = Card(Card.HEARTS, Card.SEVEN)
    # Make sure the player can break the card
    p1.add_cards([bottom_card])
    p2.add_cards([top_card])

    game.throw_cards(p1, [bottom_card])
    is_broken = game.break_card(bottom_card, top_card)

    assert not is_broken
    assert top_card in p2.cards
    assert game.current_player == p2

# Test taking cards without top cards
def test_take_no_top(game):
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.current_player
    card = p1.cards[0]
    game.throw_cards(p1, [card])
    game.take_cards()

    print(p1.cards)
    print(p2.cards)

    assert not game.table_cards

    assert p2.get_card_count() == 7
    assert p1.get_card_count() == 6

# Test taking cards with top cards

"""