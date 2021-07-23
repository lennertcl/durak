from flask import url_for, current_app
from flask_mail import Message
from website import mail
from itsdangerous import URLSafeTimedSerializer


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='playdurak',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def send_confirm_email(user, token):
    msg = Message('Confirm Email',
                  sender='playdurak',
                  recipients=[user.email])
    msg.body = f'''Thanks for signing up. To activate your account, visit the following link:
{url_for('users.confirm_email', token=token, _external=True)}    

Cheers!
'''
    mail.send(msg)

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email