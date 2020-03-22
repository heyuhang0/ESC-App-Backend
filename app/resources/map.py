from flask import Blueprint
from flask_restful import Api, fields, marshal_with, Resource
from app.common.auth import auth
from app.common.exceptions import NotFoundException
from app.models import Map

map_bp = Blueprint('map', __name__)
api = Api(map_bp)

map_field = {
    'id': fields.Integer,
    'name': fields.String,
    'url': fields.String,
    'level': fields.Integer,
    'scale': fields.Float
}


class MapListView(Resource):
    @auth.login_required
    @marshal_with(map_field)
    def get(self):
        return Map.query.all()


class MapView(Resource):
    @auth.login_required
    @marshal_with(map_field)
    def get(self, map_id):
        m = Map.query.filter(Map.id == map_id).first()
        if not m:
            raise NotFoundException(Map)
        return m


api.add_resource(MapListView, '/maps')
api.add_resource(MapView, '/maps/<int:map_id>')
