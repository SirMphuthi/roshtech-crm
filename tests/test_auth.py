"""Tests for authentication functionality."""

from app import db
from app.models import User

def test_login_page(client):
    """Test that the login page loads correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_success(client, auth):
    """Test successful login."""
    response = auth.login()
    assert response.headers['Location'] == '/dashboard'

def test_login_failure(client):
    """Test failed login."""
    response = client.post(
        '/login',
        data={'email': 'wrong@test.com', 'password': 'wrongpass'}
    )
    assert b'Invalid email or password' in response.data

def test_logout(client, auth):
    """Test logout."""
    auth.login()
    response = auth.logout()
    assert response.headers['Location'] == '/login'

def test_protected_routes_redirect(client):
    """Test that protected routes redirect to login when not authenticated."""
    routes = ['/', '/dashboard', '/users']
    for route in routes:
        response = client.get(route)
        assert response.headers['Location'].startswith('/login')

def test_admin_routes_require_admin(client, auth, app):
    """Test that admin routes are only accessible by admins."""
    # Create a non-admin user
    with app.app_context():
        user = User(
            email='user@test.com',
            first_name='Test',
            last_name='User',
            role='user'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
    
    # Try accessing admin routes as a normal user
    auth.login('user@test.com', 'password123')
    admin_routes = ['/users', '/users/create', '/tokens']
    for route in admin_routes:
        response = client.get(route)
        assert response.status_code == 403
    
    # Verify admin can access these routes
    auth.logout()
    auth.login('admin@test.com', 'password123')
    for route in admin_routes:
        response = client.get(route)
        assert response.status_code == 200