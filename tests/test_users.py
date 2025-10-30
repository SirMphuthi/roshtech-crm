from app.models import User

def test_user_list(client, auth):
    """Test that admin can view user list."""
    auth.login()
    response = client.get('/users')
    assert response.status_code == 200
    assert b'User Management' in response.data

def test_create_user(client, auth, app):
    """Test user creation."""
    auth.login()
    response = client.post('/users/create', data={
        'email': 'newuser@test.com',
        'password': 'testpass123',
        'first_name': 'New',
        'last_name': 'User',
        'role': 'user'
    })
    assert response.headers['Location'] == '/users'
    
    with app.app_context():
        user = User.query.filter_by(email='newuser@test.com').first()
        assert user is not None
        assert user.first_name == 'New'
        assert user.role == 'user'

def test_edit_user(client, auth, app):
    """Test user editing."""
    # First create a user to edit
    auth.login()
    client.post('/users/create', data={
        'email': 'edit@test.com',
        'password': 'testpass123',
        'first_name': 'Edit',
        'last_name': 'User',
        'role': 'user'
    })
    
    with app.app_context():
        user = User.query.filter_by(email='edit@test.com').first()
        response = client.post(f'/users/{user.id}/edit', data={
            'email': 'edited@test.com',
            'first_name': 'Edited',
            'last_name': 'User',
            'role': 'user'
        })
        assert response.headers['Location'] == '/users'
        
        edited_user = User.query.get(user.id)
        assert edited_user.email == 'edited@test.com'
        assert edited_user.first_name == 'Edited'

def test_delete_user(client, auth, app):
    """Test user deletion."""
    # First create a user to delete
    auth.login()
    client.post('/users/create', data={
        'email': 'delete@test.com',
        'password': 'testpass123',
        'first_name': 'Delete',
        'last_name': 'User',
        'role': 'user'
    })
    
    with app.app_context():
        user = User.query.filter_by(email='delete@test.com').first()
        response = client.post(f'/users/{user.id}/delete')
        assert response.headers['Location'] == '/users'
        
        deleted_user = User.query.get(user.id)
        assert deleted_user is None

def test_non_admin_cannot_access_user_management(client, auth, app):
    """Test that non-admin users cannot access user management."""
    # Create a regular user
    auth.login()
    client.post('/users/create', data={
        'email': 'regular@test.com',
        'password': 'testpass123',
        'first_name': 'Regular',
        'last_name': 'User',
        'role': 'user'
    })
    
    # Login as the regular user
    auth.login('regular@test.com', 'testpass123')
    
    # Try to access user management
    response = client.get('/users')
    assert response.status_code == 403  # Forbidden