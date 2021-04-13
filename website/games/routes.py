from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from website import db
# TODO
# from website.models import Game
from website.games.forms import GameForm

games = Blueprint('games', __name__)


@games.route("/game/new", methods=['GET', 'POST'])
@login_required
def new_game():
    form = GameForm()
    if form.validate_on_submit():
        # TODO create game here
        # game = Game()
        # add game to current games
        return redirect(url_for('main.home')) # redirect to the game
    return render_template('create_game.html', title='New Game',
                           form=form, legend='New Game')


@games.route("/game/<int:game_id>")
def game(game_id):
    # TODO redirect to game or 404
    # game = game.query.get_or_404(post_id)
    return render_template('game.html', title=game.title, game=game)