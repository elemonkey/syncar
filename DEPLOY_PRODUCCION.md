# 🚀 GUÍA DE DEPLOY - SYNCAR 2.0

## ⚠️ REGLA DE ORO

**NUNCA uses `docker compose down -v` en producción**

El flag `-v` elimina volúmenes = PIERDES TODOS LOS DATOS

---

## 📋 DEPLOY ESTÁNDAR (Recomendado)

### Desde tu máquina local:

```bash
# 1. Commit y push de cambios
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0
git add -A
git commit -m "descripción de cambios"
git push origin main

# 2. Deploy en servidor
ssh root@45.14.194.85
cd /opt/import-app
git pull origin main
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# 3. Verificar
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f backend
```

### Un solo comando (después del push):

```bash
ssh root@45.14.194.85 'cd /opt/import-app && git pull && docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml build && docker compose -f docker-compose.prod.yml up -d'
```

---

## 🔄 TIPOS DE DEPLOY

### 1. Deploy Completo (cambios en código)

```bash
ssh root@45.14.194.85
cd /opt/import-app
git pull
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

**Duración**: 3-5 minutos
**Downtime**: ~2 minutos

### 2. Restart Rápido (sin cambios en código)

```bash
ssh root@45.14.194.85
cd /opt/import-app
docker compose -f docker-compose.prod.yml restart
```

**Duración**: 30 segundos
**Downtime**: ~10 segundos

### 3. Restart de Servicio Específico

```bash
ssh root@45.14.194.85
cd /opt/import-app

# Solo backend
docker compose -f docker-compose.prod.yml restart backend celery-worker

# Solo frontend
docker compose -f docker-compose.prod.yml restart frontend

# Solo nginx
docker compose -f docker-compose.prod.yml restart nginx
```

**Duración**: 10-20 segundos
**Downtime**: Solo del servicio afectado

### 4. Update Parcial (solo algunos servicios)

```bash
ssh root@45.14.194.85
cd /opt/import-app
git pull

# Rebuild solo los que cambiaron
docker compose -f docker-compose.prod.yml build backend frontend

# Restart solo esos servicios
docker compose -f docker-compose.prod.yml up -d --no-deps backend frontend celery-worker
```

**Duración**: 1-2 minutos
**Downtime**: ~30 segundos

---

## ✅ CHECKLIST POST-DEPLOY

Ejecuta estos comandos después de cada deploy:

```bash
ssh root@45.14.194.85
cd /opt/import-app

# 1. ✅ Todos los servicios corriendo
docker compose -f docker-compose.prod.yml ps

# 2. ✅ Verificar logs (no debe haber errores)
docker compose -f docker-compose.prod.yml logs --tail 50 backend
docker compose -f docker-compose.prod.yml logs --tail 50 frontend

# 3. ✅ Base de datos accesible
docker exec importapp-postgres pg_isready -U import_user

# 4. ✅ Contar datos (deben estar intactos)
docker exec importapp-postgres psql -U import_user -d import_db -c "
SELECT
  'Importadores' as tabla, COUNT(*) as registros FROM importers
UNION ALL
SELECT 'Categorías', COUNT(*) FROM categories
UNION ALL
SELECT 'Productos', COUNT(*) FROM products;
"

# 5. ✅ API respondiendo
curl -k https://syncar.cl/api/v1/importers | head -20

# 6. ✅ Frontend respondiendo
curl -k https://syncar.cl | head -10
```

---

## 🛡️ BACKUP ANTES DE DEPLOY

**SIEMPRE haz backup antes de cambios grandes:**

```bash
ssh root@45.14.194.85
cd /opt/import-app

# Crear backup
docker exec importapp-postgres pg_dump -U import_user import_db > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Verificar
ls -lh backups/ | tail -5
```

### Restaurar backup (si algo sale mal):

```bash
ssh root@45.14.194.85
cd /opt/import-app

# Restaurar
docker exec -i importapp-postgres psql -U import_user -d import_db < backups/backup_20241018_150000.sql

# Verificar
docker exec importapp-postgres psql -U import_user -d import_db -c "SELECT COUNT(*) FROM products;"
```

---

## 📊 INFORMACIÓN DEL SISTEMA

### Base de Datos:

- **Host**: postgres (contenedor)
- **Puerto**: 5432
- **Usuario**: import_user
- **Password**: import_password_prod_2024
- **Base de Datos**: import_db
- **Volumen**: import-app_postgres_data

### Acceder a PostgreSQL:

```bash
ssh root@45.14.194.85
docker exec -it importapp-postgres psql -U import_user -d import_db

