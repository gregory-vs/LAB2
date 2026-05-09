ALTER TABLE formulario
ADD COLUMN IF NOT EXISTS documento_tipo VARCHAR(20);

ALTER TABLE formulario
ADD COLUMN IF NOT EXISTS documento VARCHAR(120);

UPDATE formulario
SET documento_tipo = CASE
    WHEN documentos LIKE 'cpf:%' THEN 'cpf'
    WHEN documentos LIKE 'passaporte:%' THEN 'passaporte'
    ELSE 'desconhecido'
END
WHERE documento_tipo IS NULL;

UPDATE formulario
SET documento = regexp_replace(documentos, '^(cpf|passaporte):', '')
WHERE documento IS NULL
  AND documentos IS NOT NULL;

UPDATE formulario
SET documento = documentos
WHERE documento IS NULL
  AND documentos IS NOT NULL;

UPDATE formulario
SET documento = regexp_replace(documento, '^(cpf|passaporte):', '')
WHERE documento ~ '^(cpf|passaporte):';

ALTER TABLE formulario
ALTER COLUMN documento_tipo SET NOT NULL;

ALTER TABLE formulario
ALTER COLUMN documento SET NOT NULL;

ALTER TABLE formulario
DROP COLUMN IF EXISTS documentos;
