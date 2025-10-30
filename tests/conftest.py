import os
import tempfile
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    test_app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key'
    })
    
    # Create the database and load test data
    with test_app.app_context():
        db.create_all()
        admin = User(
            email='admin@test.com',
            first_name='Test',
            last_name='Admin',
            role='admin'
        )
        admin.set_password('password123')
        db.session.add(admin)
        db.session.commit()

    yield test_app

    # Cleanup
    with test_app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except:
        pass

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """Authentication helper for tests."""
    class AuthActions:
        def login(self, email='admin@test.com', password='password123'):
            # Ensure any existing session is cleared before logging in so tests
            # can switch users without requiring an explicit logout in each test.
            try:
                client.get('/logout')
            except Exception:
                pass
            # We don't follow redirects here so tests can verify the redirect location
            response = client.post(
                '/login',
                data={'email': email, 'password': password},
                follow_redirects=False
            )
            return response

        def logout(self):
            return client.get('/logout')

    return AuthActions()