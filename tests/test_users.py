from base64 import b64encode
from tests import TestBase


def gen_authtication(username, password):
    return 'Basic ' + str(b64encode((username + ':' + password).encode('utf-8')), 'utf-8')


class TestUser(TestBase):
    TEST_ACCOUNT = {
        'email': 'test@example.com',
        'password': 'testpassword',
        'full_name': 'Test Account'
    }

    def test_signup(self):
        rv = self.client.post('/users', data=self.TEST_ACCOUNT)
        assert rv.status_code == 200
        assert 'id' in rv.json
        assert rv.json['email'] == self.TEST_ACCOUNT['email']
        assert rv.json['full_name'] == self.TEST_ACCOUNT['full_name']
        assert not rv.json['is_admin']

    def test_signup_incomplete(self):
        rv = self.client.post('/users', data={
            'email': 'test2@example.com',
            'password': 'test2password'
        })
        assert rv.status_code == 400
        assert 'Missing' in rv.json['message']['full_name']

    def test_signup_duplicate(self):
        rv = self.client.post('/users', data=self.TEST_ACCOUNT)
        assert rv.status_code == 400
        assert 'already exists' in rv.json['message']

    def test_login_noauth(self):
        rv = self.client.get('/users/current')
        assert rv.status_code == 401

    def test_login_password(self):
        rv = self.client.get('/users/current', headers={
            'Authorization': gen_authtication(
                self.TEST_ACCOUNT['email'],
                self.TEST_ACCOUNT['password']
            )
        })
        assert rv.status_code == 200
        assert 'id' in rv.json
        assert rv.json['email'] == self.TEST_ACCOUNT['email']
        assert rv.json['full_name'] == self.TEST_ACCOUNT['full_name']
        assert not rv.json['is_admin']
        assert 'token' in rv.json
        self.TEST_ACCOUNT['token'] = rv.json['token']

    def test_login_token(self):
        rv = self.client.get('/users/current', headers={
            'Authorization': 'Bearer ' + self.TEST_ACCOUNT['token']
        })
        assert rv.status_code == 200
