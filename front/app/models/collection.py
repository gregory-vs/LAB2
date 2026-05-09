from app.extensions import db


class CollectionSubmission(db.Model):
    __tablename__ = "formulario"

    id = db.Column(db.Integer, primary_key=True)
    documento_tipo = db.Column(db.String(20), nullable=False)
    documento = db.Column(db.String(120), nullable=False)
    carrinho_id = db.Column(db.String(64), nullable=False)
    totem_id = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )
