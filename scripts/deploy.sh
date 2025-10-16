#!/bin/bash

# ===== SCRIPT DE DEPLOY PARA SYNCAR 2.0 =====
# Este script despliega la aplicación en producción

set -e  # Exit on error

echo "🚀 Iniciando deploy de SYNCAR 2.0..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.prod.yml no encontrado${NC}"
    echo "Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

# Verificar que existe .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: archivo .env no encontrado${NC}"
    echo "Copia .env.production.example a .env y configura tus variables"
    exit 1
fi

# Hacer backup de la base de datos (si existe)
echo -e "${YELLOW}📦 Creando backup de la base de datos...${NC}"
if docker ps | grep -q importapp-postgres; then
    BACKUP_FILE="backups/backup_$(date +%Y%m%d_%H%M%S).sql"
    mkdir -p backups
    docker exec importapp-postgres pg_dump -U syncar_user syncar_prod > "$BACKUP_FILE"
    echo -e "${GREEN}✅ Backup creado: $BACKUP_FILE${NC}"
else
    echo -e "${YELLOW}⚠️  No hay base de datos existente para hacer backup${NC}"
fi

# Detener contenedores existentes
echo -e "${YELLOW}🛑 Deteniendo contenedores...${NC}"
docker-compose -f docker-compose.prod.yml down

# Limpiar imágenes antiguas (opcional)
read -p "¿Deseas limpiar imágenes Docker antiguas? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧹 Limpiando imágenes antiguas...${NC}"
    docker image prune -a -f
fi

# Construir imágenes
echo -e "${YELLOW}🔨 Construyendo imágenes Docker...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# Iniciar servicios
echo -e "${YELLOW}🚀 Iniciando servicios...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Esperar a que los servicios estén listos
echo -e "${YELLOW}⏳ Esperando a que los servicios inicien...${NC}"
sleep 10

# Verificar estado de los servicios
echo -e "${YELLOW}🔍 Verificando estado de los servicios...${NC}"
docker-compose -f docker-compose.prod.yml ps

# Ejecutar migraciones
echo -e "${YELLOW}🔄 Ejecutando migraciones de base de datos...${NC}"
docker exec importapp-backend alembic upgrade head

# Mostrar logs
echo -e "${GREEN}✅ Deploy completado!${NC}"
echo ""
echo "📊 Ver logs en tiempo real:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🌐 La aplicación debería estar disponible en:"
echo "   - Frontend: http://localhost (puerto 80)"
echo "   - Backend API: http://localhost/api"
echo "   - Flower (Celery): http://localhost:5555"
echo ""
echo "🛑 Para detener los servicios:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""
echo -e "${GREEN}🎉 ¡SYNCAR 2.0 está en producción!${NC}"
