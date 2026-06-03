from flask import Blueprint, redirect, render_template, url_for

home_bp = Blueprint("home", __name__)


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
    return render_template("login.html", page="login", show_nav=False)


@home_bp.post("/login")
def submit_login():
    return redirect(url_for("home.home"))


@home_bp.get("/register")
def register():
    return render_template("register.html", page="register", show_nav=False)


@home_bp.post("/register")
def submit_register():
    return redirect(url_for("home.home"))


@home_bp.get("/cadastrar-carrinho")
def cadastrar_carrinho():
    return render_template(
        "cadastrar_carrinho.html",
        menu_items=_menu_items(),
        page="cadastrar-carrinho",
    )


@home_bp.get("/cadastrar-totem")
def cadastrar_totem():
    return render_template(
        "cadastrar_totem.html",
        menu_items=_menu_items(),
        page="cadastrar-totem",
    )


@home_bp.get("/resgatar-recompensas")
def resgatar_recompensas():
    return render_template(
        "resgatar_recompensas.html",
        menu_items=_menu_items(),
        page="resgatar-recompensas",
    )


@home_bp.get("/cadastrar-recompensas")
def cadastrar_recompensas():
    return render_template(
        "cadastrar_recompensas.html",
        menu_items=_menu_items(),
        page="cadastrar-recompensas",
    )
