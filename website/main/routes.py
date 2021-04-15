from flask import render_template, flash, redirect, url_for
from website import gameManager
from website.main.forms import JoinForm
from . import main

@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():
    form = JoinForm()
    if form.validate_on_submit():
        try:
            game = gameManager.current_games[int(form.game_id.data)]
            return redirect(url_for('games.join', game_id=game.id))
        except KeyError:
            flash("No game found with this code", "danger")

    return render_template("home.html", form=form)

@main.route("/rules")
def rules():
    return render_template("rules.html")
