from flask import render_template, current_app as app
from flask import url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask_babel import _
from app import mail


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email=serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False

    return email

def sendConfirmationMail(email):
    token = generate_confirmation_token(email)
    confirm_url = url_for('auth.confirm_email_api', token=token, _external=True)
    html = render_template('mails/activate.html', confirm_url=confirm_url)
    subject = _("Confirm your mail, please.")
    msg = Message(subject=subject, sender=app.config['DEFAULT_MAIL_SENDER'], recipients=[email], html=html)
    mail.send(msg)
    app.logger.info('**** Enviada confirmacion a {} ****'.format(email))
