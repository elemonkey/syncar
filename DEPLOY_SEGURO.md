# 🚀 Deploy Completo a Producción - SYNCAR 2.0

## ⚠️ IMPORTANTE: Deploy Automatizado y Seguro

Este script de deploy:
- ✅ **Libera puertos automáticamente** (80, 5555)
- ✅ **Detiene frontend dev temporalmente** (puerto 3000)
- ✅ **Preserva servicios dev** (PostgreSQL 5432, Redis 6379, Backend 8000)
- ✅ **Elimina imágenes antiguas** para forzar rebuild completo
- ✅ **Limpia volúmenes no utilizados** (excepto los de dev)
- ✅ **Construye desde cero** con `--no-cache --pull`
- ✅ **Verifica todos los servicios** antes de finalizar
- ✅ **Reinicia servicios dev** si es necesario

---

## 🎯 Deploy en Un Solo Comando

```bash
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0
./scripts/deploy-safe.sh
```

**El script hará todo automáticamente:**

### Paso 1: Liberación de Puertos
- Detecta y cierra procesos en puerto 80
- Detecta y cierra procesos en puerto 5555 (Flower)
- Detiene frontend dev en puerto 3000 (temporalmente)

### Paso 2: Backup
- Crea backup automático de la base de datos producción (si existe)
- Guarda en `backups/backup_YYYYMMDD_HHMMSS.sql`

### Paso 3: Detener Contenedores
- Detiene y elimina contenedores de producción existentes
- Elimina volúmenes asociados (`-v`)

### Paso 4: Limpieza Profunda
- Elimina todas las imágenes antiguas de `importapp`
- Elimina volúmenes no utilizados (preserva los de dev)
- Limpia cache de build de Docker

### Paso 5: Verificar Servicios Dev
- Si PostgreSQL dev no está corriendo → lo inicia
- Si Redis dev no está corriendo → lo inicia
- Asegura que el entorno dev está disponible

### Paso 6: Construir Imágenes
- Build completo con `--no-cache` (sin usar cache)
- Con `--pull` (descarga imágenes base más recientes)
- Fuerza reconstrucción total de todas las capas

### Paso 7: Iniciar Servicios
- Levanta todos los contenedores de producción
- Espera 30 segundos para que inicien
- Verifica que todos los 8 servicios estén corriendo

### Paso 8: Migraciones
- Ejecuta `alembic upgrade head`
- Reintenta hasta 3 veces si falla
- Espera 5 segundos entre intentos

### Verificación Final
- Prueba que backend responde en `/api/docs`
- Prueba que frontend responde en `/`
- Prueba que Flower responde en `:5555`

---

## 📋 Pre-requisitos

### 1. Verifica que Git esté limpio

```bash
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0
git status
```

**Si hay cambios sin commit**, guárdalos:
```bash
git add .
git commit -m "feat: Modal persistente con progreso en tiempo real"
git push origin main
```

### 2. Verifica GitHub Secrets

Asegúrate de tener estos secrets configurados en GitHub:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `SERVER_HOST`
- `SERVER_USER`
- `SERVER_SSH_KEY`
- `POSTGRES_PASSWORD`
- `SECRET_KEY`

Ver: `docs/GITHUB_SECRETS.md`

---

## 🎯 Opciones de Deploy

### Opción 1: Deploy Local con Docker (Recomendado para pruebas)

Este deploy crea contenedores en tu máquina pero en puertos diferentes:

```bash
# 1. Crear archivo .env para producción
cp .env.example .env

# 2. Editar .env con credenciales de producción
nano .env

# 3. Ejecutar deploy
./scripts/deploy.sh
```

**Puertos usados:**
- Frontend: http://localhost (puerto 80)
- Backend API: http://localhost/api
- Flower: http://localhost:5555

**NO afecta:**
- Tu PostgreSQL dev (puerto 5432)
- Tu Redis dev (puerto 6379)
- Tu backend dev (puerto 8000)
- Tu frontend dev (puerto 3000)

---

### Opción 2: Deploy a Servidor Remoto (Producción Real)

Despliega automáticamente vía GitHub Actions:

```bash
# 1. Commit y push tus cambios
git add .
git commit -m "feat: Modal persistente con progreso en tiempo real"
git push origin main

# 2. Crear y push un tag
git tag -a v1.5.0 -m "Modal persistente con progreso en tiempo real"
git push origin v1.5.0
```

Esto activará el workflow `.github/workflows/deploy.yml` que:
1. ✅ Construye las imágenes Docker
2. ✅ Las sube a Docker Hub
3. ✅ Se conecta al servidor vía SSH
4. ✅ Hace backup de la base de datos
5. ✅ Descarga las nuevas imágenes
6. ✅ Actualiza los contenedores
7. ✅ Ejecuta migraciones

---

## 🔒 Deploy Seguro Paso a Paso (Local)

### Paso 1: Detener servidores de desarrollo

