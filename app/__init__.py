from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from flask_cors import CORS


db = SQLAlchemy()
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
auth = MultiAuth(basic_auth, token_auth)


def create_app(config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    app.config.from_pyfile('config.py')

    # Load extensions
    db.init_app(app)
    CORS(app)

    from app import models  # noqa
    Migrate(app, db)

    # Load blueprints
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app
