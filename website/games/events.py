from flask import session
from flask_socketio import send, emit, join_room, leave_room
from website import socketio, gameManager

# Event when user joins a room
@socketio.on("join")
def join(data):
    room = session.get("room")
    join_room(room)
    emit('status', {"event": "joined", "username": session.get("username")}, room=room)

# Event when a user leaves a room
@socketio.on("leave")
def leave(data):
    room = session.get("room")
    leave_room(room)
    emit('status', {"event": "left", "username": session.get("username")}, room=room)

# Event when a user clicks start game button
@socketio.on("startgame")
def start_game(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    game.start_game()
    emit('status', {"event": "startgame", "username": session.get("username")}, room=room)

@socketio.on("throwcard")
def throw_card(cards):
    room = session.get("room")
    game = gameManager.current_games[room]
    player = game.get_player(session.get("username"))
    game.throw_cards(player, cards)
    emit('move', {"event": "throwcard", "username": session.get("username")}, room=room)

@socketio.on("takecards")
def take_cards():
    room = session.get("room")
    game = gameManager.current_games[room]
    player = game.get_player(session.get("username"))
    game.take_cards(player)
    emit('move', {"event": "takecards", "username": session.get("username")}, room=room)

@socketio.on("breakcards")
def take_cards():
    room = session.get("room")
    game = gameManager.current_games[room]
    game.break_cards()
    emit('move', {"event": "breakcards", "username": session.get("username")}, room=room)

@socketio.on("breakcard")
def break_card(bottomcard,topcard):
    room = session.get("room")
    game = gameManager.current_games[room]
    game.break_card(bottomcard,topcard)
    emit('move', {"event": "breakcard", "username": session.get("username")}, room=room)

@socketio.on("passcards")
def pass_cards(cards):
    room = session.get("room")
    game = gameManager.current_games[room]
    game.pass_on(cards)
    emit('move', {"event": "passcards", "username": session.get("username")}, room=room)
