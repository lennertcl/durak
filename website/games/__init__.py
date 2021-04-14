from flask import Blueprint

games = Blueprint('games', __name__)

from . import routes, events