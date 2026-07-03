from app.extensions import db
from app.models.user import User
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash


def authenticate_user(username: str, password: str) -> User | None:
    username = username.strip()
    if not username or not password:
        return None

    user = User.query.filter(func.lower(User.username) == username.lower()).first()
    if not user or not user.ativo:
        return None

    if not check_password_hash(user.password_hash, password):
        return None

    user.ultimo_login = func.now()
    db.session.commit()
    return user


def create_user(username: str, password: str, password_confirmation: str) -> str | None:
    username = username.strip()
    if not username:
        return "Informe o usuario."

    if len(username) > 80:
        return "O usuario deve ter no maximo 80 caracteres."

    if len(password) < 8:
        return "A senha deve ter pelo menos 8 caracteres."

    if password != password_confirmation:
        return "A confirmacao da senha nao confere."

    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return "Ja existe um usuario com esse login."

    return None
