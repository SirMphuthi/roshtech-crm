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
