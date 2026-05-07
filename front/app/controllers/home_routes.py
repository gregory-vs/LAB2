from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.models.collection import CollectionSubmission
from app.services.home_service import (
    get_catalog_items,
    get_collection_stats,
    get_recent_activities,
)

home_bp = Blueprint("home", __name__)


@home_bp.get("/")
def home():
    return render_template("home.html", page="home", stats=get_collection_stats())


@home_bp.post("/coletas")
def create_collection():
    id_type = request.form.get("id_type", "cpf").strip().lower()
    id_number = request.form.get("id_number", "").strip()
    cart_id = request.form.get("carrinho_id", "").strip()
    totem_id = request.form.get("totem_id", "").strip()

    allowed_id_types = {"cpf", "passaporte"}
    if id_type not in allowed_id_types:
        flash("Tipo de identificação inválido.", "error")
        return redirect(url_for("home.home"))

    if not id_number or not cart_id or not totem_id:
        flash("Preencha identificação, ID do carrinho e ID do totem.", "error")
        return redirect(url_for("home.home"))

    submission = CollectionSubmission(
        documentos=f"{id_type}:{id_number}",
        carrinho_id=cart_id,
        totem_id=totem_id,
    )
    db.session.add(submission)
    db.session.commit()

    flash("Coleta enviada com sucesso.", "success")
    return redirect(url_for("home.home"))


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
