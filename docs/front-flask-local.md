# Front-end Flask (MVP) - Execução local

Este diretório contém o setup inicial de um site **mobile-first** com Flask, com três páginas:

- `/` → Home de coleta de carrinho
- `/consulta-saldo` → Consulta de saldo
- `/catalogo-premios` → Catálogo de prêmios

## Pré-requisitos

- Python 3.10+ (ou versão compatível com Flask 3)
- `pip`

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

5. Abra no navegador:

```text
http://127.0.0.1:5000
```

Você verá a tela inicial de coleta de carrinhos.
Você pode navegar entre as telas pela barra superior (desktop) ou barra inferior (mobile).
