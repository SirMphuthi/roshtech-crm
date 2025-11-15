from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from .config import Config

# Optional CSRF support (Flask-WTF). We import lazily so tests/dev without the
# dependency continue to run. If Flask-WTF is installed, CSRFProtect will be
# initialized and a `csrf_token` template global (generate_csrf) will be exposed.
csrf = None

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # Enable CORS for all routes, allow credentials
    CORS(app, supports_credentials=True)
    # Load the default configuration
    app.config.from_object(Config)
    # Override with test config if provided
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Security headers middleware
    @app.after_request
    def add_security_headers(response):
        # HSTS
        if app.config.get('STRICT_TRANSPORT_SECURITY'):
            response.headers['Strict-Transport-Security'] = app.config['STRICT_TRANSPORT_SECURITY']
        # Content Security Policy
        if app.config.get('CONTENT_SECURITY_POLICY'):
            response.headers['Content-Security-Policy'] = app.config['CONTENT_SECURITY_POLICY']
        # Other security headers
        response.headers['X-Content-Type-Options'] = app.config['X_CONTENT_TYPE_OPTIONS']
        response.headers['X-Frame-Options'] = app.config['X_FRAME_OPTIONS']
        response.headers['X-XSS-Protection'] = app.config['X_XSS_PROTECTION']
        return response

    # Try to enable CSRFProtect if Flask-WTF is available.
    try:
        from flask_wtf import CSRFProtect
        from flask_wtf.csrf import generate_csrf

        csrf = CSRFProtect()
        csrf.init_app(app)
        # expose generate_csrf as csrf_token() in templates
        app.jinja_env.globals['csrf_token'] = generate_csrf
    except Exception:
        csrf = None

    # Exempt API blueprint from CSRF protection
    try:
        csrf.exempt(api_blueprint)
    except Exception:
        pass

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register API blueprint
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    # Exempt API blueprint from CSRF protection
    if csrf:
        csrf.exempt(api_blueprint)

    from . import models

    # Add CLI command to create/reset admin user
    @app.cli.command('reset-admin')
    def reset_admin():
        """Create or reset the admin user with a default password."""
        from app.models import User, db
        email = 'admin@test.com'
        password = 'password123'
        with app.app_context():
            user = User.query.filter_by(email=email).first()
            if not user:
                # Create the owner account so repository owner has full access
                user = User(email=email, first_name='Test', last_name='Admin', role='owner')
                user.set_password(password)
                db.session.add(user)
            else:
                user.set_password(password)
            db.session.commit()
            print(f"Admin user reset: {email} / {password} (role=owner)")

    return app
