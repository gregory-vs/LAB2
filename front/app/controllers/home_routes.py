import re
from datetime import datetime, timedelta, timezone

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.extensions import db
from app.models.balance import DocumentBalance
from app.models.collection import CollectionSubmission
from app.models.totem import Totem
from app.services.home_service import (
    get_catalog_items,
)

home_bp = Blueprint("home", __name__)
UTC_MINUS_3 = timezone(timedelta(hours=-3))
BEACON_EVENT_VALIDITY = timedelta(minutes=10)


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


def _get_balance_from_document(id_type: str, id_number: str) -> tuple[int | None, str | None]:
    allowed_id_types = {"cpf", "passaporte"}
    if id_type not in allowed_id_types:
        return None, "Tipo de identificação inválido."

    normalized_document = _normalize_document(id_type, id_number)
    if normalized_document is None:
        return None, "Documento inválido para o tipo selecionado."

    balance = db.session.get(DocumentBalance, (id_type, normalized_document))
    return (balance.pontos if balance else 0), None


def _format_activity_date(timestamp) -> str:
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(UTC_MINUS_3).strftime("%d/%m/%Y %H:%M")


def _get_recent_activities_from_document(
    id_type: str, id_number: str
) -> tuple[list[dict[str, str | int]], str | None]:
    allowed_id_types = {"cpf", "passaporte"}
    if id_type not in allowed_id_types:
        return [], "Tipo de identificação inválido."

    normalized_document = _normalize_document(id_type, id_number)
    if normalized_document is None:
        return [], "Documento inválido para o tipo selecionado."

    stmt = (
        db.select(CollectionSubmission.timestamp, Totem.nome)
        .select_from(CollectionSubmission)
        .outerjoin(Totem, CollectionSubmission.totem_id == Totem.slug)
        .where(
            CollectionSubmission.documento_tipo == id_type,
            CollectionSubmission.documento == normalized_document,
        )
        .order_by(CollectionSubmission.timestamp.desc())
        .limit(10)
    )
    rows = db.session.execute(stmt).all()

    return [
        {
            "title": f"Coleção {row.nome or 'Totem desconhecido'}",
            "date": _format_activity_date(row.timestamp),
            "points": 1,
        }
        for row in rows
    ], None


def _render_home(prefilled_totem_id: str = "", is_totem_locked: bool = False):
    today_collections = _get_today_collections_by_totem(prefilled_totem_id) if prefilled_totem_id else 0
    return render_template(
        "home.html",
        page="home",
        stats={"today_collections": today_collections},
        prefilled_totem_id=prefilled_totem_id,
        is_totem_locked=is_totem_locked,
        nav_totem_slug=prefilled_totem_id if is_totem_locked else "",
    )


def _get_today_collections_by_totem(totem_id: str) -> int:
    now_local = datetime.now(UTC_MINUS_3)
    start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=1)
    start_utc = start_local.astimezone(timezone.utc)
    end_utc = end_local.astimezone(timezone.utc)

    dialect_name = db.session.get_bind().dialect.name
    if dialect_name == "sqlite":
        start_boundary = start_utc.replace(tzinfo=None)
        end_boundary = end_utc.replace(tzinfo=None)
    else:
        start_boundary = start_utc
        end_boundary = end_utc

    count_stmt = db.select(db.func.count()).select_from(CollectionSubmission).where(
        CollectionSubmission.totem_id == totem_id,
        CollectionSubmission.timestamp >= start_boundary,
        CollectionSubmission.timestamp < end_boundary,
    )
    return db.session.execute(count_stmt).scalar_one()


def _get_active_totem_by_slug_or_none(totem_slug: str) -> Totem | None:
    if not re.fullmatch(r"totem-[A-Z0-9]{8,10}", totem_slug):
        return None
    return Totem.query.filter_by(slug=totem_slug, ativo=True).first()


def _get_active_totem_by_slug_or_404(totem_slug: str) -> Totem:
    totem = _get_active_totem_by_slug_or_none(totem_slug)
    if totem is None:
        abort(404)
    return totem


def _as_aware_utc(timestamp: datetime | str) -> datetime:
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc)


def _validate_latest_beacon_event(totem_id: str, beacon_id: str) -> str | None:
    latest_event = db.session.execute(
        text(
            """
            SELECT status, created_at
            FROM beacon_eventos
            WHERE totem_id = :totem_id
              AND beacon_id = :beacon_id
            ORDER BY created_at DESC
            LIMIT 1
            """
        ),
        {"totem_id": totem_id, "beacon_id": beacon_id},
    ).mappings().first()

    if latest_event is None:
        return "Nenhum evento encontrado para este carrinho neste totem."

    latest_status = str(latest_event["status"] or "").strip().upper()
    if latest_status == "RETIRADO":
        return "Este carrinho consta como retirado e nao pode ser coletado."

    if latest_status != "ENTREGUE":
        return "O ultimo status do carrinho nao permite a coleta."

    created_at = latest_event["created_at"]
    if created_at is None:
        return "Evento do carrinho sem data de criacao."

    event_created_at = _as_aware_utc(created_at)
    if datetime.now(timezone.utc) - event_created_at > BEACON_EVENT_VALIDITY:
        return "O evento de entrega do carrinho expirou. Escaneie um carrinho entregue nos ultimos 10 minutos."

    return None


