import uuid

from app.extensions import db


class Totem(db.Model):
    __tablename__ = "totem"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = db.Column(db.String(32), nullable=False, unique=True)
    nome = db.Column(db.String(120), nullable=False)
    local_descricao = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
