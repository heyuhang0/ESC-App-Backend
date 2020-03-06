import os
import config
from app import create_app


environment = os.getenv('FLASK_ENV', 'development')
app = create_app(config.app_config[environment])


if __name__ == "__main__":
    app.run()
