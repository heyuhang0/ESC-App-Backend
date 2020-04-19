import tempfile


class Config():
    """ Common Config """
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = tempfile.gettempdir()

    PASSLIB_CONTEXT_CONFIG = '\n'.join([
        '[passlib]',
        'schemes = sha512_crypt, sha256_crypt',
        'default = sha512_crypt',
        'sha256_crypt__min_rounds = 535000',
        'sha512_crypt__min_rounds = 535000',
        'admin__sha256_crypt__min_rounds = 1024000',
        'admin__sha512_crypt__min_rounds = 1024000',
    ])


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
