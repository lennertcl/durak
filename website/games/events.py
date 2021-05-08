from flask import session, request, abort
from flask_socketio import send, emit, join_room, leave_room
from website import socketio, gameManager
from website.durak_game.card import Card

# Event when user joins a room
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

# Event when a user leaves a room
@socketio.on("leave")
def leave(data):
    room = session.get("room")
    leave_room(room)
    event = {"event": "left",
             "username": session.get("username")}
    emit('status', event, room=room)

# Event when a user clicks start game button
@socketio.on("startgame")
def start_game(data):
    game, _ = get_game_and_player()
    game.start_game()
    event = {"event": "startgame"}
    emit('status', event, room=game.id)

# Event when a user throws cards
@socketio.on("throwcards")
def throw_cards(data):
    game, player = get_game_and_player()
    # Translate string cards to actual cards
    cards = [Card.from_str(card_str) for 
             card_str in data["cards"]]
    is_thrown = game.throw_cards(player, cards)
    if is_thrown:
        event = {"event": "throwcards",
                "player": player.username,
                "cards": data["cards"]}
        emit('move', event, room=game.id)

# Event when a user takes cards
@socketio.on("takecards")
def take_cards(data):
    game, player = get_game_and_player()
    game.take_cards(player)
    event = {"event": "takecards"}
    emit('move', event, room=game.id)
    emit_finish_round(game)

# Event when a player breaks all cards
@socketio.on("breakcards")
def break_cards(data):
    game, player = get_game_and_player()
    is_broken = game.break_cards(player)
    if is_broken:
        event = {"event": "breakcards"}
        emit('move', event, room=game.id)
        emit_finish_round(game)

# Event when a player places a top card on
# another card to break
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

# Event when the current player moves the top
# card to another card
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

# Event when a user passes cards to other players
@socketio.on("passcards")
def pass_cards(data):
    game, player = get_game_and_player()
    # Translate string cards to actual cards
    cards = [Card.from_str(card_str) for 
             card_str in data["cards"]]
    is_passed = game.pass_on(player, cards)
    if is_passed:
        event = {"event": "passcards", 
                "player": session.get("username"),
                "newplayer": game.current_player.username,
                "cards": data["cards"]}
        emit('move', event, room=game.id)

# Event when a user passed cards using trump
@socketio.on("passtrump")
def pass_trump(data):
    game, player = get_game_and_player()
    is_passed = game.pass_on_using_trump(player)
    if is_passed:
        event = {"event": "passtrump", 
                "newplayer": game.current_player.username}
        emit('move', event, room=game.id)

# Event when a player allows the current player
# to break the cards
@socketio.on("allowbreak")
def allow_break(data):
    game, player = get_game_and_player()
    game.allow_break_cards(player)

# Give every player the necessary information
# after a round is finished
def emit_finish_round(game):
    event = {"event": "finishround",
             "newplayer": game.current_player.username,
             "deckcount": game.deck.get_card_count(),
             "cardcounts": {
                player.username:player.get_card_count()
                for player in game.players}
            }
    for player in game.players:
        cards = [str(card) for card in player.cards]
        event.update({"cards": cards})
        emit('status', event, room=player.sid)

def get_game_and_player():
    room = session.get("room")
    game = gameManager.current_games[room]
    player = game.get_player(session.get("username"))
    return game, player
