from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
import jwt
import datetime
from flask_babel import _

from flask import current_app as app
from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True, nullable=False)
    first_name = db.Column(db.String(60), index=True, nullable=False)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=True)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=True)
    is_administrator = db.Column(db.Boolean, nullable=True)

    #Audit Fields
    timestamp_insert = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    timestamp_update = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())
    user_update = db.Column(db.Integer)


    @property
    def password(self):
        raise AttributeError(_('Can not read the password.'))

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @validates('first_name')
    def validate_first_name(self, key, value):
        if not value:
            raise AssertionError(_('Mandatory First Name'))
        return value
    
    def encode_auth_token(self):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=app.config.get('TOKEN_TIME_EXPIRATION') or 3600),
                'iat': datetime.datetime.utcnow(),
                'sub': str(self.id)
            }

            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        '''
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        '''
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                raise ValueError(_('Not authenticated. Please log in again.'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise  AttributeError(_('Signature expired. Please log in again.'))
        except jwt.InvalidTokenError:
            raise ValueError(_('Not authenticated. Please log in again.'))

    def __repr__(self):
        return '<User ({}): {} {}'.format(self.email, self.first_name, self.last_name)

class BlacklistToken(db.Model):
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    #Audit Fields
    timestamp_insert = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    timestamp_update = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())
    user_update = db.Column(db.Integer, nullable=False)


    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id>: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()

        if res:
            return True
        else:
            return False
