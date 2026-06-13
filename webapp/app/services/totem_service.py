import uuid

from app.extensions import db
from app.models.totem import Totem


def list_totems() -> list[Totem]:
    return Totem.query.order_by(Totem.updated_at.desc(), Totem.nome.asc()).all()


def create_totem(slug: str, nome: str, local_descricao: str, ativo: bool) -> str | None:
    slug = slug.strip()
    nome = nome.strip()
    local_descricao = local_descricao.strip()

    if not slug:
        return "Informe o codigo do totem."
    if not nome:
        return "Informe o nome do totem."
    if Totem.query.filter_by(slug=slug).first() is not None:
        return "Ja existe um totem com esse codigo."

    totem = Totem(
        id=uuid.uuid4(),
        slug=slug,
        nome=nome,
        local_descricao=local_descricao or None,
        ativo=ativo,
    )
    db.session.add(totem)
    db.session.commit()
    return None


def update_totem(totem_id: uuid.UUID, slug: str, nome: str, local_descricao: str) -> str | None:
    slug = slug.strip()
    nome = nome.strip()
    local_descricao = local_descricao.strip()

    if not slug:
        return "Informe o codigo do totem."
    if not nome:
        return "Informe o nome do totem."

    totem = db.session.get(Totem, totem_id)
    if totem is None:
        return "Totem nao encontrado."

    existing = Totem.query.filter(Totem.slug == slug, Totem.id != totem_id).first()
    if existing is not None:
        return "Ja existe um totem com esse codigo."

    totem.slug = slug
    totem.nome = nome
    totem.local_descricao = local_descricao or None
    db.session.commit()
    return None


def set_totem_active_status(totem_id: uuid.UUID, ativo: bool) -> str | None:
    totem = db.session.get(Totem, totem_id)
    if totem is None:
        return "Totem nao encontrado."

    totem.ativo = ativo
    db.session.commit()
    return None


def delete_totem(totem_id: uuid.UUID) -> str | None:
    totem = db.session.get(Totem, totem_id)
    if totem is None:
        return "Totem nao encontrado."

    db.session.delete(totem)
    db.session.commit()
    return None
