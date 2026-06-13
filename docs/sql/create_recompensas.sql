CREATE TABLE IF NOT EXISTS recompensas (
    id BIGSERIAL PRIMARY KEY,
    imagem VARCHAR(2048),
    pontos INTEGER NOT NULL CHECK (pontos >= 0),
    titulo VARCHAR(120) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);
