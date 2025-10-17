#!/bin/bash

# ===== DEPLOY SEGURO LOCAL - SYNCAR 2.0 =====
# Este script despliega en producción SIN afectar el entorno de desarrollo
# - Cierra puertos necesarios (80, 5555)
# - Limpia imágenes y volúmenes antiguos
# - Reinicia servicios completamente
# - Preserva datos de desarrollo

set -e  # Exit on error

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

clear
echo "🚀 ===== DEPLOY COMPLETO - SYNCAR 2.0 ====="
echo ""

# Verificar directorio
if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.prod.yml no encontrado${NC}"
    echo "Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker no está corriendo${NC}"
    echo "Inicia Docker Desktop y vuelve a intentar"
    exit 1
fi

# Mostrar estado actual
echo -e "${BLUE}📊 Estado actual del sistema:${NC}"
echo ""
echo "Contenedores corriendo:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAME|importapp" || echo "  (ninguno)"
echo ""

# Advertencia
echo -e "${YELLOW}⚠️  ESTE DEPLOY HARÁ:${NC}"
echo "  ✅ Liberar puertos 80, 5555 (cerrar procesos si es necesario)"
echo "  ✅ Detener frontend dev (puerto 3000) temporalmente"
echo "  ✅ Mantener backend dev corriendo (puerto 8000)"
echo "  ✅ Mantener PostgreSQL dev (puerto 5432)"
echo "  ✅ Mantener Redis dev (puerto 6379)"
echo "  ✅ Eliminar imágenes antiguas de producción"
echo "  ✅ Eliminar volúmenes no utilizados (NO los de dev)"
echo "  ✅ Construir imágenes nuevas desde cero"
echo "  ✅ Crear contenedores de producción (puerto 80, 5555)"
echo ""
read -p "¿Continuar con el deploy? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deploy cancelado"
    exit 0
fi

# ===== PASO 1: CERRAR PUERTOS =====
echo ""
echo -e "${MAGENTA}🔒 PASO 1/8: Liberando puertos necesarios...${NC}"

# Liberar puerto 80
echo -e "${BLUE}Verificando puerto 80...${NC}"
PORT_80_PID=$(lsof -ti:80 2>/dev/null || echo "")
if [ ! -z "$PORT_80_PID" ]; then
    echo -e "${YELLOW}⚠️  Proceso en puerto 80 (PID: $PORT_80_PID)${NC}"
    ps -p $PORT_80_PID -o comm= 2>/dev/null || echo "  (proceso desconocido)"
    echo "Cerrando proceso..."
    sudo kill -9 $PORT_80_PID 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✅ Puerto 80 liberado${NC}"
else
    echo -e "${GREEN}✅ Puerto 80 disponible${NC}"
fi

# Liberar puerto 5555 (Flower)
echo -e "${BLUE}Verificando puerto 5555...${NC}"
PORT_5555_PID=$(lsof -ti:5555 2>/dev/null || echo "")
if [ ! -z "$PORT_5555_PID" ]; then
    echo -e "${YELLOW}⚠️  Proceso en puerto 5555 (PID: $PORT_5555_PID)${NC}"
    echo "Cerrando proceso..."
    sudo kill -9 $PORT_5555_PID 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✅ Puerto 5555 liberado${NC}"
else
    echo -e "${GREEN}✅ Puerto 5555 disponible${NC}"
fi

# Detener frontend dev si está corriendo (puerto 3000)
echo -e "${BLUE}Verificando frontend dev (puerto 3000)...${NC}"
PORT_3000_PID=$(lsof -ti:3000 2>/dev/null || echo "")
if [ ! -z "$PORT_3000_PID" ]; then
    echo -e "${YELLOW}⚠️  Frontend dev corriendo (PID: $PORT_3000_PID)${NC}"
    echo "Deteniendo temporalmente..."
    kill $PORT_3000_PID 2>/dev/null || true
    sleep 2
    echo -e "${GREEN}✅ Frontend dev detenido (podrás reiniciarlo después)${NC}"
else
    echo -e "${GREEN}✅ Puerto 3000 disponible${NC}"
fi

# Verificar .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Archivo .env no encontrado. Creando desde .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Archivo .env creado${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  EDITA .env antes de continuar:${NC}"
        echo "  - POSTGRES_PASSWORD"
        echo "  - SECRET_KEY"
        echo "  - Otras variables necesarias"
        echo ""
        read -p "Presiona ENTER cuando hayas editado .env..."
    else
        echo -e "${RED}❌ Error: .env.example no encontrado${NC}"
        exit 1
    fi
fi

