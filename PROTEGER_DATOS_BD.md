# 🛡️ PROTEGER DATOS DE BASE DE DATOS EN PRODUCCIÓN

## ⚠️ PROBLEMA IDENTIFICADO

**Estabas perdiendo datos porque usabas `-v` en deploy:**

```bash
# ❌ NUNCA HAGAS ESTO:
docker compose -f docker-compose.prod.yml down -v  # El -v ELIMINA VOLÚMENES = PIERDES DATOS
```

## ✅ COMANDOS CORRECTOS PARA DEPLOY

### 1. Deploy Normal (Preserva datos)

```bash
ssh root@45.14.194.85
cd /opt/import-app

# Pull cambios
git pull origin main

# Rebuild y restart SIN PERDER DATOS
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Verificar
docker compose -f docker-compose.prod.yml ps
```

### 2. Solo Reiniciar Servicios

```bash
# Reiniciar sin rebuild (más rápido)
docker compose -f docker-compose.prod.yml restart

# O reiniciar un servicio específico
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml restart frontend
```

### 3. Actualizar Solo Backend/Frontend

```bash
# Rebuild y restart solo los servicios que cambiaron
docker compose -f docker-compose.prod.yml build backend frontend
docker compose -f docker-compose.prod.yml up -d --no-deps backend frontend celery-worker
```

---

## 📊 BASES DE DATOS ACTUALES

### Volúmenes de Docker:

```bash
# Ver volúmenes
docker volume ls | grep postgres

# Resultado:
syncar_postgres_data         # ANTIGUO - Datos corruptos (17 oct)
import-app_postgres_data     # ACTUAL - Datos vigentes (18 oct)
```

### Base de Datos en Uso:

- **Host**: `postgres` (contenedor Docker)
- **Puerto**: `5432`
- **Usuario**: `import_user`
- **Password**: `import_password_prod_2024`
- **Base de Datos**: `import_db`
- **Volumen**: `import-app_postgres_data`

### Acceder a la BD:

```bash
# Desde el servidor
docker exec -it importapp-postgres psql -U import_user -d import_db

# Ver tablas
\dt

# Ver datos
SELECT * FROM importers;
SELECT * FROM products LIMIT 10;

# Salir
\q
```

---

## 🔒 RESPALDO AUTOMÁTICO

### Script de Backup Diario

Crea un cron job en el servidor:

```bash
ssh root@45.14.194.85

# Editar crontab
crontab -e

# Agregar esta línea (backup diario a las 3 AM)
0 3 * * * cd /opt/import-app && docker exec importapp-postgres pg_dump -U import_user import_db > backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql && find backups/ -name "backup_*.sql" -mtime +7 -delete
```

### Backup Manual:

```bash
ssh root@45.14.194.85
cd /opt/import-app

# Crear backup
docker exec importapp-postgres pg_dump -U import_user import_db > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Verificar
ls -lh backups/
```

### Restaurar Backup:

```bash
ssh root@45.14.194.85
cd /opt/import-app

# Restaurar desde archivo
docker exec -i importapp-postgres psql -U import_user -d import_db < backups/backup_20241018_150000.sql
```

---

## 🚨 REGLAS DE ORO EN PRODUCCIÓN

### ❌ NUNCA HACER:

1. `docker compose down -v` (elimina volúmenes)
2. `docker volume rm postgres_data` (elimina datos)
3. `docker system prune -a --volumes` (elimina TODO)

### ✅ SIEMPRE HACER:

1. `docker compose down` (sin `-v`)
2. Backup antes de cambios grandes
3. Verificar datos después de deploy:
   ```bash
   docker exec importapp-postgres psql -U import_user -d import_db -c "SELECT COUNT(*) FROM products;"
   ```

---

## 📝 CHECKLIST POST-DEPLOY

Después de cada deploy, verifica:

```bash
ssh root@45.14.194.85
cd /opt/import-app

# 1. Servicios corriendo
docker compose -f docker-compose.prod.yml ps

# 2. Base de datos accesible
docker exec importapp-postgres pg_isready -U import_user

# 3. Datos intactos
docker exec importapp-postgres psql -U import_user -d import_db -c "
SELECT
  'Importadores' as tabla, COUNT(*) as registros FROM importers
UNION ALL
SELECT 'Categorías', COUNT(*) FROM categories
UNION ALL
SELECT 'Productos', COUNT(*) FROM products
ORDER BY tabla;
"

# 4. Aplicación respondiendo
curl -k https://syncar.cl/api/v1/importers
curl -k https://syncar.cl
```

---

## 🔧 COMANDOS ÚTILES

### Ver logs sin perder contexto:

```bash
# Todos los logs
docker compose -f docker-compose.prod.yml logs -f

# Solo backend
docker compose -f docker-compose.prod.yml logs -f backend

# Últimas 100 líneas
docker logs importapp-backend --tail 100 -f
```

### Inspeccionar volumen:

```bash
# Ver información del volumen
docker volume inspect import-app_postgres_data

# Ver tamaño
docker system df -v | grep postgres
```

### Limpiar sin perder datos:

```bash
# Limpiar imágenes no usadas (NO volúmenes)
docker image prune -a

# Limpiar contenedores detenidos
docker container prune
```

---

## 🌐 ACCESOS

- **App**: https://syncar.cl
- **API Docs**: https://syncar.cl/api/docs
- **Importers**: https://syncar.cl/importers
- **Catálogo**: https://syncar.cl/catalogo
- **Flower**: https://syncar.cl:5555

---

## 📞 COMANDOS RÁPIDOS

```bash
# Deploy completo SIN PERDER DATOS
ssh root@45.14.194.85 'cd /opt/import-app && git pull && docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml build && docker compose -f docker-compose.prod.yml up -d'

# Backup rápido
ssh root@45.14.194.85 'docker exec importapp-postgres pg_dump -U import_user import_db' > backup_$(date +%Y%m%d_%H%M%S).sql

# Ver estado
ssh root@45.14.194.85 'cd /opt/import-app && docker compose -f docker-compose.prod.yml ps'
```

---

## ✅ RESUMEN

1. **SIN `-v`**: Nunca uses `docker compose down -v` en producción
2. **Backup diario**: Configura cron job para backups automáticos
3. **Verifica post-deploy**: Siempre confirma que los datos siguen ahí
4. **Volumen actual**: `import-app_postgres_data` tiene tus datos

**Tu base de datos está SEGURA ahora. Solo sigue estos comandos.** 🛡️
