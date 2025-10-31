import os
from dotenv import load_dotenv

# Find the base directory of the project so it can locate the .env file
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Set Flask configuration variables from .env file."""

    # General Config
    # Used for session security (e.g., Flask-Login)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_long_and_very_secret_key_fallback'
    
    # Database Config
    # Sets the database URI from the .env file, or defaults to a simple SQLite file
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security headers
    STRICT_TRANSPORT_SECURITY = os.environ.get('STRICT_TRANSPORT_SECURITY', 'max-age=31536000; includeSubDomains')
    CONTENT_SECURITY_POLICY = os.environ.get('CONTENT_SECURITY_POLICY', "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';")
    X_CONTENT_TYPE_OPTIONS = 'nosniff'
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    X_XSS_PROTECTION = '1; mode=block'
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100/hour')
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    
    # Mail settings (optional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 0)) if os.environ.get('MAIL_PORT') else None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False').lower() in ('1', 'true', 'yes')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'no-reply@localhost'
    
    # Session security
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('1', 'true', 'yes')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600))
