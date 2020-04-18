import os
import csv
import re
import string
from flask import Blueprint, jsonify, request, current_app
from flask_restful import Api, fields, marshal_with, Resource, reqparse
from app.common.auth import auth, ForbiddenException
from app.common.exceptions import NotFoundException, InvalidUsage
from app.models import db, Project
from werkzeug.utils import secure_filename

project_bp = Blueprint('project', __name__)
api = Api(project_bp)

project_fields = {
    'id': fields.Integer,
    'key': fields.Integer(attribute='id'),
    'name': fields.String,
    'type': fields.String,
    'allocated': fields.Boolean,
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


def ascii_str(text, length_limit=-1):
    text = str(text)
    text = ''.join(filter(lambda c: c in set(string.printable), text))
    if length_limit > 0:
        text = text[:length_limit]
    return text


class ProjectListView(Resource):
    @auth.login_required
    @marshal_with(project_fields)
    def get(self):
        if auth.current_user.is_admin:
            # create RequestParser to parse keyword
            keywordParser = reqparse.RequestParser()
            keywordParser.add_argument('id')
            keywordParser.add_argument('name')
            keywordParser.add_argument('type')
            keywordParser.add_argument('space_x')
            keywordParser.add_argument('space_y')
            keywordParser.add_argument('space_z')
            keywordParser.add_argument('creator_id')
            keywordParser.add_argument('updated_on')
            keywordParser.add_argument('prototype_x')
            keywordParser.add_argument('prototype_y')
            keywordParser.add_argument('prototype_z')
            keywordParser.add_argument('prototype_weight')
            keywordParser.add_argument('power_points_count')
            keywordParser.add_argument('pedestal_big_count')
            keywordParser.add_argument('pedestal_small_count')
            keywordParser.add_argument('pedestal_description')
            keywordParser.add_argument('monitor_count')
            keywordParser.add_argument('tv_count')
            keywordParser.add_argument('table_count')
            keywordParser.add_argument('chair_count')
            keywordParser.add_argument('hdmi_to_vga_adapter_count')
            keywordParser.add_argument('hdmi_cable_count')
            keywordParser.add_argument('remark')

            args = keywordParser.parse_args()
            '''#if keyword is present
            if args['name']:
                #use sqlalchemy to do the search, return filtered result
                search = "%{}%".format(args['name'])
                return Project.query.filter(Project.name.like(search)).all()
            #if no keyword, return all'''
            isEmpty = True
            q = db.session.query(Project)
            for attr, value in args.items():
                if args[attr]:
                    isEmpty = False
                    q = q.filter(getattr(Project, attr).like("%%%s%%" % value))
            if isEmpty:
                return Project.query.all()
            else:
                return q.all()
        else:
            return auth.current_user.projects

    def allowed_file(self, filename, allowed_extensions):
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in allowed_extensions

    def parse_csv_line(self, line):
        if len(line) < 4:
            raise InvalidUsage(
                'At least 4 columns (name, type, type description, space requirement)\
                 are required for CSV file'
            )
        result = {}
        result['name'] = ascii_str(line[0], 127)
        result['type'] = ascii_str(line[1] + ' ' + line[2], 127)
        space_numbers = [float(s) for s in re.findall(r"\d+\.?\d*", line[3])]
        use_cm = 'cm' in line[3]
        if use_cm:
            space_numbers = [n / 100 for n in space_numbers]
        result['space_x'] = space_numbers[0] if len(space_numbers) > 0 else 2.0
        result['space_y'] = space_numbers[1] if len(space_numbers) > 1 else 2.0
        result['space_z'] = space_numbers[2] if len(space_numbers) > 2 else 2.0

        # parse other optional parameters
        if len(line) > 4:
            prototype_nums = [float(s) for s in re.findall(r"\d+\.?\d*", line[4])]
            use_cm = 'cm' in line[4]
            result['prototype_weight'] = prototype_nums[3] if len(prototype_nums) > 3 else 0
            if use_cm:
                prototype_nums = [n / 100 for n in prototype_nums]
            result['prototype_x'] = prototype_nums[0] if len(prototype_nums) > 0 else 0
            result['prototype_y'] = prototype_nums[1] if len(prototype_nums) > 1 else 0
            result['prototype_z'] = prototype_nums[2] if len(prototype_nums) > 2 else 0

            mapping = {
                5: (int, 'power_points_count'),
                6: (int, 'pedestal_big_count'),
                7: (int, 'pedestal_small_count'),
                8: (ascii_str, 'pedestal_description'),
                9: (int, 'monitor_count'),
                10: (int, 'tv_count'),
                11: (int, 'table_count'),
                12: (int, 'chair_count'),
                13: (int, 'hdmi_to_vga_adapter_count'),
                14: (int, 'hdmi_cable_count'),
                16: (ascii_str, 'remark')
            }
            for i in range(5, len(line)):
                if i in mapping:
                    dtype = mapping[i][0]
                    dkey = mapping[i][1]
                    try:
                        dvalue = dtype(line[i])
                        result[dkey] = dvalue
                    except Exception:
                        pass
        return result

    @auth.login_required
    @marshal_with(project_fields)
    def post(self):
        # for CSV uploading
        file = request.files.get('file')
        if file and self.allowed_file(file.filename, 'csv'):
            auth.admin_required(lambda: None)()

            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            new_projects = []
            with open(filepath, 'r') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)  # skip headers
                for line in reader:
                    data_dict = self.parse_csv_line(line)
                    data_dict['creator'] = auth.current_user
                    new_project = Project(**data_dict)
                    new_projects.append(new_project)
                    db.session.add(new_project)

            db.session.commit()

            return new_projects

        # for normal uploading
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

    @auth.admin_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ids', type=int, action='append', location='json', required=True)
        args = parser.parse_args()

        to_be_deleted = []
        for project_id in args['ids']:
            project = Project.query.filter(Project.id == project_id).first()
            if not project:
                raise NotFoundException(f'Project {project_id} not found')
            to_be_deleted.append(project)

        for project in to_be_deleted:
            db.session.delete(project)

        db.session.commit()

        return jsonify({'message': 'Project {} deleted'.format(str(args['ids']))})


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
