# Webapp

Aplicacao web em Python com Flask, organizada para espelhar a estrutura do diretorio `front`.

## Requisitos

- Python 3
- `pip`

## Estrutura

```text
webapp/
  app.py
  wsgi.py
  requirements.txt
  app/
    __init__.py
    controllers/
    models/
    services/
    templates/
    static/
```

## Como executar

1. Entre na pasta do projeto:

```bash
cd webapp
```

2. Crie um ambiente virtual:

```bash
python3 -m venv .venv
```

3. Ative o ambiente virtual:

```bash
source .venv/bin/activate
```

4. Instale as dependencias:

```bash
pip install -r requirements.txt
```

5. Inicie a aplicacao:

```bash
python3 app.py
```

6. Abra no navegador:

```text
http://127.0.0.1:5001
```

## Observacoes

- O projeto usa Flask com template Jinja.
- O layout inicial usa Bootstrap 5 via CDN.
- O ponto de entrada para desenvolvimento local e `app.py`.
- O arquivo `wsgi.py` pode ser usado para deploy com servidor WSGI.
