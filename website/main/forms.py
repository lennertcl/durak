from flask_wtf import FlaskForm
from wtforms import IntegerField,  SubmitField
from wtforms.validators import DataRequired

# Form to join a game by using game id
class JoinForm(FlaskForm):
    game_id = IntegerField("Game id", validators=[DataRequired()])
    submit = SubmitField("Join game")