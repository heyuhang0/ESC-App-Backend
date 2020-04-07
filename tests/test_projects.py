from tests import TestBase
from flask import Blueprint, jsonify
from flask_restful import Api, fields, marshal_with, Resource, reqparse
from app.common.auth import auth, ForbiddenException
from app.common.exceptions import NotFoundException, InvalidUsage
from app.models import db, User, Project


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

    TEST_DATA={
            
        }
    def test_post(self):
        rv = self.client.post('/projects', data={
            'name': 'NHB_Spatial Autonomy',
            'type': '1:01 light installation',
            'space_x': 20,
            'space_y': 10,
            'space_z': 2.5
        },
         headers={'Authorization': 'Bearer ' + self.student.token})
        assert rv.status_code == 200
        assert 'id' in rv.json
        self.TEST_DATA['id'] = rv.json['id']
        assert rv.json['name'] == 'NHB_Spatial Autonomy'
        assert rv.json['type'] == '1:01 light installation'
        assert rv.json['space_x'] == 20
        assert rv.json['space_y'] == 10
        assert rv.json['space_z'] == 2.5

            
    def test_put(self):
        pass

    def test_get(self):
        rv = self.client.get('/projects/current')
        assert 'id' in rv.json
    
    '''def test_search(self):
        rv = self.client.get('/projects?keyword=NHB_Spatial Autonomy')
        assert rv.json['name'] == 'NHB_Spatial Autonomy'
        assert rv.json['type'] == '1:01 light installation'
        assert rv.json['space_x'] == 20
        assert rv.json['space_y'] == 10
        assert rv.json['space_z'] == 2.5
    
    def test_delete(self):
        rv = self.client.get('/projects/current')
        #assert rv.status_code == 200
        self.client.delete('/projects/{}'.format(self.TEST_DATA['id']), self.TEST_DATA['id'] , headers={'Authorization': 'Bearer ' + self.student.token})
        assert 'Project {rv_id} deleted' in rv.json'''

            
    def test_put(self):
        pass

    def test_get(self):
        rv = self.client.get('/projects/current')
        
    
    def test_delete(self):
        rv = self.client.get('/projects/current')
        #assert rv.status_code == 200
        self.client.delete('/projects/{}'.format(self.TEST_DATA['id']), self.TEST_DATA['id'] , headers={'Authorization': 'Bearer ' + self.student.token})
        assert 'Project {rv_id} deleted' in rv.json

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

    

