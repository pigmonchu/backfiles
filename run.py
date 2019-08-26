import os
from flask import logging

from app import create_app

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
else:
    gunicorn_logger = logging.logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
