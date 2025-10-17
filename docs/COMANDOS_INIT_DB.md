# 🔧 Comandos para Inicializar la Base de Datos

## Ejecuta estos comandos en el servidor

```bash
ssh root@45.14.194.85
cd /root/syncar
```

## 1. Insertar Importadores

```sql
docker exec -i importapp-postgres psql -U elemonkey -d syncar_db << 'EOF'
-- Crear importadores con ENUM
INSERT INTO importers (name, display_name, base_url, is_active, created_at)
VALUES
    ('NORIEGA', 'Noriega', 'https://www.noriegaparts.com', true, NOW()),
    ('ALSACIA', 'Alsacia', 'https://www.alsacia.cl', false, NOW()),
    ('EMASA', 'Emasa', 'https://www.emasa.cl', false, NOW()),
    ('REFAX', 'Refax', 'https://www.refax.cl', false, NOW())
ON CONFLICT (name) DO NOTHING;

-- Verificar
SELECT id, name, display_name, is_active FROM importers;
EOF
```

## 2. Crear Configuración para Noriega

```sql
docker exec -i importapp-postgres psql -U elemonkey -d syncar_db << 'EOF'
-- Insertar config para Noriega
INSERT INTO importer_configs (importer_id, products_per_category, scraping_speed_ms, credentials, is_active, created_at, updated_at)
SELECT
    id,
    10,
    1000,
    '{}'::jsonb,
    true,
    NOW(),
    NOW()
FROM importers
WHERE name = 'NORIEGA'
AND NOT EXISTS (
    SELECT 1 FROM importer_configs WHERE importer_id = importers.id
);

-- Verificar
SELECT ic.id, i.display_name, ic.products_per_category, ic.is_active
FROM importer_configs ic
JOIN importers i ON ic.importer_id = i.id;
EOF
```

## 3. Verificar Todo

```bash
docker exec importapp-postgres psql -U elemonkey -d syncar_db -c "SELECT id, name, display_name, is_active FROM importers;"
docker exec importapp-postgres psql -U elemonkey -d syncar_db -c "SELECT COUNT(*) as total_importers FROM importers;"
docker exec importapp-postgres psql -U elemonkey -d syncar_db -c "SELECT COUNT(*) as total_configs FROM importer_configs;"
```

## 4. Resultado Esperado

Deberías ver:
```
 id |   name   | display_name | is_active
----+----------+--------------+-----------
  1 | NORIEGA  | Noriega      | t
  2 | ALSACIA  | Alsacia      | f
  3 | EMASA    | Emasa        | f
  4 | REFAX    | Refax        | f
```

## Siguiente Paso

Una vez ejecutados estos comandos:

1. Ve a: https://syncar.cl/configuracion
2. Configura las credenciales de Noriega
3. Ve a: https://syncar.cl/importers
4. Importa categorías y productos

## Monitorear

Desde tu Mac:
```bash
./scripts/watch-import.sh
```

¡Listo! 🎉
