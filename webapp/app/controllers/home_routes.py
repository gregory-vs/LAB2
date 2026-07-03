import uuid
from datetime import datetime, timedelta, timezone

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from app.services.auth_service import authenticate_user, create_user
from app.services.cart_service import create_cart, delete_cart, list_carts, update_cart
from app.services.reward_admin_service import (
    create_reward,
    delete_reward,
    list_rewards,
    set_reward_active_status,
    update_reward,
)
from app.services.reward_service import find_reward_user, redeem_reward
from app.services.totem_service import (
    create_totem,
    delete_totem,
    list_totems,
    set_totem_active_status,
    update_totem,
)

home_bp = Blueprint("home", __name__)
SESSION_DURATION = timedelta(hours=5)
PUBLIC_ENDPOINTS = {
    "home.login",
    "home.submit_login",
    "home.register",
    "home.submit_register",
    "static",
}


def _session_expires_at() -> datetime:
    return datetime.now(timezone.utc) + SESSION_DURATION


def _is_authenticated() -> bool:
    user_id = session.get("auth_user_id")
    expires_at = session.get("auth_expires_at")
    if not user_id or not expires_at:
        return False

    try:
        expires_at_datetime = datetime.fromisoformat(expires_at)
    except ValueError:
        return False

    return datetime.now(timezone.utc) < expires_at_datetime


@home_bp.before_app_request
def require_login():
    endpoint = request.endpoint
    if endpoint in PUBLIC_ENDPOINTS or (endpoint and endpoint.startswith("static")):
        return None

    if _is_authenticated():
        return None

    session.clear()
    if request.path.startswith("/api/"):
        return jsonify({"error": "Sessao expirada. Faca login novamente."}), 401

    flash("Faca login para acessar esta pagina.", "error")
    return redirect(url_for("home.login", next=request.full_path))


def _serialize_totem(totem) -> dict[str, str | bool]:
    return {
        "id": str(totem.id),
        "slug": totem.slug,
        "nome": totem.nome,
        "local_descricao": totem.local_descricao or "",
        "ativo": bool(totem.ativo),
    }


def _totems_payload(message: str, status_code: int = 200):
    return jsonify(
        {
            "message": message,
            "totems": [_serialize_totem(totem) for totem in list_totems()],
        }
    ), status_code


def _serialize_reward(reward) -> dict[str, str | int | bool]:
    return {
        "id": int(reward.id),
        "imagem": reward.imagem or "",
        "pontos": int(reward.pontos),
        "titulo": reward.titulo,
        "descricao": reward.descricao or "",
        "ativo": bool(reward.ativo),
    }


def _rewards_payload(message: str, status_code: int = 200):
    return jsonify(
        {
            "message": message,
            "rewards": [_serialize_reward(reward) for reward in list_rewards()],
        }
    ), status_code


def _menu_items():
    return [
        {"label": "home", "href": url_for("home.home"), "key": "home"},
        {
            "label": "cadastrar carrinho",
            "href": url_for("home.cadastrar_carrinho"),
            "key": "cadastrar-carrinho",
        },
        {
            "label": "cadastrar totem",
            "href": url_for("home.cadastrar_totem"),
            "key": "cadastrar-totem",
        },
        {
            "label": "Resgatar recompensas",
            "href": url_for("home.resgatar_recompensas"),
            "key": "resgatar-recompensas",
        },
        {
            "label": "Cadastrar recompensas",
            "href": url_for("home.cadastrar_recompensas"),
            "key": "cadastrar-recompensas",
        },
    ]


@home_bp.get("/")
def home():
    return render_template("home.html", menu_items=_menu_items(), page="home")


@home_bp.get("/login")
def login():
    if _is_authenticated():
        return redirect(url_for("home.home"))

    return render_template("login.html", page="login", show_nav=False)


@home_bp.post("/login")
def submit_login():
    username = request.form.get("login", "").strip()
    password = request.form.get("password", "")
    user = authenticate_user(username, password)

    if not user:
        flash("Login ou senha invalidos.", "error")
        return redirect(url_for("home.login"))

    session.clear()
    session.permanent = True
    session["auth_user_id"] = int(user.id)
    session["auth_username"] = user.username
    session["auth_expires_at"] = _session_expires_at().isoformat()

    next_url = request.form.get("next") or url_for("home.home")
    if not next_url.startswith("/"):
        next_url = url_for("home.home")

    return redirect(next_url)


@home_bp.post("/logout")
def logout():
    session.clear()
    flash("Voce saiu da aplicacao.", "success")
    return redirect(url_for("home.login"))


@home_bp.get("/register")
def register():
    return render_template("register.html", page="register", show_nav=False)


