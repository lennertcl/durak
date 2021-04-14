from flask import session
from flask_socketio import send, emit, join_room, leave_room
from website import socketio

@socketio.on("message")
def message(data):

    print(data)
    send(data)
    emit('some-event', 'custom message')

@socketio.on("join")
def join(data):
    join_room(data["room"])
    send({"msg": data["username"] + " has joined"},
        room=data["room"])

@socketio.on("leave")
def leave(data):
    leave_room(data["room"])
    send({"msg": data["username"] + " has left"},
        room=data["room"])