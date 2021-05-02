from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

# Form to create a new game
class GameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=10)])
    submit = SubmitField('Create game')
