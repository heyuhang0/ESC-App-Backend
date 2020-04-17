from flask import Blueprint, jsonify
from flask_restful import fields, marshal_with
from app.common.auth import auth
from app.models import db, Marker
from app.utils.allocation import allocate
from app.resources.project import project_fields

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


allocation_result_fields = {
    'message': fields.String,
    'skipped_count': fields.Integer,
    'skipped': fields.List(fields.Nested(project_fields)),
}


@admin_bp.route('/run_allocation', methods=['POST'])
@auth.admin_required
@marshal_with(allocation_result_fields)
def run_allocation():
    reset_allocation()
    skipped = allocate()
    return {
        'message': 'Completetd successfully',
        'skipped_count': len(skipped),
        'skipped': skipped
    }


@admin_bp.route('/send_notifications', methods=['POST'])
@auth.admin_required
def send_notifications():
    return jsonify({'message': 'Completetd successfully'})


@admin_bp.route('/reset_allocation', methods=['POST'])
@auth.admin_required
def reset_allocation():
    Marker.query.delete()
    db.session.commit()
    return jsonify({'message': 'Completetd successfully'})
