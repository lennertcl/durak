from run import app
from website import db
from website.models import User
with app.app_context():
    db.create_all()