def _render_catalogo_premios(nav_totem_slug: str = ""):
    return render_template(
        "catalogo_premios.html",
        page="catalogo",
        catalog_items=get_catalog_items(),
        nav_totem_slug=nav_totem_slug,
    )


def _render_consulta_saldo(nav_totem_slug: str = ""):
    id_type = request.args.get("id_type", "cpf").strip().lower()
    id_number = request.args.get("id_number", "").strip()
    current_balance = None
    recent_activities = []

    if id_number:
        current_balance, error_message = _get_balance_from_document(id_type, id_number)
        if error_message:
            flash(error_message, "error")
            current_balance = None
        else:
            recent_activities, activities_error = _get_recent_activities_from_document(id_type, id_number)
            if activities_error:
                flash(activities_error, "error")

    return render_template(
        "consulta_saldo.html",
        page="saldo",
        recent_activities=recent_activities,
        current_balance=current_balance,
        selected_id_type=id_type if id_type in {"cpf", "passaporte"} else "cpf",
        id_number_value=id_number,
        nav_totem_slug=nav_totem_slug,
    )


def _create_collection_submission(
    id_type: str,
    id_number: str,
    cart_id: str,
    totem_id: str,
) -> tuple[str | None, int | None]:
    allowed_id_types = {"cpf", "passaporte"}
    if id_type not in allowed_id_types:
        return "Tipo de identificação inválido.", None

    if not id_number or not cart_id or not totem_id:
        return "Preencha identificação, ID do carrinho e ID do totem.", None

    normalized_document = _normalize_document(id_type, id_number)
    if normalized_document is None:
        return "Documento inválido para o tipo selecionado.", None

    beacon_error = _validate_latest_beacon_event(totem_id, cart_id)
    if beacon_error:
        return beacon_error, None

    submission = CollectionSubmission(
        documento_tipo=id_type,
        documento=normalized_document,
        carrinho_id=cart_id,
        totem_id=totem_id,
    )
    db.session.add(submission)
    db.session.execute(_build_balance_upsert_stmt(id_type, normalized_document))
    db.session.commit()
    return None, _get_today_collections_by_totem(totem_id)


@home_bp.get("/")
def home():
    return _render_home()


@home_bp.post("/coletas")
def create_collection():
    id_type = request.form.get("id_type", "cpf").strip().lower()
    id_number = request.form.get("id_number", "").strip()
    cart_id = request.form.get("carrinho_id", "").strip()
    totem_id = request.form.get("totem_id", "").strip()

    error_message, _ = _create_collection_submission(id_type, id_number, cart_id, totem_id)
    if error_message:
        flash(error_message, "error")
        return redirect(url_for("home.home"))

    flash("Coleta enviada com sucesso.", "success")
    return redirect(url_for("home.home"))


@home_bp.post("/api/coletas")
def create_collection_api():
    id_type = request.form.get("id_type", "cpf").strip().lower()
    id_number = request.form.get("id_number", "").strip()
    cart_id = request.form.get("carrinho_id", "").strip()
    totem_id = request.form.get("totem_id", "").strip()

    error_message, today_collections = _create_collection_submission(id_type, id_number, cart_id, totem_id)
    if error_message:
        return jsonify({"error": error_message}), 400

    return jsonify({"message": "Coleta enviada com sucesso.", "today_collections": today_collections}), 201


@home_bp.get("/catalogo-premios")
def catalogo_premios():
    return _render_catalogo_premios()


@home_bp.get("/consulta-saldo")
def consulta_saldo():
    return _render_consulta_saldo()


@home_bp.get("/api/consulta-saldo")
def consulta_saldo_api():
    id_type = request.args.get("id_type", "cpf").strip().lower()
    id_number = request.args.get("id_number", "").strip()

    if not id_number:
        return jsonify({"error": "Informe um número de identificação."}), 400

    current_balance, error_message = _get_balance_from_document(id_type, id_number)
    if error_message:
        return jsonify({"error": error_message}), 400

    recent_activities, activities_error = _get_recent_activities_from_document(id_type, id_number)
    if activities_error:
        return jsonify({"error": activities_error}), 400

    return jsonify({"balance": current_balance, "recent_activities": recent_activities}), 200


@home_bp.get("/<totem_slug>")
def home_by_totem_slug(totem_slug: str):
    totem = _get_active_totem_by_slug_or_404(totem_slug)
    return _render_home(prefilled_totem_id=totem.slug, is_totem_locked=True)


@home_bp.get("/<totem_slug>/consulta-saldo")
def consulta_saldo_by_totem_slug(totem_slug: str):
    totem = _get_active_totem_by_slug_or_404(totem_slug)
    return _render_consulta_saldo(nav_totem_slug=totem.slug)


@home_bp.get("/<totem_slug>/catalogo-premios")
def catalogo_premios_by_totem_slug(totem_slug: str):
    totem = _get_active_totem_by_slug_or_404(totem_slug)
    return _render_catalogo_premios(nav_totem_slug=totem.slug)
