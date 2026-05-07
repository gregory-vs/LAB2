from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_extensions(app: Flask) -> None:
    """Inicializa extensões Flask quando forem adicionadas ao projeto."""
    db.init_app(app)
