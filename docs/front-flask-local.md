# Front-end Flask (MVP) - Execução local

Este diretório contém o setup inicial de um site **mobile-first** com Flask, com três páginas:

- `/` → Home de coleta de carrinho
- `/consulta-saldo` → Consulta de saldo
- `/catalogo-premios` → Catálogo de prêmios

## Pré-requisitos

- Python 3.10+ (ou versão compatível com Flask 3)
- `pip`

## Configuração de banco de dados

Por padrão, o projeto usa SQLite com o arquivo local `cartcollect.db`.

Para Azure Database for PostgreSQL, configure a variável de ambiente `DATABASE_URL` antes de iniciar o app:

```bash
export DATABASE_URL="postgresql+psycopg://usuario:senha@servidor.postgres.database.azure.com:5432/seu_banco?sslmode=require"
```

Se você tiver recebido uma URL no formato Java (`jdbc:postgresql://...`), pode usar no `.env`: o projeto converte automaticamente para o formato do SQLAlchemy.

Depois, execute o script SQL de criação da tabela:

```bash
psql "$DATABASE_URL" -f docs/sql/create_formulario.sql
```

Também é possível definir `SECRET_KEY`:

```bash
export SECRET_KEY="uma-chave-secreta"
```

## Como rodar localmente

1. Acesse a pasta do front:

```bash
cd front
```

2. (Opcional, recomendado) Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Inicie o servidor Flask:

```bash
python app.py
```

Na primeira execução, as tabelas do banco são criadas automaticamente.

5. Abra no navegador:

```text
http://127.0.0.1:5000
```

Você verá a tela inicial de coleta de carrinhos.
Você pode navegar entre as telas pela barra superior (desktop) ou barra inferior (mobile).
