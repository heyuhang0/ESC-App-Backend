from flask import g
from functools import wraps
from itsdangerous import SignatureExpired, BadSignature
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from app.models import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
auth = MultiAuth(basic_auth, token_auth)

login_required = auth.login_required


class UnauthorizedException(Exception):
    pass


def alert_unauthorized():
    raise UnauthorizedException()


basic_auth.error_handler(alert_unauthorized)
token_auth.error_handler(alert_unauthorized)


def current_user() -> User:
    return g.user


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user().is_admin:
            alert_unauthorized()
        return f(*args, **kwargs)
    return decorated


@basic_auth.verify_password
def verify_password(email: str, password: str) -> bool:
    user = User.query.filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


@token_auth.verify_token
def verify_token(token: str) -> bool:
    try:
        user = User.verify_token(token)
    except (SignatureExpired, BadSignature):
        return False
    g.user = user
    return True
