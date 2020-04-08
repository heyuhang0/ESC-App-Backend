from flask import Blueprint, jsonify
from app.common.auth import auth
from app.models import db, Marker
from app.utils.allocation import allocate

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/run_allocation', methods=['POST'])
@auth.admin_required
def run_allocation():
    reset_allocation()
    skipped = allocate()
    return jsonify({
        'message': 'Completetd successfully',
        'skipped': len(skipped)
    })


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
