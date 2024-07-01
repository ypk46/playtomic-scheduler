import logging
from flask import Flask
from flask_cors import CORS
from app.config import settings
from app.utils import init_logger
from app.blueprints import *

# Initialize logger
logger = logging.getLogger(settings.name)
init_logger(logger, name=settings.name, env=settings.env)


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    """
    # Configure the Flask app
    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    app.register_blueprint(health_bp, url_prefix="/api")

    return app
