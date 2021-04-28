import pytest

from website.durak_game.card import Card
from website.durak_game.player import Player
from website.durak_game.durak import DurakGame

@pytest.fixture()
def game():
    game = DurakGame(3865, "testgame", 5)
    p1 = Player("p1")
    p2 = Player("p2")
    p3 = Player("p3")
    game.add_player(p1)
    game.add_player(p2)
    game.add_player(p3)
    return game

# Test game initialization
def test_lobby(game):
    assert game.get_lobby_count() == 3
    assert game.get_player_count() == 0

    game.start_game()

    assert game.get_lobby_count() == 0
    assert game.get_player_count() == 3

    for player in game.players:
        assert player.get_card_count() == game.cards_per_player


# THROWING


# Test throwing the first card
def test_throw_legal_first(game):
    game.start_game()
    p1 = game.next_player(game.current_player)
    card = p1.cards[0]
    game.throw_cards(p1, [card])

    assert card in game.table_cards

    assert p1.get_card_count() == 5

# Test throwing a card where the symbol
# of the card thrown is already in the
# bottom cards
def test_throw_legal_bottom(game):
    pass

# Test throwing a card where the symbol
# of the card thrown is already in the
# top cards
def test_throw_legal_top(game):
    pass

# Test throwing two cards where the symbol
# of 1 card thrown is already in the
# top cards and the other is already
# in the bottom cards
def test_throw_legal_both(game):
    pass

# Test throwing a card from a user that
# is not a neighbor of the current player
def test_throw_illegal_not_neighbor(game):
    pass

# Test throwing a card of a symbol that is
# not on the table yet
def test_throw_illegal_not_on_table(game):
    pass

# Test throwing the first card from the
# wrong neighbor
def test_throw_illegal_first(game):
    pass


# BREAKING CARDS


# Test breaking a card
def test_break_legal(game):
    game.start_game()

    p1 = game.next_player(game.current_player)
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

    with pytest.raises(AssertionError):
        game.break_card(None, p.cards[0])

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
    game.break_card(bottom_card, top_card)
    with pytest.raises(AssertionError):
        game.break_card(bottom_card, top_card)

# Test taking cards without top cards
def test_take_no_top(game):
    game.start_game()
    p1 = game.next_player(game.current_player)
    p2 = game.current_player
    cards = p1.cards[:2]
    game.throw_cards(p1, cards)
    game.take_cards()

    print(p1.cards)
    print(p2.cards)

    assert not game.table_cards

    assert p2.get_card_count() == 8
    assert p1.get_card_count() == 6

# Test taking cards with top cards
