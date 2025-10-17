-- Script SQL para inicializar datos básicos
-- Ejecutar en la base de datos syncar_db

-- Insertar importadores si no existen
INSERT INTO importers (code, name, description, is_active, created_at, updated_at)
VALUES
    ('noriega', 'Noriega', 'Importador de productos desde Noriega', true, NOW(), NOW()),
    ('alsacia', 'Alsacia', 'Importador de productos desde Alsacia', false, NOW(), NOW()),
    ('emasa', 'Emasa', 'Importador de productos desde Emasa', false, NOW(), NOW()),
    ('refax', 'Refax', 'Importador de productos desde Refax', false, NOW(), NOW())
ON CONFLICT (code) DO NOTHING;

-- Insertar configuración para Noriega
INSERT INTO importer_configs (importer_id, credentials, is_active, created_at, updated_at)
SELECT id, '{}'::jsonb, true, NOW(), NOW()
FROM importers
WHERE code = 'noriega'
AND NOT EXISTS (
    SELECT 1 FROM importer_configs WHERE importer_id = importers.id
);

-- Verificar
SELECT 'Importadores creados:' as info;
SELECT code, name, is_active FROM importers ORDER BY code;

SELECT '' as separator;
SELECT 'Configuraciones creadas:' as info;
SELECT ic.id, i.code as importer, ic.is_active
FROM importer_configs ic
JOIN importers i ON ic.importer_id = i.id;