```bash
# Detener frontend (Ctrl+C en la terminal donde corre npm run dev)
# Detener backend (Ctrl+C en la terminal donde corre uvicorn)
```

**IMPORTANTE**: NO detengas los contenedores dev (postgres, redis)

### Paso 2: Crear .env de producción

```bash
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0

# Crear .env desde el ejemplo
cp .env.example .env
```

Edita `.env` con estas variables:

```env
# Base de datos (DIFERENTE a dev)
POSTGRES_DB=syncar_prod
POSTGRES_USER=syncar_user
POSTGRES_PASSWORD=tu_password_seguro_aqui

# Backend
SECRET_KEY=genera_un_secret_key_nuevo
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://syncar_user:tu_password_seguro_aqui@postgres:5432/syncar_prod

# Redis
REDIS_URL=redis://redis:6379/0

# Frontend
NEXT_PUBLIC_API_URL=http://localhost/api/v1
```

### Paso 3: Ejecutar deploy

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

El script te preguntará:
- ¿Deseas limpiar imágenes Docker antiguas? → Responde `n` (no)

### Paso 4: Verificar que funciona

```bash
# Ver contenedores
docker ps

# Deberías ver:
# - importapp-postgres (puerto 5432 interno)
# - importapp-redis (puerto 6379 interno)
# - importapp-backend
# - importapp-celery-worker
# - importapp-celery-beat
# - importapp-flower (puerto 5555)
# - importapp-frontend
# - importapp-nginx (puerto 80)

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Paso 5: Probar la aplicación

Abre tu navegador:
- Frontend: http://localhost
- Backend API: http://localhost/api/docs
- Flower: http://localhost:5555

### Paso 6: Restaurar entorno de desarrollo

Si quieres volver a desarrollo:

```bash
# Detener producción
docker-compose -f docker-compose.prod.yml down

# Los contenedores dev seguirán corriendo (postgres-dev, redis-dev)

# Reiniciar backend dev
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Reiniciar frontend dev (en otra terminal)
cd frontend
npm run dev
```

---

## 🔄 Rollback en Caso de Problemas

Si algo sale mal, puedes hacer rollback:

```bash
# 1. Detener producción
docker-compose -f docker-compose.prod.yml down

# 2. Restaurar backup de base de datos (si es necesario)
LATEST_BACKUP=$(ls -t backups/*.sql | head -1)
docker exec -i importapp-postgres psql -U syncar_user syncar_prod < "$LATEST_BACKUP"

# 3. Volver a la versión anterior
git checkout <commit_anterior>
./scripts/deploy.sh
```

---

## 📊 Monitoreo Post-Deploy

### Ver logs en tiempo real

```bash
# Todos los servicios
docker-compose -f docker-compose.prod.yml logs -f

# Solo backend
docker-compose -f docker-compose.prod.yml logs -f backend

# Solo frontend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Verificar base de datos

```bash
# Conectarse a PostgreSQL
docker exec -it importapp-postgres psql -U syncar_user syncar_prod

# Ver tablas
\dt

# Ver productos importados
SELECT COUNT(*) FROM products;

# Salir
\q
```

### Ver tareas de Celery

Abre: http://localhost:5555 (Flower)

---

## 🐛 Troubleshooting

### Problema: Puerto 80 ya está en uso

```bash
# Ver qué proceso usa el puerto 80
sudo lsof -i :80

# Detener nginx local (si existe)
sudo nginx -s stop

# O cambiar el puerto en docker-compose.prod.yml:
# nginx:
#   ports:
#     - "8080:80"  # Usa puerto 8080 en lugar de 80
```

### Problema: Migraciones fallan

```bash
# Entrar al contenedor
docker exec -it importapp-backend bash

# Ver estado de migraciones
alembic current

# Ver historial
alembic history

# Hacer upgrade manualmente
alembic upgrade head

# Salir
exit
```

### Problema: Frontend no se conecta al backend

Verifica que `NEXT_PUBLIC_API_URL` en `.env` apunte a:
- Local: `http://localhost/api/v1`
- Servidor: `https://tu-dominio.com/api/v1`

---

## ✅ Checklist de Deploy Exitoso

- [ ] Contenedores corriendo (`docker ps` muestra 8 servicios)
- [ ] Frontend accesible en http://localhost
- [ ] Backend API en http://localhost/api/docs
- [ ] Flower en http://localhost:5555
- [ ] Migraciones aplicadas (`docker exec importapp-backend alembic current`)
- [ ] Base de datos tiene productos (`docker exec -it importapp-postgres psql -U syncar_user syncar_prod -c "SELECT COUNT(*) FROM products;"`)
- [ ] Logs sin errores críticos
- [ ] Importación de productos funciona
- [ ] Modal persistente funciona

---

## 🎉 Deploy Completado

Si todos los checks están ✅, tu aplicación está corriendo en producción!

**Siguiente paso**: Configurar dominio y SSL con Let's Encrypt (ver `docs/DEPLOY_SERVIDOR.md`)