@home_bp.post("/register")
def submit_register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    password_confirmation = request.form.get("password_confirmation", "")

    error_message = create_user(username, password, password_confirmation)
    if error_message:
        flash(error_message, "error")
        return redirect(url_for("home.register"))

    flash("Usuario cadastrado com sucesso. Faca login para continuar.", "success")
    return redirect(url_for("home.login"))


@home_bp.route("/cadastrar-carrinho", methods=["GET", "POST"])
def cadastrar_carrinho():
    if request.method == "POST":
        beacon_uuid = request.form.get("beacon_uuid", "").strip()

        error_message = create_cart(beacon_uuid)
        if error_message:
            flash(error_message, "error")
        else:
            flash("Carrinho cadastrado com sucesso.", "success")

        return redirect(url_for("home.cadastrar_carrinho"))

    return render_template(
        "cadastrar_carrinho.html",
        carts=list_carts(),
        menu_items=_menu_items(),
        page="cadastrar-carrinho",
    )


@home_bp.post("/cadastrar-carrinho/<int:cart_id>/editar")
def editar_carrinho(cart_id: int):
    beacon_uuid = request.form.get("beacon_uuid", "").strip()

    error_message = update_cart(cart_id, beacon_uuid)
    if error_message:
        flash(error_message, "error")
    else:
        flash("Carrinho atualizado com sucesso.", "success")

    return redirect(url_for("home.cadastrar_carrinho"))


@home_bp.post("/cadastrar-carrinho/<int:cart_id>/excluir")
def excluir_carrinho(cart_id: int):
    error_message = delete_cart(cart_id)
    if error_message:
        flash(error_message, "error")
    else:
        flash("Carrinho excluido com sucesso.", "success")

    return redirect(url_for("home.cadastrar_carrinho"))


@home_bp.route("/cadastrar-totem", methods=["GET", "POST"])
def cadastrar_totem():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        slug = request.form.get("slug", "").strip()
        local_descricao = request.form.get("local_descricao", "").strip()
        ativo = request.form.get("ativo") == "on"

        error_message = create_totem(slug, nome, local_descricao, ativo)
        if error_message:
            flash(error_message, "error")
        else:
            flash("Totem cadastrado com sucesso.", "success")

        return redirect(url_for("home.cadastrar_totem"))

    return render_template(
        "cadastrar_totem.html",
        serialized_totems=[_serialize_totem(totem) for totem in list_totems()],
        totems=list_totems(),
        menu_items=_menu_items(),
        page="cadastrar-totem",
    )


@home_bp.post("/cadastrar-totem/<uuid:totem_id>/editar")
def editar_totem(totem_id: uuid.UUID):
    nome = request.form.get("nome", "").strip()
    slug = request.form.get("slug", "").strip()
    local_descricao = request.form.get("local_descricao", "").strip()

    error_message = update_totem(totem_id, slug, nome, local_descricao)
    if error_message:
        flash(error_message, "error")
    else:
        flash("Totem atualizado com sucesso.", "success")

    return redirect(url_for("home.cadastrar_totem"))


@home_bp.post("/api/totens")
def cadastrar_totem_api():
    nome = request.form.get("nome", "").strip()
    slug = request.form.get("slug", "").strip()
    local_descricao = request.form.get("local_descricao", "").strip()
    ativo = request.form.get("ativo") == "on"

    error_message = create_totem(slug, nome, local_descricao, ativo)
    if error_message:
        return jsonify({"error": error_message}), 400

    return _totems_payload("Totem cadastrado com sucesso.", 201)


@home_bp.post("/api/totens/<uuid:totem_id>/editar")
def editar_totem_api(totem_id: uuid.UUID):
    nome = request.form.get("nome", "").strip()
    slug = request.form.get("slug", "").strip()
    local_descricao = request.form.get("local_descricao", "").strip()

    error_message = update_totem(totem_id, slug, nome, local_descricao)
    if error_message:
        return jsonify({"error": error_message}), 400

    return _totems_payload("Totem atualizado com sucesso.")


@home_bp.post("/cadastrar-totem/<uuid:totem_id>/ativar")
def ativar_totem(totem_id: uuid.UUID):
    error_message = set_totem_active_status(totem_id, True)
    if error_message:
        flash(error_message, "error")
    else:
        flash("Totem ativado com sucesso.", "success")

    return redirect(url_for("home.cadastrar_totem"))


@home_bp.post("/api/totens/<uuid:totem_id>/ativar")
def ativar_totem_api(totem_id: uuid.UUID):
    error_message = set_totem_active_status(totem_id, True)
    if error_message:
        return jsonify({"error": error_message}), 400

    return _totems_payload("Totem ativado com sucesso.")


