from app.extensions import db
from app.models.reward import Reward


def list_rewards() -> list[Reward]:
    return Reward.query.order_by(Reward.id.desc()).all()


def create_reward(imagem: str, pontos: str, titulo: str, descricao: str, ativo: bool) -> str | None:
    normalized = _normalize_reward_fields(imagem, pontos, titulo, descricao)
    if isinstance(normalized, str):
        return normalized

    reward = Reward(**normalized, ativo=ativo)
    db.session.add(reward)
    db.session.commit()
    return None


def update_reward(reward_id: int, imagem: str, pontos: str, titulo: str, descricao: str) -> str | None:
    reward = db.session.get(Reward, reward_id)
    if reward is None:
        return "Recompensa nao encontrada."

    normalized = _normalize_reward_fields(imagem, pontos, titulo, descricao)
    if isinstance(normalized, str):
        return normalized

    reward.imagem = normalized["imagem"]
    reward.pontos = normalized["pontos"]
    reward.titulo = normalized["titulo"]
    reward.descricao = normalized["descricao"]
    db.session.commit()
    return None


def set_reward_active_status(reward_id: int, ativo: bool) -> str | None:
    reward = db.session.get(Reward, reward_id)
    if reward is None:
        return "Recompensa nao encontrada."

    reward.ativo = ativo
    db.session.commit()
    return None


def delete_reward(reward_id: int) -> str | None:
    reward = db.session.get(Reward, reward_id)
    if reward is None:
        return "Recompensa nao encontrada."

    db.session.delete(reward)
    db.session.commit()
    return None


def _normalize_reward_fields(imagem: str, pontos: str, titulo: str, descricao: str) -> dict[str, str | int | None] | str:
    imagem = imagem.strip()
    titulo = titulo.strip()
    descricao = descricao.strip()

    if not titulo:
        return "Informe o titulo da recompensa."

    try:
        pontos_value = int(pontos)
    except (TypeError, ValueError):
        return "Informe uma quantidade de pontos valida."

    if pontos_value < 0:
        return "A quantidade de pontos nao pode ser negativa."

    return {
        "imagem": imagem or None,
        "pontos": pontos_value,
        "titulo": titulo,
        "descricao": descricao or None,
    }
