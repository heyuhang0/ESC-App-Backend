from base64 import b64encode
from tests import TestBase, mutator


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

    def test_signup_no_fullname(self):
        rv = self.client.post('/users', data={
            'email': 'test2@example.com',
            'password': 'test2password',
        })
        assert rv.status_code == 400
        assert 'Missing' in str(rv.json['message'])

    def test_signup_no_email(self):
        rv = self.client.post('/users', data={
            'password': 'test2password',
            'full_name': 'Test Account 2'
        })
        assert rv.status_code == 400
        assert 'Missing' in str(rv.json['message'])

    def test_signup_no_password(self):
        rv = self.client.post('/users', data={
            'email': 'test2@example.com',
            'full_name': 'Test Account 2'
        })
        assert rv.status_code == 400
        assert 'Missing' in str(rv.json['message'])

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

    def test_login_password_empty(self):
        rv = self.client.get('/users/current', headers={
            'Authorization': gen_authtication('', '')
        })
        assert rv.status_code == 401

    def test_login_wrong_password(self):
        for _ in range(5):
            rv = self.client.get('/users/current', headers={
                'Authorization': gen_authtication(
                    self.TEST_ACCOUNT['email'],
                    mutator.mutate(self.TEST_ACCOUNT['password'])
                )
            })
            assert rv.status_code == 401

    def test_login_wrong_email(self):
        for _ in range(5):
            rv = self.client.get('/users/current', headers={
                'Authorization': gen_authtication(
                    mutator.mutate(self.TEST_ACCOUNT['email']),
                    self.TEST_ACCOUNT['password']
                )
            })
            assert rv.status_code == 401

    def test_login_token(self):
        rv = self.client.get('/users/current', headers={
            'Authorization': 'Bearer ' + self.TEST_ACCOUNT['token']
        })
        assert rv.status_code == 200

    def test_login_token_wrong(self):
        for _ in range(5):
            rv = self.client.get('/users/current', headers={
                'Authorization': 'Bearer ' + mutator.mutate(self.TEST_ACCOUNT['token'])
            })
            assert rv.status_code == 401

    def test_update_user_email(self):
        new_email = 'newemail@example.com'
        rv = self.client.put(
            '/users/current',
            data={'email': new_email},
            headers={'Authorization': 'Bearer ' + self.TEST_ACCOUNT['token']}
        )
        assert rv.status_code == 200
        assert rv.json['email'] == new_email
        rv = self.client.put(
            '/users/current',
            headers={'Authorization': 'Bearer ' + self.TEST_ACCOUNT['token']}
        )
        assert rv.status_code == 200
        assert rv.json['email'] == new_email
        self.TEST_ACCOUNT['email'] = new_email

    def test_update_user_fullname(self):
        new_full_name = 'New Name'
        rv = self.client.put(
            '/users/current',
            data={'full_name': new_full_name},
            headers={'Authorization': 'Bearer ' + self.TEST_ACCOUNT['token']}
        )
        assert rv.status_code == 200
        assert rv.json['full_name'] == new_full_name
        rv = self.client.put(
            '/users/current',
            headers={'Authorization': 'Bearer ' + self.TEST_ACCOUNT['token']}
        )
        assert rv.status_code == 200
        assert rv.json['full_name'] == new_full_name
        self.TEST_ACCOUNT['full_name'] = new_full_name

    def test_update_user_password(self):
        new_password = 'new_password'
        rv = self.client.put(
            '/users/current',
            data={'password': new_password},
            headers={'Authorization': 'Bearer ' + self.TEST_ACCOUNT['token']}
        )
        assert rv.status_code == 200
        self.TEST_ACCOUNT['password'] = new_password

    def test_login_with_new_password(self):
        rv = self.client.get('/users/current', headers={
            'Authorization': gen_authtication(
                self.TEST_ACCOUNT['email'],
                self.TEST_ACCOUNT['password']
            )
        })
        assert rv.status_code == 200
