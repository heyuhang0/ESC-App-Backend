import json
from tests import TestBase
from app.models import db, User, Project, Map


class TestMarker(TestBase):
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
        db.session.add(Project(name='Test project'))
        db.session.commit()

    def test_get_maps(self):
        rv = self.client.get(
            '/maps',
            headers={'Authorization': 'Bearer ' + self.admin.token}
        )
        assert rv.status_code == 200
        assert rv.json == [{
            'id': 1,
            'name': 'Campus Centre Level 1',
            'url': 'https://static.sutd-capstone.xyz/floorplan/level1',
            'level': 1,
            'scale': 0.025
        }, {
            'id': 2,
            'name': 'Campus Centre Level 2',
            'url': 'https://static.sutd-capstone.xyz/floorplan/level2',
            'level': 1,
            'scale': 0.017
        }]

    def test_get_map_by_id(self):
        rv = self.client.get(
            '/maps/1',
            headers={'Authorization': 'Bearer ' + self.admin.token}
        )
        assert rv.status_code == 200
        assert rv.json == {
            'id': 1,
            'name': 'Campus Centre Level 1',
            'url': 'https://static.sutd-capstone.xyz/floorplan/level1',
            'level': 1,
            'scale': 0.025
        }

    def test_get_map_page(self):
        rv = self.client.get(
            '/maps/page',
            headers={'Authorization': 'Bearer ' + self.student.token}
        )
        assert rv.status_code == 200

    def test_post_marker_by_student(self):
        rv = self.client.post(
            '/maps/1/markers',
            headers={'Authorization': 'Bearer ' + self.student.token}
        )
        assert rv.status_code == 403

    def test_post_marker_incomplete(self):
        rv = self.client.post(
            '/maps/1/markers',
            headers={'Authorization': 'Bearer ' + self.admin.token},
            data={}
        )
        assert rv.status_code == 400

    def test_post_marker_damaged(self):
        rv = self.client.post(
            '/maps/1/markers',
            headers={'Authorization': 'Bearer ' + self.admin.token},
            data={
                'polygon_json': '[{"x": 500, "y":500},{"y":500},{"x": 1000, "y":1000}]'
            }
        )
        assert rv.status_code == 400

    def test_post_marker_invalid_map(self):
        rv = self.client.post(
            '/maps/0/markers',  # 0 is an invalid map_id
            headers={'Authorization': 'Bearer ' + self.admin.token},
            data={
                'polygon_json': '[{"x": 500, "y":500},{"x": 1000, "y":500},{"x": 1000, "y":1000}]'
            }
        )
        assert rv.status_code == 400

    def test_post_marker(self):
        polygon = [
            {"x": 500, "y": 500},
            {"x": 1000, "y": 500},
            {"x": 1000, "y": 1000},
            {"x": 500, "y": 1000}
        ]
        centre = {"x": 750, "y": 750}
        rv = self.client.post(
            '/maps/1/markers',
            headers={'Authorization': 'Bearer ' + self.admin.token},
            data={
                'polygon_json': json.dumps(polygon)
            }
        )
        assert rv.status_code == 200
        assert rv.json['polygon'] == polygon
        assert rv.json['centre'] == centre
        assert rv.json['map_id'] == 1

    def test_get_markers(self):
        rv = self.client.get(
            '/maps/1/markers',
            headers={'Authorization': 'Bearer ' + self.admin.token},
        )
        assert rv.status_code == 200
        assert len(rv.json) == 1

    def test_get_marker(self):
        rv = self.client.get(
            '/maps/1/markers/1',
            headers={'Authorization': 'Bearer ' + self.admin.token},
        )
        assert rv.status_code == 200
        assert rv.json['id'] == 1
        assert rv.json['map_id'] == 1

    def test_update_marker(self):
        polygon = [
            {"x": 0,   "y": 0},
            {"x": 100, "y": 0},
            {"x": 100, "y": 100},
            {"x": 0,   "y": 100}
        ]
        centre = {"x": 50, "y": 50}
        rv = self.client.put(
            '/maps/1/markers/1',
            headers={'Authorization': 'Bearer ' + self.admin.token},
            data={'polygon_json': json.dumps(polygon)}
        )
        assert rv.status_code == 200
        assert rv.json['polygon'] == polygon
        assert rv.json['centre'] == centre
        assert rv.json['map_id'] == 1

    def test_allocate_project_invalid(self):
        rv = self.client.put(
            '/maps/1/markers/1',
            headers={'Authorization': 'Bearer ' + self.admin.token},
            data={'project_id': 54235}
        )
        assert rv.status_code == 400

    def test_allocate_project(self):
        rv = self.client.put(
            '/maps/1/markers/1',
            headers={'Authorization': 'Bearer ' + self.admin.token},
            data={'project_id': 1}
        )
        assert rv.status_code == 200
        assert rv.json['project_id'] == 1
        assert rv.json['project'] == {
            'id': 1,
            'name': 'Test project'
        }

    def test_allocate_reset(self):
        rv = self.client.put(
            '/maps/1/markers/1',
            headers={'Authorization': 'Bearer ' + self.admin.token},
            data={'project_id': 0}
        )
        assert rv.status_code == 200
        assert rv.json['project_id'] == 0
        assert rv.json['project'] == {
            'id': 0,
            'name': None
        }

    def test_delete_marker(self):
        rv = self.client.delete(
            '/maps/1/markers/1',
            headers={'Authorization': 'Bearer ' + self.admin.token},
            data={'project_id': 0}
        )
        assert rv.status_code == 200

    def test_get_marker_after_delete(self):
        rv = self.client.get(
            '/maps/1/markers/1',
            headers={'Authorization': 'Bearer ' + self.admin.token},
        )
        assert rv.status_code == 404
