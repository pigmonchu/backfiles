from flask import Flask, logging, request, g
from flask_babel import Babel, _
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import app_config

db = SQLAlchemy()
mail = None
root_url = ''

def create_app(config_name):
    global mail, root_url
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    if app.config['DEBUG']:
        CORS(app)

    db.init_app(app)
    migrate = Migrate(app, db)
    babel = Babel(app)
    mail = Mail(app)
    root_url = '/{}/{}/'.format(app.config.get('API_ROOT_URL'), app.config.get('API_VERSION'))

    if app.config.get('LOG_LEVEL') == 'DEBUG':
        app.logger.setLevel(logging.logging.DEBUG)
    else:
        app.logger.setLevel(logging.logging.INFO)

    from app.auth import models

    '''
    Aquí los blueprints y route
    '''
    from .auth import auth  as auth_blueprint

    @app.before_request
    def before_request():
        g.locale = str(get_ocale())

    @babel.localeselector
    def get_ocale():
        user = getattr(g, 'user', None)
        if user is not None:
            return user.locale

        loc = request.accept_languages.best_match(app.config['LANGUAGES']) or app.config['DEFAULT_LANGUAGE']
        return loc

    # registrar los blueprints
    app.register_blueprint(auth_blueprint)

    @app.route('/')
    def hello_world():
        stri= _('Flask is OK')
        return stri

    return app
