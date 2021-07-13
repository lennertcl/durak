from website.durak_game.card import Card
from website.durak_game.player import Player
from website.durak_game.durak import DurakGame

from .fixtures import game


# BREAKING 1 CARD


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


def test_break_card(game):
    """ Regular breaking of a card """
    game.start_game()

    p1 = game.prev_player(game.current_player)
    p2 = game.current_player

    bottom_card = Card(Card.HEARTS, Card.SEVEN)
    top_card = Card(Card.HEARTS, Card.SEVEN)
    # Make sure the player can break the card
    p1.add_cards([bottom_card])
    p2.add_cards([top_card])

    game.throw_cards(p1, [bottom_card])
    game.break_card(p2, bottom_card, top_card)

    assert game.table_cards[bottom_card] == top_card
    assert p2.get_card_count() == 6
    assert top_card not in p2.cards


# BREAKING CARDS


# POSSIBLE


def test_possible_break_cards_possible(game):
    """ Possible break """
    game.start_game()
    p1 = game.current_player
    p2 = game.next_player(p1)
    p3 = game.prev_player(p1)

    game.allow_break_cards(p2)
    game.allow_break_cards(p3)

    assert game.is_possible_break_cards(p1)

def test_possible_break_cards_impossible_not_allowed(game):
    """ A player has not allowed yet """
    game.start_game()
    assert not game.is_possible_break_cards(game.current_player)

def test_possible_break_cards_impossible_player(game):
    """ The player is not the current player """
    game.start_game()
    p = game.next_player(game.current_player)
    assert not game.is_possible_break_cards(p)


# LEGAL


def test_legal_break_cards_legal_regular(game):
    """ Legal break cards without trump"""
    game.start_game()

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): Card(Card.HEARTS, Card.EIGHT)}

    assert game.is_legal_break_cards()

def test_legal_break_cards_legal_trump(game):
    """ Legal break cards with trump"""
    game.start_game()
    game.trump = Card.HEARTS

    game.table_cards = {Card(Card.CLUBS, Card.SEVEN): Card(Card.HEARTS, Card.EIGHT)}

    assert game.is_legal_break_cards()

def test_legal_break_cards_illegal_no_top(game):
    """ A bottom card does not have a top card """
    game.start_game()

    game.table_cards = {Card(Card.CLUBS, Card.SEVEN): None}

    assert not game.is_legal_break_cards()

def test_legal_break_cards_illegal_not_higher(game):
    """ A card is broken by a card that is not higher """
    game.start_game()

    game.table_cards = {Card(Card.HEARTS, Card.EIGHT): Card(Card.HEARTS, Card.SEVEN)}

    assert not game.is_legal_break_cards()

def test_legal_break_cards_illegal_other_suit(game):
    """ A card is broken by a card of another suit (not trump) """
    game.start_game()
    game.trump = Card.CLUBS

    game.table_cards = {Card(Card.HEARTS, Card.SEVEN): Card(Card.DIAMONDS, Card.EIGHT)}

    assert not game.is_legal_break_cards()

def test_legal_break_cards_illegal_lower_trump(game):
    """ A trump card is broken by a lower trump card """
    game.start_game()
    game.trump = Card.HEARTS

    game.table_cards = {Card(Card.HEARTS, Card.EIGHT): Card(Card.HEARTS, Card.SEVEN)}

    assert not game.is_legal_break_cards()


# PERFORMING BREAK CARDS


def test_break_cards(game):
    """ Regular breaking of cards 

    We only test whether the round has been finished correctly by checking that
    the current player has been set to the next player. Full functionality of
    finishing a round is not tested here. 
    """
    game.start_game()
    p1 = game.current_player
    p2 = game.next_player(p1)
    p3 = game.prev_player(p1)

    p2.add_cards([Card(Card.HEARTS, Card.SEVEN)])
    p1.add_cards([Card(Card.HEARTS, Card.EIGHT)])

    game.throw_cards(p2, [Card(Card.HEARTS, Card.SEVEN)])
    game.break_card(p1, Card(Card.HEARTS, Card.SEVEN), Card(Card.HEARTS, Card.EIGHT))

    game.allow_break_cards(p2)
    game.allow_break_cards(p3)

    is_broken = game.break_cards(p1)
    assert is_broken
    assert game.current_player == p2


