from typing import TypedDict

from app.models.reward import Reward


class CatalogItem(TypedDict):
    title: str
    category: str
    points: int
    description: str
    image_url: str
    redeem_enabled: bool


def get_catalog_items() -> list[CatalogItem]:
    rewards = Reward.query.order_by(Reward.ativo.desc(), Reward.pontos.asc(), Reward.id.desc()).all()
    fallback_image_url = "https://placehold.co/600x400?text=Recompensa"

    return [
        {
            "title": reward.titulo,
            "category": "Recompensa",
            "points": reward.pontos,
            "description": reward.descricao or "Sem descricao cadastrada.",
            "image_url": reward.imagem or fallback_image_url,
            "redeem_enabled": bool(reward.ativo),
        }
        for reward in rewards
    ]
