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
