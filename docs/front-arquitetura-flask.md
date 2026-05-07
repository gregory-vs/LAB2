# Arquitetura de pastas - Front Flask (MVC adaptado)

Este front foi organizado com uma estrutura **MVC adaptada para Flask**:

- **Models**: dados e entidades (`app/models`)
- **Controllers**: rotas HTTP e blueprints (`app/controllers`)
- **Views**: templates HTML (`app/templates`)
- **Services**: regras de negócio (`app/services`)

Também usamos **Application Factory** (`create_app`) para facilitar evolução do projeto.

As telas foram adaptadas dos templates de:

- `stitch_coleta_de_carrinhos_premiada/home_coleta_de_carrinho` → rota `/`
- `stitch_coleta_de_carrinhos_premiada/consulta_de_saldo` → rota `/consulta-saldo`
- `stitch_coleta_de_carrinhos_premiada/cat_logo_de_pr_mios` → rota `/catalogo-premios`

## Estrutura

```text
front/
  app.py
  wsgi.py
  requirements.txt
  app/
    __init__.py
    config.py
    extensions.py
    models/
      __init__.py
      collection.py
      user.py
    controllers/
      __init__.py
      home_routes.py
    services/
      __init__.py
      home_service.py
    templates/
      base.html
      home.html
      consulta_saldo.html
      catalogo_premios.html
    static/
      css/
        main.css
      js/
      img/
```

## Para que serve cada pasta/arquivo

### `front/app.py`
Ponto de entrada para desenvolvimento local. Cria a aplicação via `create_app()` e sobe o servidor Flask.

### `front/wsgi.py`
Entrada para servidores WSGI em produção (Gunicorn, uWSGI etc.). Expõe `app = create_app()`.

### `front/requirements.txt`
Lista de dependências Python do projeto.

### `front/app/__init__.py`
Implementa a **Application Factory** (`create_app`):

1. Cria a instância Flask
2. Carrega configurações
3. Inicializa extensões
4. Registra blueprints (rotas)

### `front/app/config.py`
Configurações centralizadas da aplicação, incluindo:

- `SECRET_KEY`
- `SQLALCHEMY_DATABASE_URI` (via `DATABASE_URL`)
- `SQLALCHEMY_TRACK_MODIFICATIONS`

### `front/app/extensions.py`
Arquivo dedicado para inicializar extensões Flask.  
Atualmente inicializa o `db` (`Flask-SQLAlchemy`).

### `front/app/models/`
Camada de dados (entidades/modelos).  
Atualmente contém:

- `collection.py`: entidade `CollectionSubmission` mapeada para a tabela `formulario`
- `user.py`: exemplo simples de entidade

### `front/app/controllers/`
Camada de controle HTTP:

- define rotas
- recebe requisições
- chama serviços
- retorna respostas/templates

Exemplo atual: `home_routes.py` com as rotas `/`, `/consulta-saldo` e `/catalogo-premios`.
Também possui `POST /coletas` para salvar envios do formulário de coleta.

### `front/app/services/`
Camada de regra de negócio.  
Mantém lógica fora das rotas para evitar controllers “gordos” e facilitar testes/reuso.

### `front/app/templates/`
Views HTML com Jinja2:

- `base.html`: layout base
- `home.html`: home de coleta
- `consulta_saldo.html`: tela de saldo e atividades
- `catalogo_premios.html`: catálogo de recompensas

### `front/app/static/`
Arquivos estáticos:

- `css/`: estilos
- `js/`: scripts
- `img/`: imagens

## Fluxo da requisição (resumo)

1. Usuário acessa uma rota (`/`, `/consulta-saldo` ou `/catalogo-premios`)
2. `home_routes.py` recebe a requisição
3. Controller chama `home_service.py` para obter os dados de tela
4. Controller renderiza o template correspondente
5. Template usa `base.html` + tokens/componentes do CSS em `static/css/main.css`

No fluxo da home (`/`):

1. Usuário envia o formulário de coleta
2. Controller valida os campos obrigatórios
3. Controller persiste em `formulario` (`documentos`, `carrinho_id`, `totem_id`, `timestamp`)
4. UI recebe feedback por mensagem flash (sucesso/erro)

## Mini framework de UI (cores e botões)

O arquivo `app/static/css/main.css` foi organizado como uma base reutilizável para o projeto:

- **Tokens de cor** em `:root` (`--primary`, `--background`, `--surface`, `--outline`, etc.), alinhados ao `precision_utility/DESIGN.md`
- **Componentes de botão**:
  - `.btn` (base)
  - `.btn-primary` (ação principal)
  - `.btn-secondary` (apoio)
  - `.btn-ghost` (ação neutra)
  - `.btn-disabled` (estado desabilitado)
  - `.btn-block` (largura total)
- **Componentes comuns**: `.panel`, `.segment`, `.field`, `.chip`, `.reward-card`, `.activity-item`, além de navegação desktop/mobile compartilhada no `base.html`

## Como evoluir essa arquitetura

- Criar novos módulos por feature (ex.: `qr_routes.py`, `qr_service.py`)
- Adicionar extensão de banco em `extensions.py`
- Manter regra de negócio sempre em `services/` (não nas rotas)
- Reaproveitar layout em `base.html` para novas telas mobile
