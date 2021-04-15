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
