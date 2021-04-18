import pytest

from website.durak import DurakGame, Player

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

# Test throwing cards
def test_throw(game):
    pass