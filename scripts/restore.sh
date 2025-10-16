#!/bin/bash

# ===== SCRIPT DE RESTAURACIÓN PARA SYNCAR 2.0 =====
# Este script restaura un backup de la base de datos

set -e

echo "🔄 Script de restauración de SYNCAR 2.0"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar argumento
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Debes especificar el archivo de backup${NC}"
    echo "Uso: ./restore.sh <archivo_backup.sql.gz>"
    echo ""
    echo "Backups disponibles:"
    ls -lh backups/syncar_backup_*.sql.gz 2>/dev/null || echo "  No hay backups disponibles"
    exit 1
fi

BACKUP_FILE="$1"

# Verificar que el archivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ Error: El archivo $BACKUP_FILE no existe${NC}"
    exit 1
fi

# Verificar que el contenedor está corriendo
if ! docker ps | grep -q importapp-postgres; then
    echo -e "${RED}❌ Error: El contenedor de PostgreSQL no está corriendo${NC}"
    exit 1
fi

# Advertencia
echo -e "${YELLOW}⚠️  ADVERTENCIA: Esta operación eliminará todos los datos actuales${NC}"
read -p "¿Estás seguro de que deseas continuar? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^yes$ ]]; then
    echo "Operación cancelada"
    exit 0
fi

# Descomprimir si es necesario
TEMP_FILE="$BACKUP_FILE"
if [[ $BACKUP_FILE == *.gz ]]; then
    echo -e "${YELLOW}📂 Descomprimiendo backup...${NC}"
    TEMP_FILE="${BACKUP_FILE%.gz}"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
fi

# Restaurar backup
echo -e "${YELLOW}🔄 Restaurando backup...${NC}"

# Detener aplicación para evitar conexiones
echo "  1. Deteniendo aplicación..."
docker-compose -f docker-compose.prod.yml stop backend celery-worker celery-beat

# Eliminar base de datos actual y crear nueva
echo "  2. Recreando base de datos..."
docker exec importapp-postgres psql -U syncar_user -d postgres -c "DROP DATABASE IF EXISTS syncar_prod;"
docker exec importapp-postgres psql -U syncar_user -d postgres -c "CREATE DATABASE syncar_prod;"

# Restaurar datos
echo "  3. Restaurando datos..."
cat "$TEMP_FILE" | docker exec -i importapp-postgres psql -U syncar_user -d syncar_prod

# Limpiar archivo temporal
if [[ $BACKUP_FILE == *.gz ]]; then
    rm "$TEMP_FILE"
fi

# Reiniciar aplicación
echo "  4. Reiniciando aplicación..."
docker-compose -f docker-compose.prod.yml start backend celery-worker celery-beat

echo -e "${GREEN}✅ Restauración completada exitosamente!${NC}"
echo ""
echo "La aplicación debería estar disponible en unos segundos"
