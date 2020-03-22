from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from app.models import db
from app.common.exceptions import InvalidUsage


def create_app(config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    app.config.from_pyfile('config.py')

    # Load extensions
    db.init_app(app)
    CORS(app)
    Migrate(app, db)

    # Exception handling
    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(e: InvalidUsage):
        return e.make_response()

    # Load blueprints
    from app.resources.user import user_bp
    app.register_blueprint(user_bp)

    from app.resources.project import project_bp
    app.register_blueprint(project_bp)

    from app.resources.map import map_bp
    app.register_blueprint(map_bp)

    from app.resources.marker import marker_bp
    app.register_blueprint(marker_bp)

    return app
