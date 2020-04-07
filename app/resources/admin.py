from flask import Blueprint, jsonify
from app.common.auth import auth

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/run_allocation', methods=['POST'])
@auth.admin_required
def run_allocation():
    return jsonify({'message': 'Completetd successfully'})


@admin_bp.route('/send_notifications', methods=['POST'])
@auth.admin_required
def send_notifications():
    return jsonify({'message': 'Completetd successfully'})


@admin_bp.route('/reset_allocation', methods=['POST'])
@auth.admin_required
def reset_allocation():
    return jsonify({'message': 'Completetd successfully'})
