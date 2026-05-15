from app.extensions import db


class DocumentBalance(db.Model):
    __tablename__ = "saldo_documento"

    documento_tipo = db.Column(db.String(20), primary_key=True)
    documento = db.Column(db.String(120), primary_key=True)
    pontos = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
