from flask import Flask

from .controllers.home_routes import home_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(home_bp)
    return app
