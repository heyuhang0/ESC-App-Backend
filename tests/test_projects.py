import io
from tests import TestBase
from app.models import db, User, Map


TESTING_CSV = b"""\
Project 1,  1:01,   Light Installation, 5m x 4m,    20cm*10cm*30cm*80kg,    1, 2, 3, descrption1, 4, 5, 6, 7, 8, 9, 10, Remark1
Project 2,      ,   Prototype,          5 x 4 x 3m, 2 x 3                   1, 2, 3, descrption2, 4, 5, 6, 7, 8, 9, 10, Remark2
Project 3,  Prototype, Software,        500 x 400cm,1 X 2 x 1m,             1, 2, 3, descrption3, 4, 5, 6, 7, 8, 9, 10, Remark3
Project 4,  1:01,   ,                   5.00 x 4.00m,    ,                  1, 2, 3, descrption4, 4, 5, 6, 7, 8, 9, 10, Remark4
Project 5,  1:01,   Physical showroom,  5x4m,       20cm*10cm*30cm*80kg,    1, 2, 3, descrption5, 4, 5, 6, 7, 8, 9, 10, Remark5"""


class TestProject(TestBase):
    TEST_DATA = {}

    def setup_class(self):
        super().setup_class(self)
        self.student = User(
            email='student@test.com',
            password='studentpassword',
            full_name='Student',
            is_admin=False
        )
        self.admin = User(
            email='admin@test.com',
            password='adminpassword',
            full_name='Admin',
            is_admin=True
        )
        db.session.add(self.student)
        db.session.add(self.admin)
        db.session.add(Map(
            name='Campus Centre Level 1',
            url='https://static.sutd-capstone.xyz/floorplan/level1',
            level=1,
            scale=0.025
        ))
        db.session.add(Map(
            name='Campus Centre Level 2',
            url='https://static.sutd-capstone.xyz/floorplan/level2',
            level=1,
            scale=0.017
        ))
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
        assert 'id' in rv.json
        self.TEST_DATA['id'] = rv.json['id']
        assert rv.json['key'] == self.TEST_DATA['id']
        assert rv.json['name'] == 'NHB_Spatial Autonomy'
        assert rv.json['type'] == '1:01 light installation'
        assert rv.json['space_x'] == 20
        assert rv.json['space_y'] == 10
        assert rv.json['space_z'] == 2.5

    def test_post_duplicated(self):
        rv = self.client.post('/projects', data={
            'name': 'NHB_Spatial Autonomy',
            'type': '1:01 light installation',
            'space_x': 25,
            'space_y': 12,
            'space_z': 2
        }, headers={'Authorization': 'Bearer ' + self.student.token})
        assert rv.status_code == 400
        assert 'Only one submission allowed' in rv.json['message']

    def test_put(self):
        rv = self.client.put(
            '/projects/{}'.format(self.TEST_DATA['id']),
            data={'name': 'Project 1 NHB_Spatial Autonomy'},
            headers={'Authorization': 'Bearer ' + self.student.token}
        )
        assert rv.status_code == 200
        assert rv.json['name'] == 'Project 1 NHB_Spatial Autonomy'

    def test_get(self):
        rv = self.client.get(
            '/projects/{}'.format(self.TEST_DATA['id']),
            headers={'Authorization': 'Bearer ' + self.student.token}
        )
        assert rv.status_code == 200
        assert rv.json['id'] == self.TEST_DATA['id']
        assert rv.json['key'] == self.TEST_DATA['id']
        assert rv.json['name'] == 'Project 1 NHB_Spatial Autonomy'
        assert rv.json['type'] == '1:01 light installation'
        assert rv.json['space_x'] == 20
        assert rv.json['space_y'] == 10
        assert rv.json['space_z'] == 2.5
        assert not rv.json['allocated']

    def test_delete(self):
        rv = self.client.delete(
            '/projects/{}'.format(self.TEST_DATA['id']),
            headers={'Authorization': 'Bearer ' + self.student.token}
        )
        assert rv.status_code == 200
        assert 'Project {} deleted'.format(self.TEST_DATA['id']) == rv.json['message']

    def test_get_after_delete(self):
        rv = self.client.get(
            '/projects/{}'.format(self.TEST_DATA['id']),
            headers={'Authorization': 'Bearer ' + self.student.token}
        )
        assert rv.status_code == 404

    def test_post_using_csv_by_student(self):
        rv = self.client.post(
            '/projects',
            data={'file': (io.BytesIO(b""), 'test.csv')},
            headers={'Authorization': 'Bearer ' + self.student.token},
            content_type='multipart/form-data'
        )
        assert rv.status_code == 403

    def test_post_using_csv_by_admin(self):
        rv = self.client.post(
            '/projects',
            data={'file': (io.BytesIO(TESTING_CSV), 'test.csv')},
            headers={'Authorization': 'Bearer ' + self.admin.token},
            content_type='multipart/form-data'
        )
        assert rv.status_code == 200
        assert len(rv.json) == 5

    def test_get_list(self):
        rv = self.client.get('/projects', headers={'Authorization': 'Bearer ' + self.admin.token})
        assert rv.status_code == 200
        assert len(rv.json) == 5
        self.TEST_DATA['project_count'] = len(rv.json)
        for i in range(5):
            assert rv.json[i]['name'] == 'Project {}'.format(i + 1)
            assert rv.json[i]['space_x'] == 5
            assert rv.json[i]['space_y'] == 4

    def test_filter_by_name(self):
        rv = self.client.get(
            '/projects',
            data={'name': 'Project 3'},
            headers={'Authorization': 'Bearer ' + self.admin.token}
        )
        assert rv.status_code == 200
        assert len(rv.json) == 1
        assert rv.json[0]['name'] == 'Project 3'

    def test_filter_by_remark(self):
        rv = self.client.get(
            '/projects',
            data={'remark': 'Remark4'},
            headers={'Authorization': 'Bearer ' + self.admin.token}
        )
        assert rv.status_code == 200
        assert len(rv.json) == 1
        assert rv.json[0]['name'] == 'Project 4'

    def test_filter_by_space(self):
        rv = self.client.get(
            '/projects',
            data={'space_z': '3'},
            headers={'Authorization': 'Bearer ' + self.admin.token}
        )
        assert rv.status_code == 200
        assert len(rv.json) == 1
        assert rv.json[0]['name'] == 'Project 2'

    def test_filter_by_multiple(self):
        rv = self.client.get(
            '/projects',
            data={
                'name': 'Project',
                'type': 'ro',
                'prototype_x': '0.2'
            },
            headers={'Authorization': 'Bearer ' + self.admin.token}
        )
        assert rv.status_code == 200
        assert len(rv.json) == 1
        assert rv.json[0]['name'] == 'Project 5'

    def test_allocation(self):
        rv = self.client.post(
            '/admin/run_allocation',
            headers={'Authorization': 'Bearer ' + self.admin.token}
        )
        assert rv.status_code == 200
        assert 'skipped' in rv.json
        self.TEST_DATA['skipped_count'] = rv.json['skipped_count']

    def test_markers_after_allocation(self):
        rv = self.client.get(
            '/maps',
            headers={'Authorization': 'Bearer ' + self.admin.token}
        )
        assert rv.status_code == 200
        maps = rv.json
        marker_count = 0
        for m in maps:
            rv = self.client.get(
                '/maps/{}'.format(m['id']),
                headers={'Authorization': 'Bearer ' + self.admin.token}
            )
            assert rv.status_code == 200
            rv = self.client.get(
                '/maps/{}/markers'.format(m['id']),
                headers={'Authorization': 'Bearer ' + self.admin.token}
            )
            assert rv.status_code == 200
            marker_count += len(rv.json)
        assert marker_count == self.TEST_DATA['project_count'] - self.TEST_DATA['skipped_count']

    def test_send_notifications(self):
        rv = self.client.post(
            '/admin/send_notifications',
            headers={'Authorization': 'Bearer ' + self.admin.token}
        )
        assert rv.status_code == 200
