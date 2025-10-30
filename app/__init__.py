from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Load the default configuration
    app.config.from_object(Config)
    
    # Override with test config if provided
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register API blueprint
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from . import models

    return app
