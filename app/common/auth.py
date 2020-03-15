from flask import g
from functools import wraps
from itsdangerous import SignatureExpired, BadSignature
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from app.models import User
from app.common.exceptions import InvalidUsage


class UnauthorizedException(InvalidUsage):
    def __init__(self, authenticate_header=None):
        header = {}
        if authenticate_header:
            header['WWW-Authenticate'] = authenticate_header
        super().__init__('Unauthorized Access', 401, header)


class ForbiddenException(InvalidUsage):
    def __init__(self):
        super().__init__('Forbidden', 403)


class Auth(MultiAuth):
    def __init__(self):
        self.basic_auth = HTTPBasicAuth()
        self.token_auth = HTTPTokenAuth()

        @self.basic_auth.verify_password
        def verify_password(email: str, password: str) -> bool:
            user = User.query.filter_by(email=email).first()
            if not user or not user.verify_password(password):
                return False
            g.user = user
            return True

        @self.basic_auth.error_handler
        def basic_auth_error_handler():
            raise UnauthorizedException(self.basic_auth.authenticate_header())

        @self.token_auth.verify_token
        def verify_token(token: str) -> bool:
            try:
                user = User.verify_token(token)
            except (SignatureExpired, BadSignature):
                return False
            g.user = user
            return True

        @self.token_auth.error_handler
        def token_auth_error_handler():
            raise UnauthorizedException(self.token_auth.authenticate_header())

        super().__init__(self.basic_auth, self.token_auth)

    @property
    def current_user(self) -> User:
        return g.user

    def admin_required(self, f):
        @wraps(f)
        @self.login_required
        def decorated(*args, **kwargs):
            if not self.current_user.is_admin:
                raise ForbiddenException()
            return f(*args, **kwargs)
        return decorated


auth = Auth()
