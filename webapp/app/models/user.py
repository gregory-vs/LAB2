from app.extensions import db


class User(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.BigInteger().with_variant(db.Integer, "sqlite"), primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    data_cadastro = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )
    ultimo_login = db.Column(db.DateTime(timezone=True))
