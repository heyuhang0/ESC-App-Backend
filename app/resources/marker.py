import json
from flask import Blueprint, jsonify
from flask_restful import Api, fields, marshal_with, Resource, reqparse
from app.common.auth import auth
from app.common.exceptions import NotFoundException
from app.models import db, Map, Marker

marker_bp = Blueprint('marker', __name__)
api = Api(marker_bp)

marker_field = {
    'id': fields.Integer,
    'centre': fields.Nested({
        'x': fields.Integer,
        'y': fields.Integer
    }),
    'polygon': fields.List(fields.Nested({
        'x': fields.Integer,
        'y': fields.Integer
    })),
    'project_id': fields.Integer,
    'project': fields.Nested({
        'id': fields.Integer,
        'name': fields.String
    }),
    'map_id': fields.Integer
}


def polygon(polygon_json):
    """ Return coordinates list if valid, raise an exception in other case. """
    try:
        polygon = json.loads(polygon_json)
        clean_polygon = [{
            'x': int(point['x']),
            'y': int(point['y'])
        } for point in polygon]
        return clean_polygon
    except Exception:
        raise ValueError('{} is not a valid polygon'.format(polygon_json))


class MarkerListView(Resource):
    @auth.login_required
    @marshal_with(marker_field)
    def get(self, map_id):
        m = Map.query.filter(Map.id == map_id).first()
        if not m:
            raise NotFoundException(Map)
        return m.markers

    @auth.admin_required
    @marshal_with(marker_field)
    def post(self, map_id):
        parser = reqparse.RequestParser()
        parser.add_argument('polygon_json', dest='polygon', type=polygon, required=True)
        parser.add_argument('map_id', type=int, required=True)
        parser.add_argument('project_id', type=int)
        args = parser.parse_args()

        marker = Marker(**args)

        if args.get('project_id') == 0:
            marker.project_id = None

        db.session.add(marker)
        db.session.commit()

        return marker


class MarkerView(Resource):
    def get_marker(self, map_id, marker_id):
        marker = Marker.query.filter(
            Marker.map_id == map_id,
            Marker.id == marker_id
        ).first()
        if not marker:
            raise NotFoundException(Marker)
        return marker

    @auth.login_required
    @marshal_with(marker_field)
    def get(self, map_id, marker_id):
        return self.get_marker(map_id, marker_id)

    @auth.admin_required
    @marshal_with(marker_field)
    def put(self, map_id, marker_id):
        parser = reqparse.RequestParser()
        parser.add_argument('polygon_json', dest='polygon', type=polygon)
        parser.add_argument('map_id', type=int)
        parser.add_argument('project_id', type=int)
        args = parser.parse_args()

        marker = self.get_marker(map_id, marker_id)
        for k, v in args.items():
            if v is not None:
                setattr(marker, k, v)

        if args.get('project_id') == 0:
            marker.project_id = None

        db.session.commit()
        return marker

    @auth.admin_required
    def delete(self, map_id, marker_id):
        db.session.delete(self.get_marker(map_id, marker_id))
        db.session.commit()
        return jsonify({'message': f'Marker {marker_id} deleted'})


api.add_resource(MarkerListView, '/maps/<int:map_id>/markers')
api.add_resource(MarkerView, '/maps/<int:map_id>/markers/<int:marker_id>')
