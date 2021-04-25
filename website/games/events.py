from flask import session, request
from flask_socketio import send, emit, join_room, leave_room
from website import socketio, gameManager
from website.durak_game.card import Card

# TODO prevent users from doing impossible stuff

# Event when user joins a room
@socketio.on("join")
def join(data):
    room = session.get("room")
    join_room(room)
    game = gameManager.current_games[room]
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
    is_thrown = game.throw_cards(player, cards)
    if is_thrown:
        event = {"event": "throwcards",
                "player": player.username,
                "cards": data["cards"]}
        emit('move', event, room=room)

# Event when a user takes cards
@socketio.on("takecards")
def take_cards(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    game.take_cards()
    event = {"event": "takecards"}
    emit('move', event, room=room)
    emit_finish_round(game)

# Event when a player breaks all cards
@socketio.on("breakcards")
def break_cards(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    game.break_cards()
    event = {"event": "breakcards"}
    emit('move', event, room=room)
    emit_finish_round(game)

# Event when a player places a top card on
# another card to break
@socketio.on("breakcard")
def break_card(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    bottomcard = Card.from_str(data["bottomcard"])
    topcard = Card.from_str(data["topcard"])
    is_broken = game.break_card(bottomcard,topcard)
    if is_broken:
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
    is_passed = game.pass_on(cards)
    if is_passed:
        event = {"event": "passcards", 
                "player": session.get("username"),
                "newplayer": game.current_player.username,
                "cards": data["cards"]}
        emit('move', event, room=room)

# Event when a user passed cards using trump
@socketio.on("passtrump")
def pass_trump(data):
    room = session.get("room")
    game = gameManager.current_games[room]
    is_passed = game.pass_on_using_trump()
    if is_passed:
        event = {"event": "passtrump", 
                "newplayer": game.current_player.username}
        emit('move', event, room=room)

# Give every player the necessary information
# after a round is finished
def emit_finish_round(game):
    event = {"event": "finishround",
             "newplayer": game.current_player.username,
             "deckcount": game.deck.get_card_count()}
    for player in game.players:
        cards = [str(card) for card in player.cards]
        event.update({"cards": cards})
        emit('status', event, room=player.sid)