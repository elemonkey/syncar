#!/bin/bash

# ===== SCRIPT DE BACKUP PARA SYNCAR 2.0 =====
# Este script crea un backup completo de la base de datos

set -e

echo "📦 Iniciando backup de SYNCAR 2.0..."

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuración
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/syncar_backup_${TIMESTAMP}.sql"
BACKUP_COMPRESSED="${BACKUP_FILE}.gz"

# Crear directorio de backups
mkdir -p "$BACKUP_DIR"

# Verificar que el contenedor está corriendo
if ! docker ps | grep -q importapp-postgres; then
    echo "❌ Error: El contenedor de PostgreSQL no está corriendo"
    exit 1
fi

# Crear backup
echo -e "${YELLOW}📦 Creando backup...${NC}"
docker exec importapp-postgres pg_dump -U syncar_user syncar_prod > "$BACKUP_FILE"

# Comprimir backup
echo -e "${YELLOW}🗜️  Comprimiendo backup...${NC}"
gzip "$BACKUP_FILE"

# Información del backup
SIZE=$(du -h "$BACKUP_COMPRESSED" | cut -f1)
echo -e "${GREEN}✅ Backup completado!${NC}"
echo "📁 Archivo: $BACKUP_COMPRESSED"
echo "📊 Tamaño: $SIZE"

# Limpiar backups antiguos (mantener últimos 30 días)
echo -e "${YELLOW}🧹 Limpiando backups antiguos...${NC}"
find "$BACKUP_DIR" -name "syncar_backup_*.sql.gz" -mtime +30 -delete
echo -e "${GREEN}✅ Backups antiguos eliminados${NC}"

# Listar backups disponibles
echo ""
echo "📋 Backups disponibles:"
ls -lh "$BACKUP_DIR"/syncar_backup_*.sql.gz | tail -5
