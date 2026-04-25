from flask import Blueprint, render_template

from app.services.home_service import (
    get_catalog_items,
    get_collection_stats,
    get_recent_activities,
)

home_bp = Blueprint("home", __name__)


@home_bp.get("/")
def home():
    return render_template("home.html", page="home", stats=get_collection_stats())


@home_bp.get("/catalogo-premios")
def catalogo_premios():
    return render_template(
        "catalogo_premios.html",
        page="catalogo",
        catalog_items=get_catalog_items(),
    )


@home_bp.get("/consulta-saldo")
def consulta_saldo():
    return render_template(
        "consulta_saldo.html",
        page="saldo",
        recent_activities=get_recent_activities(),
    )
