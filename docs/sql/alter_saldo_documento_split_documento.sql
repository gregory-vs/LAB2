ALTER TABLE saldo_documento
ADD COLUMN IF NOT EXISTS documento_tipo VARCHAR(20);

ALTER TABLE saldo_documento
ADD COLUMN IF NOT EXISTS documento VARCHAR(120);

UPDATE saldo_documento
SET documento_tipo = CASE
    WHEN documentos LIKE 'cpf:%' THEN 'cpf'
    WHEN documentos LIKE 'passaporte:%' THEN 'passaporte'
    ELSE 'desconhecido'
END
WHERE documento_tipo IS NULL;

UPDATE saldo_documento
SET documento = regexp_replace(documentos, '^(cpf|passaporte):', '')
WHERE documento IS NULL
  AND documentos IS NOT NULL;

ALTER TABLE saldo_documento
ALTER COLUMN documento_tipo SET NOT NULL;

ALTER TABLE saldo_documento
ALTER COLUMN documento SET NOT NULL;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_name = 'saldo_documento'
          AND constraint_type = 'PRIMARY KEY'
          AND constraint_name = 'saldo_documento_pkey'
    ) THEN
        ALTER TABLE saldo_documento DROP CONSTRAINT saldo_documento_pkey;
    END IF;
END $$;

ALTER TABLE saldo_documento
ADD CONSTRAINT saldo_documento_pkey PRIMARY KEY (documento_tipo, documento);

ALTER TABLE saldo_documento
DROP COLUMN IF EXISTS documentos;
