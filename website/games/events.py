from flask import session
from flask_socketio import send, emit, join_room, leave_room
from website import socketio, gameManager
from website.durak_game.card import Card

# TODO prevent users from doing impossible stuff

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
    event = {"event": "startgame"}
    emit('status', event, room=room)

# Event when a user throws cards
@socketio.on("throwcards")
def throw_cards(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    player = game.get_player(session.get("username"))
    # Translate string cards to actual cards
    cards = [Card.from_str(card_str) for 
             card_str in data["cards"]]
    game.throw_cards(player, cards)
    event = {"event": "throwcards",
             "player": player.username,
             "cards": data["cards"]}
    emit('move', event, room=room)

# Event when a user takes cards
@socketio.on("takecards")
def take_cards(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    count = game.get_table_cards_count()
    game.take_cards()
    event = {"event": "takecards",
             "player": data["username"],
             "cardcount": count,
             "newplayer": game.current_player.username}
    emit('move', event, room=room)

# Event when a player breaks all cards
@socketio.on("breakcards")
def break_cards(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    game.break_cards()
    event = {"event": "breakcards",
             "newplayer": game.current_player.username}
    emit('move', event, room=room)

# Event when a player places a top card on
# another card to break
@socketio.on("breakcard")
def break_card(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    bottomcard = Card.from_str(data["bottomcard"])
    topcard = Card.from_str(data["topcard"])
    game.break_card(bottomcard,topcard)
    event = {"event": "breakcard",
             "bottomcard": data["bottomcard"],
             "topcard": data["topcard"]}
    emit('move', event, room=room)

# Event when a user passes cards to other players
@socketio.on("passcards")
def pass_cards(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    # Translate string cards to actual cards
    cards = [Card.from_str(card_str) for 
             card_str in data["cards"]]
    game.pass_on(cards)
    event = {"event": "passcards", 
             "username": session.get("username"),
             "newplayer": game.current_player.username,
             "cards": data["cards"]}
    emit('move', event, room=room)

# Event when a user passed cards using trump
@socketio.on("passtrump")
def pass_trump(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    game.pass_on_using_trump()
    event = {"event": "passtrump", 
             "newplayer": game.current_player.username}
    emit('move', event, room=room)