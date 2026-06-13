from app.extensions import db


class Reward(db.Model):
    __tablename__ = "recompensas"

    id = db.Column(db.BigInteger, primary_key=True)
    imagem = db.Column(db.String(2048))
    pontos = db.Column(db.Integer, nullable=False)
    titulo = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
