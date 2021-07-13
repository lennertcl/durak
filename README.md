# Durak

## Quickstart

### Install requirements

Create virtual environment and activate it.

Linux/mac:
```
python -m venv durakenv
source durakenv/bin/activate
pip install -r requirements.txt
```

Windows:
```
python -m venv durakenv
call durakenv/Scripts/activate.bat
pip install -r requirements.txt
```

### Initialize the database

```python
from run import app
from website import db
from website.models import User

with app.app_context():
    db.create_all()
```

### Set the necessary config variables

Copy the `website/.env.example` file to `website/.env`.
Enter the correct information for your system:

```
SECRET_KEY=<your secret key>
SQLALCHEMY_DATABASE_URI=<location of the database>
EMAIL_USER=<app gmail account>
EMAIL_PASS=<app gmail password>
```

### Run the application

```
python run.py
```

Visit the application at 0.0.0.0:5000 in your browser.