@home_bp.post("/cadastrar-totem/<uuid:totem_id>/inativar")
def inativar_totem(totem_id: uuid.UUID):
    error_message = set_totem_active_status(totem_id, False)
    if error_message:
        flash(error_message, "error")
    else:
        flash("Totem inativado com sucesso.", "success")

    return redirect(url_for("home.cadastrar_totem"))


@home_bp.post("/api/totens/<uuid:totem_id>/inativar")
def inativar_totem_api(totem_id: uuid.UUID):
    error_message = set_totem_active_status(totem_id, False)
    if error_message:
        return jsonify({"error": error_message}), 400

    return _totems_payload("Totem inativado com sucesso.")


@home_bp.post("/cadastrar-totem/<uuid:totem_id>/excluir")
def excluir_totem(totem_id: uuid.UUID):
    error_message = delete_totem(totem_id)
    if error_message:
        flash(error_message, "error")
    else:
        flash("Totem excluido com sucesso.", "success")

    return redirect(url_for("home.cadastrar_totem"))


@home_bp.post("/api/totens/<uuid:totem_id>/excluir")
def excluir_totem_api(totem_id: uuid.UUID):
    error_message = delete_totem(totem_id)
    if error_message:
        return jsonify({"error": error_message}), 400

    return _totems_payload("Totem excluido com sucesso.")


@home_bp.get("/resgatar-recompensas")
def resgatar_recompensas():
    return render_template(
        "resgatar_recompensas.html",
        menu_items=_menu_items(),
        page="resgatar-recompensas",
    )


@home_bp.get("/api/resgatar-recompensas/usuario")
def buscar_usuario_recompensa():
    id_type = request.args.get("id_type", "cpf").strip().lower()
    document = request.args.get("document", "").strip()

    user, error_message = find_reward_user(id_type, document)
    if error_message:
        return jsonify({"error": error_message}), 400

    return jsonify(user)


@home_bp.post("/api/resgatar-recompensas")
def resgatar_recompensa_api():
    id_type = request.form.get("id_type", "cpf").strip().lower()
    document = request.form.get("document", "").strip()
    reward_id = request.form.get("reward_id", "").strip()

    user, error_message = redeem_reward(id_type, document, reward_id)
    if error_message:
        return jsonify({"error": error_message}), 400

    return jsonify(
        {
            "message": "Recompensa resgatada com sucesso.",
            **user,
        }
    )


@home_bp.get("/cadastrar-recompensas")
def cadastrar_recompensas():
    return render_template(
        "cadastrar_recompensas.html",
        serialized_rewards=[_serialize_reward(reward) for reward in list_rewards()],
        menu_items=_menu_items(),
        page="cadastrar-recompensas",
    )


@home_bp.post("/api/recompensas")
def cadastrar_recompensa_api():
    imagem = request.form.get("imagem", "").strip()
    pontos = request.form.get("pontos", "").strip()
    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()
    ativo = request.form.get("ativo") == "on"

    error_message = create_reward(imagem, pontos, titulo, descricao, ativo)
    if error_message:
        return jsonify({"error": error_message}), 400

    return _rewards_payload("Recompensa cadastrada com sucesso.", 201)


@home_bp.post("/api/recompensas/<int:reward_id>/editar")
def editar_recompensa_api(reward_id: int):
    imagem = request.form.get("imagem", "").strip()
    pontos = request.form.get("pontos", "").strip()
    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()

    error_message = update_reward(reward_id, imagem, pontos, titulo, descricao)
    if error_message:
        return jsonify({"error": error_message}), 400

    return _rewards_payload("Recompensa atualizada com sucesso.")


@home_bp.post("/api/recompensas/<int:reward_id>/ativar")
def ativar_recompensa_api(reward_id: int):
    error_message = set_reward_active_status(reward_id, True)
    if error_message:
        return jsonify({"error": error_message}), 400

    return _rewards_payload("Recompensa ativada com sucesso.")


@home_bp.post("/api/recompensas/<int:reward_id>/inativar")
def inativar_recompensa_api(reward_id: int):
    error_message = set_reward_active_status(reward_id, False)
    if error_message:
        return jsonify({"error": error_message}), 400

    return _rewards_payload("Recompensa inativada com sucesso.")


@home_bp.post("/api/recompensas/<int:reward_id>/excluir")
def excluir_recompensa_api(reward_id: int):
    error_message = delete_reward(reward_id)
    if error_message:
        return jsonify({"error": error_message}), 400

    return _rewards_payload("Recompensa excluida com sucesso.")
