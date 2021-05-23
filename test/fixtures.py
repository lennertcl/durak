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