from config import Config
from app import create_app
from app.models import db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class TestBase:
    def setup_class(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self._app_context = self.app.app_context()
        self._app_context.push()
        db.create_all()

    def teardown_class(self):
        db.session.remove()
        db.drop_all()
        self._app_context.pop()
