# 🚀 DEPLOY A PRODUCCIÓN - SYNCAR 2.0

## ✅ Pre-requisitos Completados
- ✅ Código subido a GitHub (commit: f840c1b)
- ✅ Cambios importantes incluidos:
  - Scraping completo de EMASA con aplicaciones
  - Características en formato tabla
  - Auto-refresh de importaciones
  - Modal persistente mejorado
  - Fix de extra_data con flag_modified

---

## 📋 OPCIÓN 1: Deploy vía Git (RECOMENDADO)

### Paso 1: Conectar al servidor

```bash
ssh root@45.14.194.85
```

### Paso 2: Actualizar código en el servidor

```bash
cd /opt/syncar
git pull origin main
```

### Paso 3: Actualizar configuración

```bash
# Verificar que .env está actualizado
cat .env | grep DOMAIN_NAME
# Debería mostrar: DOMAIN_NAME=syncar.cl
```

### Paso 4: Reconstruir y reiniciar

```bash
# Opción A: Rebuild completo (recomendado para cambios importantes)
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Opción B: Restart rápido (solo para cambios menores)
docker-compose -f docker-compose.prod.yml restart backend celery-worker frontend
```

### Paso 5: Ejecutar migraciones (si hay cambios en DB)

```bash
docker exec importapp-backend alembic upgrade head
```

### Paso 6: Verificar servicios

```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Paso 7: Verificar en el navegador

- 🌐 **Frontend**: https://syncar.cl
- 📚 **API Docs**: https://syncar.cl/api/docs
- 📊 **Flower**: https://syncar.cl:5555

---

## 📋 OPCIÓN 2: Deploy Completo desde Cero

Si el servidor NO tiene el código todavía:

### Paso 1: Conectar al servidor

```bash
ssh root@45.14.194.85
```

### Paso 2: Clonar repositorio

```bash
cd /opt
git clone https://github.com/elemonkey/syncar.git
cd syncar
```

### Paso 3: Configurar variables de entorno

```bash
cp .env.production .env
nano .env  # Verificar que todas las variables estén correctas
```

### Paso 4: Hacer deploy

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh
```

### Paso 5: Configurar SSL (si es primera vez)

```bash
# Instalar certbot (si no está)
apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
certbot --nginx -d syncar.cl -d www.syncar.cl --non-interactive --agree-tos --email admin@syncar.cl

# Verificar renovación automática
certbot renew --dry-run
```

---

## 🔄 OPCIÓN 3: Deploy Rápido (Sin Downtime)

Para actualizaciones rápidas sin bajar los servicios:

```bash
ssh root@45.14.194.85
cd /opt/syncar

# Pull de cambios
git pull origin main

# Rebuild solo los servicios que cambiaron
docker-compose -f docker-compose.prod.yml build backend frontend
docker-compose -f docker-compose.prod.yml up -d --no-deps backend frontend celery-worker

# Verificar
docker-compose -f docker-compose.prod.yml ps
```

---

## 🧪 Verificación Post-Deploy

### 1. Servicios corriendo

```bash
docker-compose -f docker-compose.prod.yml ps
```

Deberías ver 8 servicios:
- ✅ postgres (healthy)
- ✅ redis (healthy)
- ✅ backend (up)
- ✅ celery-worker (up)
- ✅ celery-beat (up)
- ✅ flower (up)
- ✅ frontend (up)
- ✅ nginx (up)

### 2. Backend respondiendo

```bash
curl https://syncar.cl/api/docs
# Debería devolver HTML de la documentación
```

### 3. Frontend respondiendo

```bash
curl https://syncar.cl
# Debería devolver HTML de Next.js
```

### 4. Base de datos conectada

```bash
docker exec importapp-backend python -c "from app.core.database import engine; print('✅ DB conectada')"
```

### 5. Logs limpios

```bash
# Backend logs
docker logs importapp-backend --tail 50

# Celery logs
docker logs importapp-celery-worker --tail 50

# Frontend logs
docker logs importapp-frontend --tail 50
```

---

## 🐛 Troubleshooting

### Backend no inicia

```bash
# Ver logs detallados
docker logs importapp-backend -f

# Verificar variables de entorno
docker exec importapp-backend printenv | grep POSTGRES

# Reiniciar
docker-compose -f docker-compose.prod.yml restart backend
```

### Frontend muestra error 502

```bash
# Verificar nginx
docker logs importapp-nginx -f

# Verificar que frontend esté corriendo
docker ps | grep frontend

# Rebuild frontend
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

### Celery no procesa tareas

```bash
# Ver logs de celery
docker logs importapp-celery-worker -f

# Verificar Redis
docker exec importapp-redis redis-cli ping
# Debe responder: PONG

# Reiniciar celery
docker-compose -f docker-compose.prod.yml restart celery-worker
```

### Base de datos sin conexión

```bash
# Verificar postgres
docker exec importapp-postgres pg_isready -U elemonkey

# Ver logs
docker logs importapp-postgres --tail 50

# Conectar a postgres
docker exec -it importapp-postgres psql -U elemonkey -d syncar_db
```

---

## 📊 Comandos Útiles

### Ver todos los logs

```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Ver logs de un servicio específico

```bash
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f celery-worker
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Reiniciar un servicio

```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### Ver uso de recursos

```bash
docker stats
```

### Backup manual de base de datos

```bash
docker exec importapp-postgres pg_dump -U elemonkey syncar_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar backup

```bash
docker exec -i importapp-postgres psql -U elemonkey syncar_db < backup_20241018_150000.sql
```

---

## 🎯 Recomendación

Para esta actualización con cambios importantes (EMASA scraping, aplicaciones, características):

**USA OPCIÓN 1 - Deploy vía Git con rebuild completo:**

```bash
ssh root@45.14.194.85
cd /opt/syncar
git pull origin main
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
docker exec importapp-backend alembic upgrade head
docker-compose -f docker-compose.prod.yml ps
```

**Tiempo estimado: 5-10 minutos**

---

## ✅ Checklist Final

Después del deploy, verifica:

- [ ] https://syncar.cl carga correctamente
- [ ] https://syncar.cl/api/docs muestra la documentación
- [ ] https://syncar.cl/catalogo muestra productos
- [ ] Puedes hacer login en /importers
- [ ] Las importaciones funcionan
- [ ] Las aplicaciones se muestran en el modal de productos
- [ ] Las características se ven en formato tabla
- [ ] Flower está accesible en https://syncar.cl:5555

---

**¿Listo para deployar? 🚀**

Ejecuta los comandos de la **OPCIÓN 1** para hacer el deploy ahora.
