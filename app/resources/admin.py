from flask import Blueprint, jsonify, render_template, current_app
from flask_restful import fields, marshal_with, reqparse
from app.common.auth import auth
from app.models import db, Marker, User
from app.utils.allocation import allocate
from app.utils.email import send_emails
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
    parser = reqparse.RequestParser()
    parser.add_argument(
        'map_url', type=str,
        default=current_app.config['BACKEND_URL'] + '/maps/page')
    args = parser.parse_args()

    send_emails(
        User.query.all(),
        'Capstone Booth Allocation Result',
        render_template(
            'allocation_notification.html',
            map_url=args.get('map_url')
        ))
    return jsonify({'message': 'Completetd successfully'})


@admin_bp.route('/reset_allocation', methods=['POST'])
@auth.admin_required
def reset_allocation():
    Marker.query.delete()
    db.session.commit()
    return jsonify({'message': 'Completetd successfully'})
