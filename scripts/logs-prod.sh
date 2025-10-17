#!/bin/bash

# ===== MONITOREO DE LOGS EN PRODUCCIÓN REMOTA =====
# Script para ver logs del servidor de producción desde tu Mac

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuración (EDITA ESTOS VALORES)
SERVER_USER="tu_usuario"
SERVER_HOST="tu-servidor.com"  # o IP: 123.45.67.89
PROJECT_PATH="/home/tu_usuario/syncar"

echo -e "${BLUE}📡 Monitoreo de Logs - SYNCAR 2.0 Producción${NC}"
echo ""
echo "Servidor: $SERVER_USER@$SERVER_HOST"
echo "Ruta: $PROJECT_PATH"
echo ""

# Menú
echo "Selecciona qué logs ver:"
echo "  1) Todos los servicios"
echo "  2) Backend"
echo "  3) Celery Worker (importaciones)"
echo "  4) Frontend"
echo "  5) Nginx"
echo "  6) PostgreSQL"
echo "  7) Estado de servicios"
echo "  8) Últimas 50 líneas del backend"
echo ""
read -p "Opción (1-8): " option

case $option in
  1)
    echo -e "${GREEN}Conectando a logs de todos los servicios...${NC}"
    ssh -t $SERVER_USER@$SERVER_HOST "cd $PROJECT_PATH && docker-compose -f docker-compose.prod.yml logs -f"
    ;;
  2)
    echo -e "${GREEN}Conectando a logs del backend...${NC}"
    ssh -t $SERVER_USER@$SERVER_HOST "cd $PROJECT_PATH && docker-compose -f docker-compose.prod.yml logs -f backend"
    ;;
  3)
    echo -e "${GREEN}Conectando a logs del worker...${NC}"
    ssh -t $SERVER_USER@$SERVER_HOST "cd $PROJECT_PATH && docker-compose -f docker-compose.prod.yml logs -f celery-worker"
    ;;
  4)
    echo -e "${GREEN}Conectando a logs del frontend...${NC}"
    ssh -t $SERVER_USER@$SERVER_HOST "cd $PROJECT_PATH && docker-compose -f docker-compose.prod.yml logs -f frontend"
    ;;
  5)
    echo -e "${GREEN}Conectando a logs de nginx...${NC}"
    ssh -t $SERVER_USER@$SERVER_HOST "cd $PROJECT_PATH && docker-compose -f docker-compose.prod.yml logs -f nginx"
    ;;
  6)
    echo -e "${GREEN}Conectando a logs de PostgreSQL...${NC}"
    ssh -t $SERVER_USER@$SERVER_HOST "cd $PROJECT_PATH && docker-compose -f docker-compose.prod.yml logs -f postgres"
    ;;
  7)
    echo -e "${GREEN}Estado de servicios...${NC}"
    ssh -t $SERVER_USER@$SERVER_HOST "cd $PROJECT_PATH && docker-compose -f docker-compose.prod.yml ps"
    ;;
  8)
    echo -e "${GREEN}Últimas 50 líneas del backend...${NC}"
    ssh -t $SERVER_USER@$SERVER_HOST "cd $PROJECT_PATH && docker-compose -f docker-compose.prod.yml logs --tail=50 backend"
    ;;
  *)
    echo -e "${YELLOW}Opción inválida${NC}"
    exit 1
    ;;
esac
