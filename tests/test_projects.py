from tests import TestBase
from app.models import db, User


class TestProject(TestBase):
    def setup_class(self):
        super().setup_class(self)
        self.student = User(
            email='student@test.com',
            password='studentpassword',
            full_name='Student',
            is_admin=False
        )
        db.session.add(self.student)
        db.session.commit()

    def test_post(self):
        rv = self.client.post('/projects', data={
            'name': 'NHB_Spatial Autonomy',
            'type': '1:01 light installation',
            'space_x': 20,
            'space_y': 10,
            'space_z': 2.5
        }, headers={'Authorization': 'Bearer ' + self.student.token})
        assert rv.status_code == 200
        assert rv.json['name'] == 'NHB_Spatial Autonomy'
        assert rv.json['type'] == '1:01 light installation'
        assert rv.json['space_x'] == 20
        assert rv.json['space_y'] == 10
        assert rv.json['space_z'] == 2.5

    def test_post_multiple(self):
        rv = self.client.post('/projects', data={
            'name': 'NHB_Spatial Autonomy',
            'type': '1:01 light installation',
            'space_x': 25,
            'space_y': 12,
            'space_z': 2
        }, headers={'Authorization': 'Bearer ' + self.student.token})
        assert rv.status_code == 400
        assert 'Only one submission allowed' in rv.json['message']