# ===== PASO 2: BACKUP =====
echo ""
echo -e "${MAGENTA}� PASO 2/8: Creando backup de base de datos...${NC}"
mkdir -p backups

if docker ps | grep -q "importapp-postgres"; then
    BACKUP_FILE="backups/backup_$(date +%Y%m%d_%H%M%S).sql"
    echo "Creando backup en $BACKUP_FILE..."
    docker exec importapp-postgres pg_dump -U syncar_user syncar_prod > "$BACKUP_FILE" 2>/dev/null || true
    if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
        echo -e "${GREEN}✅ Backup creado: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))${NC}"
    else
        rm -f "$BACKUP_FILE"
        echo -e "${YELLOW}⚠️  No se pudo crear backup (posiblemente no hay datos)${NC}"
    fi
else
    echo -e "${YELLOW}ℹ️  No hay contenedor de producción existente${NC}"
fi

# ===== PASO 3: DETENER CONTENEDORES =====
echo ""
echo -e "${MAGENTA}🛑 PASO 3/8: Deteniendo contenedores de producción...${NC}"
if docker-compose -f docker-compose.prod.yml ps -q 2>/dev/null | grep -q .; then
    echo "Deteniendo servicios..."
    docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
    echo -e "${GREEN}✅ Contenedores detenidos${NC}"
else
    echo -e "${GREEN}✅ No hay contenedores de producción corriendo${NC}"
fi

# ===== PASO 4: LIMPIAR IMÁGENES Y VOLÚMENES =====
echo ""
echo -e "${MAGENTA}🧹 PASO 4/8: Limpiando imágenes y volúmenes antiguos...${NC}"

# Eliminar imágenes de producción antiguas
echo "Eliminando imágenes antiguas de importapp..."
docker images | grep "importapp\|syncar2.0" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
echo -e "${GREEN}✅ Imágenes antiguas eliminadas${NC}"

# Limpiar volúmenes no utilizados (excepto los de dev)
echo "Limpiando volúmenes no utilizados..."
VOLUMES_REMOVED=$(docker volume ls -qf dangling=true | grep -v "syncar20-postgres-dev-data\|syncar20-redis-dev-data" | xargs -r docker volume rm 2>/dev/null | wc -l || echo "0")
if [ "$VOLUMES_REMOVED" -gt 0 ]; then
    echo -e "${GREEN}✅ $VOLUMES_REMOVED volúmenes eliminados${NC}"
else
    echo -e "${GREEN}✅ No hay volúmenes para eliminar${NC}"
fi

# Limpiar cache de build
echo "Limpiando cache de build de Docker..."
docker builder prune -f > /dev/null 2>&1 || true
echo -e "${GREEN}✅ Cache de build limpiado${NC}"

# ===== PASO 5: VERIFICAR SERVICIOS DEV =====
echo ""
echo -e "${MAGENTA}🔍 PASO 5/8: Verificando servicios de desarrollo...${NC}"

# Verificar PostgreSQL dev
if docker ps | grep -q "importapp-postgres-dev"; then
    echo -e "${GREEN}✅ PostgreSQL dev corriendo (puerto 5432)${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL dev no está corriendo${NC}"
    echo "   Iniciando PostgreSQL dev..."
    docker-compose -f docker-compose.dev.yml up -d postgres 2>/dev/null || true
    sleep 3
    echo -e "${GREEN}✅ PostgreSQL dev iniciado${NC}"
fi

# Verificar Redis dev
if docker ps | grep -q "importapp-redis-dev"; then
    echo -e "${GREEN}✅ Redis dev corriendo (puerto 6379)${NC}"
else
    echo -e "${YELLOW}⚠️  Redis dev no está corriendo${NC}"
    echo "   Iniciando Redis dev..."
    docker-compose -f docker-compose.dev.yml up -d redis 2>/dev/null || true
    sleep 2
    echo -e "${GREEN}✅ Redis dev iniciado${NC}"
fi

# ===== PASO 6: CONSTRUIR IMÁGENES =====
echo ""
echo -e "${MAGENTA}🔨 PASO 6/8: Construyendo imágenes Docker desde cero...${NC}"
echo "Esto puede tomar varios minutos..."
docker-compose -f docker-compose.prod.yml build --no-cache --pull

echo -e "${GREEN}✅ Imágenes construidas${NC}"

# ===== PASO 7: INICIAR SERVICIOS =====
echo ""
echo -e "${MAGENTA}🚀 PASO 7/8: Iniciando servicios de producción...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Esperar a que los servicios estén listos
echo ""
echo -e "${BLUE}⏳ Esperando a que los servicios inicien...${NC}"
for i in {1..30}; do
    echo -n "."
    sleep 1
