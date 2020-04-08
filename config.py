import tempfile


class Config():
    """ Common Config """
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = tempfile.gettempdir()


class DevelopmentConfig(Config):
    """ Development Specific Config """
    DEBUG = True


class ProductionConfig(Config):
    """ Production Specific Config """
    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
