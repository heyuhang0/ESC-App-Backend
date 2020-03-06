from flask import Blueprint, request, jsonify, g
from app import db, basic_auth, token_auth, auth
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return jsonify({
            'message': 'Missing arguments'
        }), 400
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({
            'message': 'user already exists'
        }), 400
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username})


@bp.route('/login')
@auth.login_required
def get_auth_token():
    token = str(g.user.generate_auth_token(), encoding='utf-8')
    return jsonify({'token': token})


@bp.route('/hello')
@auth.login_required
def hello():
    return 'hello ' + g.user.username


@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@token_auth.verify_token
def verify_token(token):
    user = User.verify_auth_token(token)
    if not user:
        return False
    g.user = user
    return True
