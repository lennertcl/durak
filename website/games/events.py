from flask import session
from flask_socketio import send, emit, join_room, leave_room
from website import socketio, gameManager

# Event when user joins a room
@socketio.on("join")
def join(data):
    room = session.get("room")
    join_room(room)
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
    room = session.get("room")
    game = gameManager.current_games[room]
    game.start_game()
    event = {"event": "startgame",
             "username": session.get("username")}
    emit('status', event, room=room)

# Event when a user throws cards
@socketio.on("throwcards")
def throw_cards(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    player = game.get_player(session.get("username"))
    # TODO translate data["cards"] to card objects
    # before throwing them from the game
    cards = None
    game.throw_cards(player, cards)
    event = {"event": "throwcards",
             "player": player.username,
             "cards": data["cards"]}
    emit('move', event, room=room)

# Event when a user takes cards
@socketio.on("takecards")
def take_cards():
    room = session.get("room")
    game = gameManager.current_games[room]
    # TODO player probably doesnt matter because
    # it is always the current player who takes
    player = game.get_player(session.get("username"))
    game.take_cards(player)
    event = {"event": "takecards"}
    emit('move', event, room=room)

# Event when a player breaks all cards
@socketio.on("breakcards")
def take_cards():
    room = session.get("room")
    game = gameManager.current_games[room]
    game.break_cards()
    event = {"event": "breakcards"}
    emit('move', event, room=room)

# Event when a player places a top card on
# another card to break
@socketio.on("breakcard")
def break_card(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    bottomcard = data["bottomcard"]
    topcard = data["topcard"]
    # TODO translate to card object
    game.break_card(bottomcard,topcard)
    event = {"event": "breakcard",
             "bottomcard": bottomcard,
             "topcard": topcard}
    emit('move', event, room=room)

# Event when a user passes cards to other players
@socketio.on("passcards")
def pass_cards(cards):
    room = session.get("room")
    game = gameManager.current_games[room]
    game.pass_on(cards)
    event = {"event": "passcards", 
             "username": session.get("username")}
    emit('move', event, room=room)
