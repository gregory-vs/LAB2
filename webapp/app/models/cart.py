import uuid

from app.extensions import db


class Cart(db.Model):
    __tablename__ = "carrinho"

    id = db.Column(db.BigInteger, primary_key=True)
    beacon_uuid = db.Column(db.UUID(as_uuid=True), nullable=False)
    data_cadastro = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    def set_beacon_uuid(self, value: str) -> None:
        self.beacon_uuid = uuid.UUID(value.strip())
