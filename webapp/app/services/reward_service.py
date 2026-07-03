import re
from typing import TypedDict

from app.extensions import db
from app.models.balance import DocumentBalance
from app.models.reward import Reward


class RewardOption(TypedDict):
    id: int
    name: str
    cost: int


class RewardUser(TypedDict):
    document: str
    points: int
    rewards: list[RewardOption]


def normalize_document(id_type: str, document: str) -> str | None:
    if id_type == "cpf":
        normalized = re.sub(r"\D", "", document)
        return normalized if len(normalized) == 11 else None

    if id_type == "passaporte":
        normalized = re.sub(r"[^A-Za-z0-9]", "", document).upper()
        return normalized if re.fullmatch(r"[A-Z]{2}\d{6}", normalized) else None

    return None


def _serialize_reward_option(reward: Reward) -> RewardOption:
    return {
        "id": int(reward.id),
        "name": reward.titulo,
        "cost": int(reward.pontos),
    }


def _available_rewards(points: int) -> list[RewardOption]:
    rewards = (
        Reward.query.filter_by(ativo=True)
        .filter(Reward.pontos <= points)
        .order_by(Reward.pontos.asc(), Reward.titulo.asc())
        .all()
    )
    return [_serialize_reward_option(reward) for reward in rewards]


def find_reward_user(id_type: str, document: str) -> tuple[RewardUser | None, str | None]:
    normalized_document = normalize_document(id_type, document)
    if normalized_document is None:
        return None, "Documento invalido para o tipo selecionado."

    balance = DocumentBalance.query.filter_by(
        documento_tipo=id_type,
        documento=normalized_document,
    ).first()
    if balance is None:
        return None, "Usuario nao encontrado."

    return {
        "document": normalized_document,
        "points": int(balance.pontos),
        "rewards": _available_rewards(int(balance.pontos)),
    }, None


def redeem_reward(id_type: str, document: str, reward_id: str) -> tuple[RewardUser | None, str | None]:
    normalized_document = normalize_document(id_type, document)
    if normalized_document is None:
        return None, "Documento invalido para o tipo selecionado."

    try:
        parsed_reward_id = int(reward_id)
    except (TypeError, ValueError):
        return None, "Selecione uma recompensa valida."

    balance = (
        DocumentBalance.query.filter_by(
            documento_tipo=id_type,
            documento=normalized_document,
        )
        .with_for_update()
        .first()
    )
    if balance is None:
        return None, "Usuario nao encontrado."

    reward = Reward.query.filter_by(id=parsed_reward_id, ativo=True).first()
    if reward is None:
        return None, "Recompensa nao encontrada ou inativa."

    reward_cost = int(reward.pontos)
    if int(balance.pontos) < reward_cost:
        return None, "Saldo insuficiente para resgatar esta recompensa."

    balance.pontos = int(balance.pontos) - reward_cost
    db.session.commit()

    updated_points = int(balance.pontos)
    return {
        "document": normalized_document,
        "points": updated_points,
        "rewards": _available_rewards(updated_points),
    }, None
