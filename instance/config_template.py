# -*- coding: utf-8 -*-
import os
sqlitedb = os.path.abspath("your-sqlite-relative-path-here")


SECRET_KEY = 'your-secret-key-here'
SECURITY_PASSWORD_SALT = 'your-security-password-salt-here'
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(sqlitedb)
MAIL_SERVER = 'your-smtp-server-here'
MAIL_PORT = 000
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = 'your-mail-user-name-here'
MAIL_PASSWORD = 'your-mail-pwd-here'
LOG_LEVEL = 'DEBUG|INFO|WARNING|ERROR'

DEFAULT_LANGUAGE = 'en'
LANGUAGES = ['en']
TOKEN_TIME_EXPIRATION = 300

WTF_CSRF_CHECK_DEFAULT = False

API_ROOT_URL = 'api'
API_VERSION = 'v1.0'
