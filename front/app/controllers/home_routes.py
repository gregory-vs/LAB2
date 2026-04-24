from flask import Blueprint, render_template

from app.services.home_service import get_home_message

home_bp = Blueprint("home", __name__)


@home_bp.get("/")
def home():
    return render_template("home.html", message=get_home_message())
