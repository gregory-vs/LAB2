import re

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.extensions import db
from app.models.balance import DocumentBalance
from app.models.collection import CollectionSubmission
from app.services.home_service import (
    get_catalog_items,
    get_collection_stats,
    get_recent_activities,
)

home_bp = Blueprint("home", __name__)


def _build_balance_upsert_stmt(document_type: str, document_value: str):
    dialect_name = db.session.get_bind().dialect.name
    if dialect_name == "postgresql":
        insert_stmt = postgres_insert(DocumentBalance).values(
            documento_tipo=document_type,
            documento=document_value,
            pontos=1,
        )
    else:
        insert_stmt = sqlite_insert(DocumentBalance).values(
            documento_tipo=document_type,
            documento=document_value,
            pontos=1,
        )

    return insert_stmt.on_conflict_do_update(
        index_elements=[DocumentBalance.documento_tipo, DocumentBalance.documento],
        set_={
            "pontos": DocumentBalance.pontos + 1,
            "updated_at": db.func.now(),
        },
    )


def _normalize_document(id_type: str, id_number: str) -> str | None:
    if id_type == "cpf":
        cpf = re.sub(r"\D", "", id_number)
        if len(cpf) != 11:
            return None
        return cpf

    passport = re.sub(r"[^A-Za-z0-9]", "", id_number).upper()
    if not re.fullmatch(r"[A-Z]{2}\d{6}", passport):
        return None
    return passport


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

    normalized_document = _normalize_document(id_type, id_number)
    if normalized_document is None:
        flash("Documento inválido para o tipo selecionado.", "error")
        return redirect(url_for("home.home"))

    submission = CollectionSubmission(
        documento_tipo=id_type,
        documento=normalized_document,
        carrinho_id=cart_id,
        totem_id=totem_id,
    )
    db.session.add(submission)
    db.session.execute(_build_balance_upsert_stmt(id_type, normalized_document))
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
