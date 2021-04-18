# Durak

## Quickstart

### Install requirements

Create virtual environment and activate it

```bash
python -m venv durakenv
source durakenv/bin/activate
pip install -r requirements.txt
```

### Initialize the database

```python
from website import db
db.create_all()
```

### Set the necessary config variables

Directly in config.py:

```python
SECRET_KEY="your secret key"
SQLALCHEMY_DATABASE_URI="path/to/database.db"
EMAIL_USER="app gmail account"
EMAIL_PASS="app gmail password"
```

Or using environment variables:

```bash
EXPORT SECRET_KEY="your secret key"
EXPORT SQLALCHEMY_DATABASE_URI="path/to/database.db"
EXPORT EMAIL_USER="app gmail account"
EXPORT EMAIL_PASS="app gmail password"
```

### Run the application

```bash
python run.py
```

Visit the application at 127.0.0.1:5000 in your browser