# Comandos útiles en psql:
\dt                    # Listar tablas
\d products            # Descripción de tabla
SELECT COUNT(*) FROM products;
\q                     # Salir
```

### URLs de la aplicación:

- **Frontend**: https://syncar.cl
- **API Docs**: https://syncar.cl/api/docs
- **Importers**: https://syncar.cl/importers
- **Catálogo**: https://syncar.cl/catalogo
- **Flower**: https://syncar.cl:5555

---

## 🔍 TROUBLESHOOTING

### Servicio no inicia:

```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs backend

# Reiniciar
docker compose -f docker-compose.prod.yml restart backend
```

### Base de datos no conecta:

```bash
# Verificar postgres
docker compose -f docker-compose.prod.yml ps postgres

# Ver logs
docker logs importapp-postgres

# Reiniciar
docker compose -f docker-compose.prod.yml restart postgres
```

### Nginx muestra 502 Bad Gateway:

```bash
# Ver logs
docker logs importapp-nginx

# Verificar que backend esté corriendo
docker ps | grep backend

# Reiniciar
docker compose -f docker-compose.prod.yml restart nginx backend
```

### Olvidé hacer backup y perdí datos:

```bash
# Ver si hay backups automáticos
ls -la /opt/import-app/backups/

# Ver volúmenes antiguos
docker volume ls | grep postgres

# Si no hay backups, los datos se perdieron 😢
# Por eso SIEMPRE haz backup antes de deploy
```

---

## 🚨 COMANDOS PROHIBIDOS EN PRODUCCIÓN

### ❌ NUNCA EJECUTES:

```bash
docker compose down -v              # Elimina volúmenes = PIERDES DATOS
docker volume rm postgres_data      # Elimina datos permanentemente
docker system prune -a --volumes    # Elimina TODO incluidos datos
rm -rf backups/                     # Elimina backups
```

### ✅ USA EN SU LUGAR:

```bash
docker compose down                 # Sin -v = preserva datos
docker volume ls                    # Solo listar, no eliminar
docker system prune -a              # Sin --volumes
ls backups/                         # Solo listar
```

---

## 📝 WORKFLOW RECOMENDADO

### Desarrollo → Producción:

```bash
# 1. Desarrollar en local
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0
# ... hacer cambios ...

# 2. Probar localmente
make dev-backend    # Terminal 1
make dev-frontend   # Terminal 2
# ... probar en http://localhost:3000 ...

# 3. Commit
git add -A
git commit -m "feat: descripción del cambio"
git push origin main

# 4. Backup en producción
ssh root@45.14.194.85 'cd /opt/import-app && docker exec importapp-postgres pg_dump -U import_user import_db > backups/backup_$(date +%Y%m%d_%H%M%S).sql'

# 5. Deploy
ssh root@45.14.194.85 'cd /opt/import-app && git pull && docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml build && docker compose -f docker-compose.prod.yml up -d'

# 6. Verificar
ssh root@45.14.194.85 'cd /opt/import-app && docker compose -f docker-compose.prod.yml ps'
curl -k https://syncar.cl

# 7. Monitorear logs por 2-3 minutos
ssh root@45.14.194.85 'docker compose -f /opt/import-app/docker-compose.prod.yml logs -f backend'
```

---

## 📞 COMANDOS RÁPIDOS

### Deploy completo:
```bash
ssh root@45.14.194.85 'cd /opt/import-app && git pull && docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml build && docker compose -f docker-compose.prod.yml up -d'
```

### Backup:
```bash
ssh root@45.14.194.85 'docker exec importapp-postgres pg_dump -U import_user import_db' > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Ver estado:
```bash
ssh root@45.14.194.85 'docker compose -f /opt/import-app/docker-compose.prod.yml ps'
```

### Ver logs:
```bash
ssh root@45.14.194.85 'docker compose -f /opt/import-app/docker-compose.prod.yml logs -f backend'
```

---

## ✅ RESUMEN

1. **SIN `-v`**: Nunca uses `docker compose down -v`
2. **Backup primero**: Siempre haz backup antes de deploy grande
3. **Verificar después**: Checklist post-deploy obligatorio
4. **Git flow**: Commit → Push → Backup → Deploy → Verificar

**Con esta guía, tus datos están seguros.** 🛡️
