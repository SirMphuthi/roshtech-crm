import io
import csv

def test_accounts_list(client, auth):
    # Login as admin and fetch accounts list (initially empty)
    auth.login()
    res = client.get('/accounts')
    assert res.status_code == 200
    assert b'Accounts' in res.data


def test_create_account(client, auth):
    auth.login()
    res = client.post('/accounts/create', data={
        'name': 'Test Corp',
        'industry': 'Software',
        'phone': '0123456789',
        'website': 'https://test.example'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Account created successfully' in res.data
    # Now listing should show the account
    res2 = client.get('/accounts')
    assert b'Test Corp' in res2.data


def test_import_accounts_csv(client, auth):
    auth.login()
    csv_content = 'name,industry,phone,website,owner_email\n'
    csv_content += 'ImportCo,Manufacturing,0987654321,https://import.example,admin@test.com\n'

    data = {
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'accounts.csv')
    }
    res = client.post('/accounts/import', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert res.status_code == 200
    assert b'Imported' in res.data
    # Ensure imported company appears in list
    res2 = client.get('/accounts')
    assert b'ImportCo' in res2.data
