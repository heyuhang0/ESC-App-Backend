from flask import Blueprint
from flask_restful import Api, fields, marshal_with, Resource, reqparse
from app.common.auth import auth
from app.common.exceptions import InvalidUsage
from app.models import db, User

user_bp = Blueprint('user', __name__)
api = Api(user_bp)

user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'full_name': fields.String,
    'is_admin': fields.Boolean
}


class UserListView(Resource):
    @auth.admin_required
    @marshal_with(user_fields)
    def get(self):
        return User.query.all()

    @marshal_with(user_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('full_name', type=str, required=True)
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            raise InvalidUsage('User already exists')

        user = User(
            email=args['email'],
            password=args['password'],
            full_name=args['full_name']
        )
        db.session.add(user)
        db.session.commit()

        return user


class UserView(Resource):
    @auth.login_required
    @marshal_with(user_fields)
    def get(self):
        return auth.current_user

    @auth.login_required
    @marshal_with(user_fields)
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('full_name', type=str)
        args = parser.parse_args()

        user = auth.current_user

        for k, v in args.items():
            if v is not None:
                setattr(user, k, v)
        db.session.commit()

        return user


class UserTokenView(Resource):
    @auth.login_required
    def get(self):
        return {'token': auth.current_user.token}


api.add_resource(UserListView, '/users')
api.add_resource(UserView, '/users/current')
api.add_resource(UserTokenView, '/users/current/token')
