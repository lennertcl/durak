from flask import (render_template, url_for, redirect, 
                   abort, session, flash)
from flask_login import current_user, login_required
from website import db, gameManager, socketio
from website.games.forms import GameForm
from website.durak_game.player import Player
from . import games

@games.route("/game/new", methods=['GET', 'POST'])
@login_required
def new_game():
    form = GameForm()
    if form.validate_on_submit():
        game = gameManager.create_game(form.name.data)
        return redirect(url_for('games.join', game_id=game.id))

    return render_template('game/create_game.html', title='New Game',
                           form=form, legend='New Game')

@games.route("/game/join/<int:game_id>")
@login_required
def join(game_id):
    try:
        game = gameManager.current_games[game_id]
        if game.is_full():
            flash("The game is full.", "danger")
            return redirect(url_for('main.home'))
        session["room"] = game_id
        session["username"] = current_user.username
        game.add_player(current_user.username)
    except KeyError:
        abort(404)
    if game.is_in_progress:
        # If the game is already in progress, spectating is possible
        return redirect(url_for('games.game', game_id=game.id))
    return redirect(url_for('games.lobby', game_id=game.id))

@games.route("/game/lobby/<int:game_id>", methods=['GET', 'POST'])
@login_required
def lobby(game_id):
    username = session.get("username", None)
    room = session.get("room", None)
    if not username or not room:
        return redirect(url_for("games.join", game_id=game_id))
    try:
        game = gameManager.current_games[game_id]
    except KeyError:
        abort(404)
    return render_template("game/game_lobby.html", game=game, 
                username=current_user.username)

@games.route("/game/<int:game_id>")
@login_required
def game(game_id):
    try:
        game = gameManager.current_games[game_id]
        player = game.get_player(current_user.username)
        spectating = player not in game.players
        other_players = player.get_players_in_position(game, spectating=spectating)
        allowed_break_players = []
        if game.next_allows_break:
            allowed_break_players.append(game.next_player(game.current_player))
        if game.prev_allows_break:
            allowed_break_players.append(game.prev_player(game.current_player))
    except KeyError:
        abort(404)
    return render_template('game/game.html', game=game,
                player=player,
                current_player=game.current_player.username,
                other_players=other_players,
                spectating=spectating,
                allowed_break_players=allowed_break_players)
