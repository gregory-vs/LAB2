import re
from typing import TypedDict

from app.models.balance import DocumentBalance


class RewardOption(TypedDict):
    id: str
    name: str
    cost: int


class RewardUser(TypedDict):
    document: str
    points: int
    rewards: list[RewardOption]


REWARDS: list[RewardOption] = [
    {"id": "voucher-cafe", "name": "Voucher Cafe", "cost": 50},
    {"id": "desconto-estacionamento", "name": "Desconto no estacionamento", "cost": 120},
    {"id": "acesso-vip", "name": "Acesso VIP", "cost": 300},
    {"id": "mala-extra", "name": "Mala extra", "cost": 450},
]


def normalize_document(id_type: str, document: str) -> str | None:
    if id_type == "cpf":
        normalized = re.sub(r"\D", "", document)
        return normalized if len(normalized) == 11 else None

    if id_type == "passaporte":
        normalized = re.sub(r"[^A-Za-z0-9]", "", document).upper()
        return normalized if re.fullmatch(r"[A-Z]{2}\d{6}", normalized) else None

    return None


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

    available_rewards = [reward for reward in REWARDS if reward["cost"] <= balance.pontos]
    return {
        "document": normalized_document,
        "points": int(balance.pontos),
        "rewards": available_rewards,
    }, None
