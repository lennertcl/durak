from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

# Form to create a new game
class GameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    lowest_card = SelectField("Lowest card", default=(6, 6),
        choices=[(2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)],
        validators=[DataRequired()])
    submit = SubmitField('Create game')
