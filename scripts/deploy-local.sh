#!/bin/bash

# ===== SCRIPT DE DEPLOY LOCAL PARA TESTING =====
# Este script te permite probar el entorno de producción localmente

set -e

echo "🔧 Deploy LOCAL de SYNCAR 2.0 (testing)"
echo "========================================="

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar requisitos
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

# Crear .env si no existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creando archivo .env para testing...${NC}"
    cat > .env << EOF
# Variables para TESTING LOCAL
POSTGRES_DB=syncar_local
POSTGRES_USER=syncar_local
POSTGRES_PASSWORD=local_password_123
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

SECRET_KEY=local_secret_key_for_testing_only_not_secure
ENVIRONMENT=local
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

JWT_SECRET_KEY=local_jwt_secret_for_testing_only
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

NEXT_PUBLIC_API_URL=http://localhost/api/v1

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

LOG_LEVEL=DEBUG
EOF
    echo -e "${GREEN}✅ Archivo .env creado${NC}"
fi

# Limpiar contenedores anteriores
echo -e "${YELLOW}🧹 Limpiando contenedores anteriores...${NC}"
docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true

# Construir imágenes
echo -e "${YELLOW}🔨 Construyendo imágenes Docker...${NC}"
docker-compose -f docker-compose.prod.yml build

# Iniciar servicios
echo -e "${YELLOW}🚀 Iniciando servicios...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Esperar a que los servicios estén listos
echo -e "${YELLOW}⏳ Esperando a que los servicios inicien...${NC}"
sleep 15

# Ejecutar migraciones
echo -e "${YELLOW}🔄 Ejecutando migraciones...${NC}"
docker exec importapp-backend alembic upgrade head || echo "⚠️  Migraciones fallaron o no son necesarias"

# Verificar estado
echo -e "${BLUE}📊 Estado de los servicios:${NC}"
docker-compose -f docker-compose.prod.yml ps

# Información final
echo ""
echo -e "${GREEN}✅ Deploy local completado!${NC}"
echo ""
echo "🌐 Servicios disponibles:"
echo "   - Frontend:     http://localhost"
echo "   - Backend API:  http://localhost/api"
echo "   - API Docs:     http://localhost/api/docs"
echo "   - Flower:       http://localhost:5555"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs:       docker-compose -f docker-compose.prod.yml logs -f"
echo "   Detener:        docker-compose -f docker-compose.prod.yml down"
echo "   Reiniciar:      docker-compose -f docker-compose.prod.yml restart"
echo ""
echo -e "${YELLOW}⚠️  NOTA: Este es un entorno de TESTING, NO usar en producción${NC}"
