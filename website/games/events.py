from flask import session, request
from flask_socketio import emit, join_room, leave_room
from website import socketio, gameManager
from website.durak_game.card import Card


@socketio.on("join")
def join(data):
    room = session.get("room")
    join_room(room)

    try:
        game = gameManager.current_games[room]
    except KeyError as e:
        print(f"Game not found: {e}")
        return

    player = game.get_player(session.get("username"))
    player.sid = request.sid
    event = {"event": "joined",
             "username": session.get("username")}
    emit('status', event, room=room)


@socketio.on("leave")
def leave(data):
    room = session.get("room")
    leave_room(room)

    game, player = get_game_and_player()
    is_next_round = game.remove_player(player)

    event = {"event": "left",
             "username": session.get("username")}
    emit('status', event, room=room)

    if is_next_round:
        emit_finish_round(game)


@socketio.on("chat")
def chat(data):
    game, player = get_game_and_player()
    event = {"event": "chat",
             "content": data["content"],
             "player": player.username}
    emit('status', event, room=game.id)


@socketio.on("startgame")
def start_game(data):
    game, _ = get_game_and_player()

    if game.is_in_progress:
        event = {"event": "message",
                 "body": "Game is already in progress",
                 "type": "danger"}
        emit('status', event, room=game.id)
        return

    if (game.get_lobby_count() + game.get_player_count()) <= 1:
        event = {"event": "message",
                 "body": "Not enough players to start the game",
                 "type": "danger"}
        emit('status', event, room=game.id) 
        return

    game.start_game()
    event = {"event": "startgame"}
    emit('status', event, room=game.id)


@socketio.on("throwcards")
def throw_cards(data):
    game, player = get_game_and_player()
    cards = [Card.from_str(card_str) for card_str in data["cards"]]
    is_thrown = game.throw_cards(player, cards)

    if is_thrown:
        event = {"event": "throwcards",
                "player": player.username,
                "cards": data["cards"]}
        emit('move', event, room=game.id)


@socketio.on("takecards")
def take_cards(data):
    game, player = get_game_and_player()
    is_taken = game.take_cards(player)

    if is_taken:
        event = {"event": "takecards"}
        emit('move', event, room=game.id)
        emit_finish_round(game)


@socketio.on("breakcards")
def break_cards(data):
    game, player = get_game_and_player()
    is_broken = game.break_cards(player)

    if is_broken:
        event = {"event": "breakcards"}
        emit('move', event, room=game.id)
        emit_finish_round(game)


@socketio.on("breakcard")
def break_card(data):
    game, player = get_game_and_player()
    bottomcard = Card.from_str(data["bottomcard"])
    topcard = Card.from_str(data["topcard"])
    is_broken = game.break_card(player, bottomcard, topcard)

    if is_broken:
        event = {"event": "breakcard",
                "bottomcard": data["bottomcard"],
                "topcard": data["topcard"],
                "player": player.username}
        emit('move', event, room=game.id)


@socketio.on("movetopcard")
def move_top_card(data):
    game, player = get_game_and_player()
    new_bottomcard = Card.from_str(data["new_bottomcard"])
    topcard = Card.from_str(data["topcard"])
    is_moved = game.move_top_card(player, topcard, new_bottomcard)

    if is_moved:
        event = {"event": "movetopcard",
                "new_bottomcard": data["new_bottomcard"],
                "topcard": data["topcard"]}
        emit('move', event, room=game.id)


@socketio.on("passcards")
def pass_cards(data):
    game, player = get_game_and_player()
    cards = [Card.from_str(card_str) for card_str in data["cards"]]
    is_passed = game.pass_on(player, cards)

    if is_passed:
        event = {"event": "passcards", 
                "player": session.get("username"),
                "newplayer": game.current_player.username,
                "cards": data["cards"]}
        emit('move', event, room=game.id)


@socketio.on("passtrump")
def pass_trump(data):
    game, player = get_game_and_player()
    is_passed = game.pass_on_using_trump(player)

    if is_passed:
        event = {"event": "passtrump", 
                "newplayer": game.current_player.username}
        emit('move', event, room=game.id)


@socketio.on("allowbreak")
def allow_break(data):
    game, player = get_game_and_player()
    allowed_break = game.allow_break_cards(player)

    if allowed_break:
        event = {"event": "allowbreak",
                 "player": player.username}
        emit('move', event, room=game.id)


@socketio.on("stealtrump")
def steal_trump(data):
    game, player = get_game_and_player()
    card = Card.from_str(data["card"])
    stole_card = game.steal_trump_card(player, card)

    if stole_card:
        event =  {"event": "stealtrump",
                  "player": player.username,
                  "card": data["card"]}
        emit('cheat', event, room=game.id)


@socketio.on("putintodeck")
def put_into_deck(data):
    game, player = get_game_and_player()
    cards = [Card.from_str(card_str) for card_str in data["cards"]]
    put_in_deck = game.put_into_deck(player, cards)

    if put_in_deck:
        event = {"event": "putintodeck",
                 "player": player.username,
                 "cards": data["cards"]}
        emit('cheat', event, room=game.id)


# Give every player the necessary information after a round is finished
def emit_finish_round(game):
    event = {
        "event": "finishround",
        "newplayer": game.current_player.username,
        "deckcount": game.deck.get_card_count(),
        "cardcounts": { player.username:player.get_card_count()
                        for player in game.players}
    }

    # Players that are playing get info about the new cards
    for player in game.players:
        cards = [str(card) for card in player.cards]
        event.update({"cards": cards})
        emit('status', event, room=player.sid)
    for player in game.lobby:
        emit('status', event, room=player.sid)


def get_game_and_player():
    room = session.get("room")
    game = gameManager.current_games[room]
    player = game.get_player(session.get("username"))
    return game, player
