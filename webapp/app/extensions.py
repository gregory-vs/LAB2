from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_extensions(app: Flask) -> None:
    db.init_app(app)
