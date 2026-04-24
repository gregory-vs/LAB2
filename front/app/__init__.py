from flask import Flask

from .config import Config
from .controllers.home_routes import home_bp
from .extensions import init_extensions


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_extensions(app)
    app.register_blueprint(home_bp)

    return app
