# 🔧 Solución: Base de Datos Vacía

## Problema

Los datos de la base de datos se eliminaron cuando ejecutamos `docker-compose down -v`.
La bandera `-v` elimina los volúmenes, incluyendo los datos de PostgreSQL.

## Solución Rápida

### 1. Conectarte al servidor

```bash
ssh root@45.14.194.85
```
Contraseña: `AGp231512`

### 2. Ir al proyecto

```bash
cd /root/syncar
```

### 3. Ejecutar SQL de inicialización

```bash
docker exec -i importapp-postgres psql -U elemonkey -d syncar_db << 'EOF'
-- Crear importadores
INSERT INTO importers (code, name, description, is_active, created_at, updated_at)
VALUES
    ('noriega', 'Noriega', 'Importador de productos desde Noriega', true, NOW(), NOW()),
    ('alsacia', 'Alsacia', 'Importador de productos desde Alsacia', false, NOW(), NOW()),
    ('emasa', 'Emasa', 'Importador de productos desde Emasa', false, NOW(), NOW()),
    ('refax', 'Refax', 'Importador de productos desde Refax', false, NOW(), NOW())
ON CONFLICT (code) DO NOTHING;

-- Crear configuración para Noriega
INSERT INTO importer_configs (importer_id, credentials, is_active, created_at, updated_at)
SELECT id, '{}'::jsonb, true, NOW(), NOW()
FROM importers
WHERE code = 'noriega'
AND NOT EXISTS (SELECT 1 FROM importer_configs WHERE importer_id = importers.id);

-- Verificar
SELECT 'Importadores:' as tabla;
SELECT code, name, is_active FROM importers;
EOF
```

### 4. Verificar que se crearon los datos

```bash
docker exec importapp-postgres psql -U elemonkey -d syncar_db -c "SELECT code, name FROM importers;"
```

Deberías ver:
```
   code   |   name
----------+----------
 alsacia  | Alsacia
 emasa    | Emasa
 noriega  | Noriega
 refax    | Refax
```

## Luego de la Inicialización

### 1. Ir a Configuración

Abre: https://syncar.cl/configuracion

### 2. Configurar Noriega

- Usuario: Tu usuario de Noriega
- Contraseña: Tu contraseña de Noriega
- Guardar

### 3. Ir a Importers

Abre: https://syncar.cl/importers

Ahora deberías poder:
- ✅ Cargar categorías
- ✅ Seleccionar categorías
- ✅ Importar productos

## Monitorear en Vivo

Desde tu Mac, ejecuta:

```bash
./scripts/watch-import.sh
```

Esto mostrará los logs en tiempo real mientras haces la importación.

## Prevención Futura

Para evitar que esto vuelva a pasar:

### Script de Backup Automático

```bash
# En el servidor
crontab -e
```

Agregar:
```
0 2 * * * docker exec importapp-postgres pg_dump -U elemonkey syncar_db > /root/backups/syncar_$(date +\%Y\%m\%d).sql
```

Esto creará un backup diario a las 2 AM.

### Deploy Seguro

En el futuro, usa:
```bash
./scripts/deploy-safe.sh
```

Este script NO usa la bandera `-v`, preservando los datos.

## ¿Por Qué Pasó Esto?

1. Había contenedores "fantasma" bloqueando el deploy
2. Para limpiarlos, ejecuté `docker-compose down -v`
3. La bandera `-v` elimina **volúmenes** (datos persistentes)
4. Se perdieron:
   - Productos importados
   - Categorías
   - Configuraciones de importadores
   - Trabajos de importación

## Estado Actual

- ✅ Aplicación funcionando
- ✅ SSL configurado
- ✅ Modal persistente activo
- ❌ Base de datos vacía
- 🔄 Necesita reinicialización (sigue los pasos arriba)

## Resumen de Comandos

```bash
# 1. Conectar al servidor
ssh root@45.14.194.85

# 2. Ejecutar el script SQL completo (ver paso 3 arriba)

# 3. Verificar
docker exec importapp-postgres psql -U elemonkey -d syncar_db -c "SELECT * FROM importers;"

# 4. Salir
exit

# 5. Desde tu Mac, monitorear
./scripts/watch-import.sh

# 6. Ir a https://syncar.cl/configuracion y configurar credenciales
# 7. Ir a https://syncar.cl/importers e importar
```

¡Listo! 🎉
