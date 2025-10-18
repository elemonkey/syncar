.PHONY: help dev-up dev-down dev-backend dev-celery dev-frontend prod-build prod-up prod-down prod-logs test-local shell-db clean

# ============================================
# AYUDA
# ============================================
help:
	@echo "📋 Comandos disponibles:"
	@echo ""
	@echo "🔧 DESARROLLO LOCAL:"
	@echo "  make dev-up          - Levantar PostgreSQL y Redis (Docker)"
	@echo "  make dev-down        - Apagar servicios de desarrollo"
	@echo "  make dev-backend     - Ejecutar backend (nativo)"
	@echo "  make dev-celery      - Ejecutar Celery worker (nativo)"
	@echo "  make dev-frontend    - Ejecutar frontend (nativo)"
	@echo ""
	@echo "🚀 PRODUCCIÓN:"
	@echo "  make prod-build      - Construir imágenes Docker"
	@echo "  make prod-up         - Levantar todos los servicios"
	@echo "  make prod-down       - Apagar todos los servicios"
	@echo "  make prod-logs       - Ver logs en tiempo real"
	@echo ""
	@echo "🧪 TESTING:"
	@echo "  make test-local      - Ejecutar tests localmente"
	@echo ""
	@echo "🛠️ UTILIDADES:"
	@echo "  make shell-db        - Abrir shell de PostgreSQL"
	@echo "  make clean           - Limpiar volúmenes y caché"

# ============================================
# DESARROLLO LOCAL
# ============================================
dev-up:
	@echo "🐳 Levantando PostgreSQL y Redis..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Servicios levantados en:"
	@echo "   PostgreSQL: localhost:5432"
	@echo "   Redis: localhost:6379"

dev-down:
	@echo "🛑 Apagando servicios..."
	docker-compose -f docker-compose.dev.yml down

dev-backend:
	@echo "🐍 Iniciando backend en http://localhost:8000"
	@echo "📖 API Docs: http://localhost:8000/docs"
	@./scripts/dev-backend.sh

dev-celery:
	@echo "⚙️ Iniciando Celery worker..."
	cd backend && source venv/bin/activate && celery -A app.tasks.celery_app worker --loglevel=info

dev-frontend:
	@echo "⚛️ Iniciando frontend en http://localhost:3000"
	cd frontend && npm run dev

# ============================================
# PRODUCCIÓN
# ============================================
prod-build:
	@echo "🏗️ Construyendo imágenes Docker..."
	docker-compose -f docker-compose.prod.yml build

prod-up:
	@echo "🚀 Levantando servicios de producción..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Servicios activos:"
	@echo "   Backend: http://localhost:8000"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Flower: http://localhost:5555"
	@echo "   Nginx: http://localhost"

prod-down:
	@echo "🛑 Apagando servicios de producción..."
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	@echo "📋 Logs en tiempo real (Ctrl+C para salir)..."
	docker-compose -f docker-compose.prod.yml logs -f

# ============================================
# TESTING
# ============================================
test-local:
	@echo "🧪 Ejecutando tests..."
	cd backend && source venv/bin/activate && pytest -v

# ============================================
# UTILIDADES
# ============================================
shell-db:
	@echo "🐘 Abriendo shell de PostgreSQL..."
	docker-compose -f docker-compose.dev.yml exec postgres psql -U admin -d importapp_db

clean:
	@echo "🧹 Limpiando volúmenes y caché..."
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.prod.yml down -v
	@echo "✅ Limpieza completada"

# ============================================
# INSTALACIÓN INICIAL
# ============================================
install-backend:
	@echo "📦 Instalando dependencias de backend..."
	cd backend && python3.11 -m venv venv
	cd backend && source venv/bin/activate && pip install -r requirements.txt
	cd backend && source venv/bin/activate && playwright install chromium
	@echo "✅ Backend instalado"

install-frontend:
	@echo "📦 Instalando dependencias de frontend..."
	cd frontend && npm install
	@echo "✅ Frontend instalado"

install: install-backend install-frontend
	@echo "🎉 Instalación completa"