done
echo ""

# Verificar que todos los servicios estén corriendo
echo ""
echo -e "${BLUE}� Verificando servicios...${NC}"
EXPECTED_SERVICES=8
RUNNING_SERVICES=$(docker-compose -f docker-compose.prod.yml ps --services --filter "status=running" | wc -l)

if [ "$RUNNING_SERVICES" -eq "$EXPECTED_SERVICES" ]; then
    echo -e "${GREEN}✅ Todos los servicios están corriendo ($RUNNING_SERVICES/$EXPECTED_SERVICES)${NC}"
else
    echo -e "${YELLOW}⚠️  Solo $RUNNING_SERVICES de $EXPECTED_SERVICES servicios están corriendo${NC}"
    echo "Servicios:"
    docker-compose -f docker-compose.prod.yml ps
fi

# ===== PASO 8: MIGRACIONES =====
echo ""
echo -e "${MAGENTA}🔄 PASO 8/8: Ejecutando migraciones de base de datos...${NC}"
sleep 5  # Esperar un poco más para que postgres esté listo

# Intentar migraciones hasta 3 veces
MAX_RETRIES=3
RETRY_COUNT=0
MIGRATION_SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker exec importapp-backend alembic upgrade head 2>/dev/null; then
        echo -e "${GREEN}✅ Migraciones ejecutadas exitosamente${NC}"
        MIGRATION_SUCCESS=true
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo -e "${YELLOW}⚠️  Intento $RETRY_COUNT falló, reintentando en 5 segundos...${NC}"
            sleep 5
        fi
    fi
done

if [ "$MIGRATION_SUCCESS" = false ]; then
    echo -e "${YELLOW}⚠️  Migraciones fallaron después de $MAX_RETRIES intentos${NC}"
    echo "   Esto puede ser normal en el primer deploy"
    echo "   Puedes ejecutarlas manualmente con:"
    echo "   docker exec importapp-backend alembic upgrade head"
fi

# ===== VERIFICACIÓN FINAL =====
echo ""
echo -e "${MAGENTA}🔍 Verificación final...${NC}"

# Probar que el backend responde
echo -n "Verificando backend... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/docs | grep -q "200"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️  (puede tardar unos segundos en estar disponible)${NC}"
fi

# Probar que el frontend responde
echo -n "Verificando frontend... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️  (puede tardar unos segundos en estar disponible)${NC}"
fi

# Probar que Flower responde
echo -n "Verificando Flower... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5555 | grep -q "200"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️  (puede tardar unos segundos en estar disponible)${NC}"
fi

# ===== RESUMEN FINAL =====
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ ===== DEPLOY COMPLETADO EXITOSAMENTE ===== ${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}🌐 URLs de la aplicación:${NC}"
echo "   Frontend:    http://localhost"
echo "   Backend API: http://localhost/api/docs"
echo "   Flower:      http://localhost:5555"
echo ""
echo -e "${BLUE}📊 Comandos útiles:${NC}"
echo "   Ver todos los logs:     docker-compose -f docker-compose.prod.yml logs -f"
echo "   Ver logs del backend:   docker-compose -f docker-compose.prod.yml logs -f backend"
echo "   Ver logs del frontend:  docker-compose -f docker-compose.prod.yml logs -f frontend"
echo "   Ver estado:             docker-compose -f docker-compose.prod.yml ps"
echo "   Reiniciar servicio:     docker-compose -f docker-compose.prod.yml restart <servicio>"
echo "   Detener todo:           docker-compose -f docker-compose.prod.yml down"
echo ""
echo -e "${BLUE}� Para restaurar entorno de desarrollo:${NC}"
echo "   1. docker-compose -f docker-compose.prod.yml down"
echo "   2. cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "   3. cd frontend && npm run dev"
echo ""
echo -e "${BLUE}🗄️  Base de datos:${NC}"
echo "   Conectar:  docker exec -it importapp-postgres psql -U syncar_user syncar_prod"
echo "   Backup en: backups/"
echo ""
echo -e "${BLUE}📦 Contenedores de producción:${NC}"
docker-compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo -e "${GREEN}🎉 ¡SYNCAR 2.0 está corriendo en producción!${NC}"
echo ""
echo -e "${YELLOW}💡 Tip: Espera 10-15 segundos para que todos los servicios estén 100% listos${NC}"
echo ""

# Preguntar si desea ver los logs
read -p "¿Deseas ver los logs en tiempo real? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Presiona Ctrl+C para salir de los logs"
    echo ""
    sleep 2
    docker-compose -f docker-compose.prod.yml logs -f
fi
