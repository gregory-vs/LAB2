import uuid

from app.extensions import db
from app.models.cart import Cart


def list_carts() -> list[Cart]:
    return Cart.query.order_by(Cart.data_cadastro.desc(), Cart.id.desc()).all()


def create_cart(beacon_uuid: str) -> str | None:
    beacon_uuid = beacon_uuid.strip()
    if not beacon_uuid:
        return "Informe o BLE UUID do carrinho."
    try:
        parsed_uuid = uuid.UUID(beacon_uuid)
    except ValueError:
        return "Informe um BLE UUID valido."

    cart = Cart(beacon_uuid=parsed_uuid)
    db.session.add(cart)
    db.session.commit()
    return None


def update_cart(cart_id: int, beacon_uuid: str) -> str | None:
    beacon_uuid = beacon_uuid.strip()
    if not beacon_uuid:
        return "Informe o BLE UUID do carrinho."
    try:
        parsed_uuid = uuid.UUID(beacon_uuid)
    except ValueError:
        return "Informe um BLE UUID valido."

    cart = db.session.get(Cart, cart_id)
    if cart is None:
        return "Carrinho nao encontrado."

    cart.beacon_uuid = parsed_uuid
    db.session.commit()
    return None


def delete_cart(cart_id: int) -> str | None:
    cart = db.session.get(Cart, cart_id)
    if cart is None:
        return "Carrinho nao encontrado."

    db.session.delete(cart)
    db.session.commit()
    return None