# ALLOWING BREAK CARDS


def test_allow_break_cards_regular(game):
    """ Regular scenario of allowing to break cards """
    game.start_game()
    p1 = game.prev_player(game.current_player)
    p2 = game.next_player(game.current_player)

    game.allow_break_cards(p1)
    game.allow_break_cards(p2)

    assert game.next_allows_break
    assert game.prev_allows_break

def test_allow_break_cards_other_player(game):
    """ An irrelevant player allows break cards """
    game.start_game()
    p = game.current_player

    game.allow_break_cards(p)

    assert not game.next_allows_break
    assert not game.prev_allows_break

def test_allow_break_cards_same_player(game):
    """ The next player and the previous player are the same """
    game.remove_player(game.lobby[0])
    game.remove_player(game.lobby[0])
    game.start_game()
    p = game.next_player(game.current_player)

    game.allow_break_cards(p)

    assert game.next_allows_break
    assert game.prev_allows_break


# MOVE TOP CARD


# POSSIBLE


def test_possible_move_top_card_possible(game):
    """ Moving the top card is possible """
    game.start_game()
    p = game.current_player
    game.table_cards = {
        Card(Card.CLUBS, Card.SEVEN): Card(Card.HEARTS, Card.NINE),
        Card(Card.HEARTS, Card.EIGHT): None
    }

    assert game.is_possible_move_top_card(p,
        top_card=Card(Card.HEARTS, Card.NINE),
        new_bottom_card=Card(Card.HEARTS, Card.EIGHT))


def test_possible_move_top_card_impossible_player(game):
    """ The player is not the current player """
    game.start_game()
    p = game.next_player(game.current_player)
    game.table_cards = {
        Card(Card.CLUBS, Card.SEVEN): Card(Card.HEARTS, Card.NINE),
        Card(Card.HEARTS, Card.EIGHT): None
    }

    assert not game.is_possible_move_top_card(p,
        top_card=Card(Card.HEARTS, Card.NINE),
        new_bottom_card=Card(Card.HEARTS, Card.EIGHT))

def test_possible_move_top_card_impossible_top_card(game):
    """ The top card is not on the table as a top card """
    game.start_game()
    p = game.current_player
    game.table_cards = {
        Card(Card.CLUBS, Card.SEVEN): Card(Card.HEARTS, Card.NINE),
        Card(Card.HEARTS, Card.EIGHT): None
    }

    assert not game.is_possible_move_top_card(p,
        top_card=Card(Card.HEARTS, Card.TEN),
        new_bottom_card=Card(Card.HEARTS, Card.EIGHT))

def test_possible_move_top_card_impossible_bottom_card(game):
    """ The bottom card is not on the table as a bottom card """
    game.start_game()
    p = game.current_player
    game.table_cards = {
        Card(Card.CLUBS, Card.SEVEN): Card(Card.HEARTS, Card.NINE)
    }

    assert not game.is_possible_move_top_card(p,
        top_card=Card(Card.HEARTS, Card.NINE),
        new_bottom_card=Card(Card.HEARTS, Card.EIGHT))

def test_possible_move_top_card_impossible_already_on_top(game):
    """ The bottom card already has another card on top """
    game.start_game()
    p = game.current_player
    game.table_cards = {
        Card(Card.CLUBS, Card.SEVEN): Card(Card.HEARTS, Card.NINE),
        Card(Card.HEARTS, Card.EIGHT): Card(Card.HEARTS, Card.TEN)
    }

    assert not game.is_possible_move_top_card(p,
        top_card=Card(Card.HEARTS, Card.TEN),
        new_bottom_card=Card(Card.HEARTS, Card.EIGHT))


# PERFORMING MOVE TOP CARD
# TODO