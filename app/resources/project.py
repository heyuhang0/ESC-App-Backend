from flask import Blueprint, jsonify
from flask_restful import Api, fields, marshal_with, Resource, reqparse
from app.common.auth import auth, ForbiddenException
from app.common.exceptions import NotFoundException, InvalidUsage
from app.models import db, Project

project_bp = Blueprint('project', __name__)
api = Api(project_bp)

project_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'type': fields.String,
    'space_x': fields.Float,
    'space_y': fields.Float,
    'space_z': fields.Float,
    'creator_id': fields.Integer,
    'updated_on': fields.DateTime,
    'prototype_x': fields.Float,
    'prototype_y': fields.Float,
    'prototype_z': fields.Float,
    'prototype_weight': fields.Float,
    'power_points_count': fields.Integer,
    'pedestal_big_count': fields.Integer,
    'pedestal_small_count': fields.Integer,
    'pedestal_description': fields.String,
    'monitor_count': fields.Integer,
    'tv_count': fields.Integer,
    'table_count': fields.Integer,
    'chair_count': fields.Integer,
    'hdmi_to_vga_adapter_count': fields.Integer,
    'hdmi_cable_count': fields.Integer,
    'remark': fields.String
}


class ProjectListView(Resource):
    @auth.login_required
    @marshal_with(project_fields)
    def get(self):
        if auth.current_user.is_admin:
            return Project.query.all()
        else:
            return auth.current_user.projects

    @auth.login_required
    @marshal_with(project_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('type', type=str, required=True)
        parser.add_argument('space_x', type=float, required=True)
        parser.add_argument('space_y', type=float, required=True)
        parser.add_argument('space_z', type=float, required=True)
        parser.add_argument('prototype_x', type=float, default=0)
        parser.add_argument('prototype_y', type=float, default=0)
        parser.add_argument('prototype_z', type=float, default=0)
        parser.add_argument('prototype_weight', type=float, default=0)
        parser.add_argument('power_points_count', type=int, default=0)
        parser.add_argument('pedestal_big_count', type=int, default=0)
        parser.add_argument('pedestal_small_count', type=int, default=0)
        parser.add_argument('pedestal_description', type=str, default=0)
        parser.add_argument('monitor_count', type=int, default=0)
        parser.add_argument('tv_count', type=int, default=0)
        parser.add_argument('table_count', type=int, default=0)
        parser.add_argument('chair_count', type=int, default=0)
        parser.add_argument('hdmi_to_vga_adapter_count', type=int, default=0)
        parser.add_argument('hdmi_cable_count', type=int, default=0)
        parser.add_argument('remark', type=str, default='')
        args = parser.parse_args()

        # Students are only allowed to submit one project
        if not auth.current_user.is_admin and len(auth.current_user.projects) > 0:
            raise InvalidUsage('Only one submission allowed')

        project_attributes = dict(args)
        project_attributes['creator'] = auth.current_user
        project = Project(**project_attributes)

        db.session.add(project)
        db.session.commit()

        return project


class ProjectView(Resource):
    @auth.login_required
    def get_project(self, project_id):
        project = Project.query.filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(Project)
        if not auth.current_user.is_admin and project.creator != auth.current_user:
            raise ForbiddenException()
        return project

    @marshal_with(project_fields)
    def get(self, project_id):
        return self.get_project(project_id)

    @marshal_with(project_fields)
    def put(self, project_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('type', type=str)
        parser.add_argument('space_x', type=float)
        parser.add_argument('space_y', type=float)
        parser.add_argument('space_z', type=float)
        parser.add_argument('prototype_x', type=float)
        parser.add_argument('prototype_y', type=float)
        parser.add_argument('prototype_z', type=float)
        parser.add_argument('prototype_weight', type=float)
        parser.add_argument('power_points_count', type=int)
        parser.add_argument('pedestal_big_count', type=int)
        parser.add_argument('pedestal_small_count', type=int)
        parser.add_argument('pedestal_description', type=str)
        parser.add_argument('monitor_count', type=int)
        parser.add_argument('tv_count', type=int)
        parser.add_argument('table_count', type=int)
        parser.add_argument('chair_count', type=int)
        parser.add_argument('hdmi_to_vga_adapter_count', type=int)
        parser.add_argument('hdmi_cable_count', type=int)
        parser.add_argument('remark', type=str)
        args = parser.parse_args()

        project = self.get_project(project_id)
        for k, v in args.items():
            if v is not None:
                setattr(project, k, v)
        db.session.commit()

        return project

    def delete(self, project_id):
        project = self.get_project(project_id)
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': f'Project {project_id} deleted'})


api.add_resource(ProjectListView, '/projects')
api.add_resource(ProjectView, '/projects/<int:project_id>')
