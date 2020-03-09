from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from app.models import db


def create_app(config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    app.config.from_pyfile('config.py')

    # Load extensions
    db.init_app(app)
    CORS(app)
    Migrate(app, db)

    # Load blueprints
    from app.resources.user import user_bp
    app.register_blueprint(user_bp)

    return app
