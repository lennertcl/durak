from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from website.config import Config
from website.durak_game.game_manager import GameManager


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()
socketio = SocketIO()
gameManager = GameManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)

    from website.users.routes import users
    from website.games import games
    from website.main import main
    from website.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(games)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
