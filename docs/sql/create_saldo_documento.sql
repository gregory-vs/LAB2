CREATE TABLE IF NOT EXISTS saldo_documento (
    documento_tipo VARCHAR(20) NOT NULL,
    documento VARCHAR(120) NOT NULL,
    pontos INTEGER NOT NULL DEFAULT 0 CHECK (pontos >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (documento_tipo, documento)
);
