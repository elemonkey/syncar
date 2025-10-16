# ⚡ Quick Reference - Comandos Esenciales

## 🚀 Inicio Rápido Diario

```bash
# 1. Levantar servicios de infra (solo una vez)
make dev-up

# 2. Backend (Terminal 1)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# 3. Celery (Terminal 2)
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app worker -l INFO

# 4. Frontend (Terminal 3)
cd frontend
npm run dev
```

## 📦 Makefile Commands

```bash
make help              # Ver todos los comandos disponibles

# Desarrollo
make dev-up            # PostgreSQL + Redis en Docker
make dev-down          # Apagar servicios
make dev-backend       # Ejecutar backend
make dev-celery        # Ejecutar Celery worker
make dev-frontend      # Ejecutar frontend

# Producción
make prod-build        # Construir imágenes Docker
make prod-up           # Levantar servicios de producción
make prod-down         # Apagar servicios de producción
make prod-logs         # Ver logs en tiempo real

# Testing
make test-local        # Ejecutar tests

# Utilidades
make shell-db          # Shell de PostgreSQL
make clean             # Limpiar volúmenes y caché

# Instalación (solo primera vez)
make install           # Instalar backend + frontend
make install-backend   # Solo backend
make install-frontend  # Solo frontend
```

## 🗄️ Base de Datos

```bash
# Conectar a PostgreSQL
make shell-db

# O manualmente:
docker exec -it importapp-postgres-dev psql -U admin -d importapp_db

# Comandos útiles dentro de psql:
\dt              # Listar tablas
\d importers     # Describir tabla
SELECT * FROM importers;
\q               # Salir
```

## 🔍 Debugging

```bash
# Ver logs de Docker
docker-compose -f docker-compose.dev.yml logs -f postgres
docker-compose -f docker-compose.dev.yml logs -f redis

# Ver estado de Celery
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app status
celery -A app.tasks.celery_app inspect active

# Flower (UI para Celery)
celery -A app.tasks.celery_app flower
# → http://localhost:5555
```

## 🐍 Python

```bash
# Activar entorno virtual
cd backend
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Instalar nuevas dependencias
pip install nueva_libreria
pip freeze > requirements.txt

# Ejecutar script
python -m app.scripts.mi_script

# Shell interactivo con imports
python
>>> from app.models import Importer
>>> from app.core.database import AsyncSessionLocal
```

## 🎨 Frontend

```bash
cd frontend

# Desarrollo
npm run dev          # Puerto 3000

# Build
npm run build
npm run start

# Linting
npm run lint

# Type checking
npm run type-check

# Instalar nuevas dependencias
npm install nueva_libreria
```

## 🐳 Docker

```bash
# Ver contenedores activos
docker ps

# Ver logs de un contenedor
docker logs importapp-postgres-dev -f

# Entrar a un contenedor
docker exec -it importapp-backend /bin/sh

# Limpiar todo
docker system prune -a --volumes  # ⚠️ CUIDADO: Borra todo

# Rebuild solo un servicio
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml up -d backend
```

## 🔧 Git

```bash
# Push a main (trigger CI/CD)
git add .
git commit -m "feat: implementar auth de alsacia"
git push origin main

# Ver status
git status

# Ver logs
git log --oneline
```

## 📡 API Testing

```bash
# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc

# Health check
curl http://localhost:8000/health

# Test endpoint
curl -X POST http://localhost:8000/api/v1/importers/alsacia/import-categories

# Con httpie (más bonito)
http POST localhost:8000/api/v1/importers/alsacia/import-categories
```

## 🔐 Secrets & Environment

```bash
# Editar variables de entorno
nano .env

# Ver variables cargadas (en Python)
python
>>> from app.core.config import settings
>>> settings.POSTGRES_DB
>>> settings.ALSACIA_USERNAME
```

## 🧪 Playwright

```bash
# Instalar browsers (primera vez)
cd backend
source venv/bin/activate
playwright install chromium

# Ejecutar en modo visible (debugging)
# Edita app/core/config.py: HEADLESS = False

# Codegen (grabar interacciones)
playwright codegen https://ejemplo.com
```

## 📊 Monitoring

```bash
# Flower (Celery)
http://localhost:5555

# Logs del backend
tail -f backend/logs/app.log  # Si está configurado

# Stats de Docker
docker stats
```

## 🚨 Troubleshooting

```bash
# Reset completo de base de datos
make dev-down
docker volume rm syncar20_postgres_data_dev
make dev-up

# Reinstalar Playwright
cd backend
source venv/bin/activate
playwright uninstall --all
playwright install chromium

# Limpiar cache de npm
cd frontend
rm -rf node_modules package-lock.json
npm install

# Ver puertos ocupados
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :3000  # Frontend
```

## 📝 Logs Importantes

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --log-level debug

# Celery
celery -A app.tasks.celery_app worker -l DEBUG

# Docker
docker-compose -f docker-compose.dev.yml logs -f
```

## 🔄 Workflow Típico

```bash
# 1. Mañana: Levantar todo
make dev-up
make dev-backend  # Terminal 1
make dev-celery   # Terminal 2
make dev-frontend # Terminal 3

# 2. Durante el día: Editar código
# → Hot reload automático

# 3. Testing
make test-local

# 4. Commit
git add .
git commit -m "feat: ..."
git push

# 5. Tarde: Apagar
Ctrl+C en cada terminal
make dev-down
```

---

**💾 Guarda este archivo como referencia rápida!**
