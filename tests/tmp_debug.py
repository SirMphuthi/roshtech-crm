def test_debug_whoami_flow(client, auth):
    # Create a regular user as admin
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

    # Check whoami
    resp = client.get('/_debug/whoami')
    print(resp.get_data(as_text=True))
    assert resp.status_code == 200
