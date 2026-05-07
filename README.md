# LAB2

Este repositório está dividido em dois blocos principais:

- **Front** (`front/`): aplicação web Flask (mobile-first).
- **Backend** (`ble-totem/`): serviços de captura/processamento BLE (scanner + totem API).

## Front (Flask)

### Pré-requisitos

- Python 3.10+
- `pip`

### Setup e execução

```bash
cd front
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

A aplicação sobe em `http://127.0.0.1:5000`.

### Banco de dados (PostgreSQL/Azure)

O projeto lê variáveis de ambiente via `.env`.

Exemplo de `front/.env`:

```env
DB_USER=seu_usuario
DB_PASSWORD="sua_senha"
DB_HOST=seu-host.postgres.database.azure.com
DB_PORT=5432
DB_NAME=postgres
DB_SSLMODE=require
```

Se preferir, pode usar `DATABASE_URL` também.

### Tabela do formulário

Script SQL:

```bash
psql "$DATABASE_URL" -f docs/sql/create_formulario.sql
```

## Backend (BLE Totem)

O backend está em `ble-totem/` e possui dois processos:

1. `wsl_totem.py` (API FastAPI para ingestão/status)
2. `windows_scanner.py` (scanner BLE com `bleak`)

### 1) Totem API (WSL/Linux)

```bash
cd ble-totem
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install fastapi uvicorn
uvicorn wsl_totem:app --host 0.0.0.0 --port 8000 --reload
```

### 2) Scanner BLE (Windows)

```bash
cd ble-totem
python -m venv .venv-win
.venv-win\Scripts\activate
pip install bleak
python windows_scanner.py
```

## Documentação complementar

- `docs/front-flask-local.md`
- `docs/front-arquitetura-flask.md`
- `docs/tutorial-totem-ble.md`
