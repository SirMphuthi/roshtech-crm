import secrets
from app.models import Token, User, Account, Opportunity

def test_api_accounts_public(client, app):
    # Create an account in test DB
    with app.app_context():
        a = Account(name='TestCo', industry='Tech', phone='123', website='https://test.co')
        app.db = None
        db = __import__('app').app.db if False else None
    # We will use the client to call the public endpoint
    resp = client.get('/api/accounts')
    assert resp.status_code == 200


def test_token_auth_for_opportunities(client, app):
    # Ensure an opportunity exists and token works
    with app.app_context():
        admin = User.query.filter_by(email='admin@test.com').first()
        if not admin:
            admin = User(email='admin@test.com', first_name='Test', last_name='Admin', role='admin')
            admin.set_password('password123')
            from app import db
            db.session.add(admin)
            db.session.commit()
        # create an account and opportunity
        acc = Account(name='API Co')
        from app import db
        db.session.add(acc)
        db.session.commit()
        opp = Opportunity(name='API Deal', account_id=acc.id, owner_id=admin.id)
        db.session.add(opp)
        db.session.commit()
        # create token
        token_value = secrets.token_urlsafe(24)
        t = Token(token=token_value, user_id=admin.id)
        db.session.add(t)
        db.session.commit()

    # call API with token in query param
    resp = client.get(f'/api/opportunities?token={token_value}')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'items' in data

    # call API with Authorization header
    resp2 = client.get('/api/opportunities', headers={'Authorization': f'Bearer {token_value}'})
    assert resp2.status_code == 200
