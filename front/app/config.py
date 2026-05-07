import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def _get_kv_secret(secret_name: str) -> str | None:
     vault_url = os.getenv("KEYVAULT_URL")
     tenant_id = os.getenv("AZURE_TENANT_ID")
     client_id = os.getenv("AZURE_CLIENT_ID")
     client_secret = os.getenv("AZURE_CLIENT_SECRET")

     if not (vault_url and tenant_id and client_id and client_secret):
         return None

     cred = ClientSecretCredential(
         tenant_id=tenant_id,
         client_id=client_id,
         client_secret=client_secret,
     )
     client = SecretClient(vault_url=vault_url, credential=cred)
     return client.get_secret(secret_name).value

def _normalize_database_url(raw_url: str) -> str:
    url = raw_url.strip()
    if url.startswith("jdbc:"):
        url = url.removeprefix("jdbc:")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _build_database_url_from_parts() -> str | None:
    user = os.getenv("DB_USER")
    password = _get_kv_secret(os.getenv("KV_DB_PASSWORD_SECRET"))
    host = _get_kv_secret(os.getenv("KV_DB_HOST_SECRET"))
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    sslmode = os.getenv("DB_SSLMODE", "require")

    if not (user and password and host and db_name):
        return None

    return (
        f"postgresql+psycopg://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{db_name}?sslmode={sslmode}"
    )


def _get_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL")
    if raw_url:
        return _normalize_database_url(raw_url)

    from_parts = _build_database_url_from_parts()
    if from_parts:
        return from_parts

    return "sqlite:///cartcollect.db"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = _get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
