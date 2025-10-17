#!/bin/bash

# Script para configurar SSL con Let's Encrypt
# Autor: GitHub Copilot
# Fecha: 16 de octubre de 2025

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Configuración SSL para syncar.cl ===${NC}\n"

# Variables
DOMAIN="syncar.cl"
WWW_DOMAIN="www.syncar.cl"
EMAIL="admin@syncar.cl"

echo -e "${YELLOW}📋 Información:${NC}"
echo "  - Dominio: $DOMAIN"
echo "  - Dominio WWW: $WWW_DOMAIN"
echo "  - Email: $EMAIL"
echo ""

# Paso 1: Detener nginx temporalmente para que certbot pueda usar el puerto 80
echo -e "${YELLOW}1. Deteniendo nginx temporalmente...${NC}"
docker-compose -f docker-compose.prod.yml stop nginx

# Paso 2: Obtener certificado SSL
echo -e "${YELLOW}2. Obteniendo certificado SSL de Let's Encrypt...${NC}"
certbot certonly \
  --standalone \
  --preferred-challenges http \
  --non-interactive \
  --agree-tos \
  --email "$EMAIL" \
  -d "$DOMAIN" \
  -d "$WWW_DOMAIN" \
  --keep-until-expiring

# Paso 3: Copiar certificados a la carpeta SSL
echo -e "${YELLOW}3. Copiando certificados...${NC}"
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/

# Paso 4: Reiniciar nginx
echo -e "${YELLOW}4. Reiniciando nginx con SSL...${NC}"
docker-compose -f docker-compose.prod.yml up -d nginx

# Paso 5: Verificar SSL
echo -e "${YELLOW}5. Verificando configuración SSL...${NC}"
sleep 3
if curl -sI https://$DOMAIN | head -1 | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ SSL configurado correctamente${NC}"
    echo -e "Puedes acceder a: ${GREEN}https://$DOMAIN${NC}"
else
    echo -e "${RED}❌ Error al verificar SSL${NC}"
    exit 1
fi

# Información sobre renovación
echo ""
echo -e "${GREEN}=== Configuración Completada ===${NC}\n"
echo -e "${YELLOW}📝 Notas importantes:${NC}"
echo "  - Los certificados se renuevan automáticamente"
echo "  - Puedes forzar renovación con: certbot renew --force-renewal"
echo "  - Los certificados expiran en 90 días"
echo "  - Certbot renovará automáticamente si está configurado el cron"
echo ""
echo -e "${YELLOW}🔄 Para configurar renovación automática, agrega a crontab:${NC}"
echo "  0 0,12 * * * certbot renew --quiet --deploy-hook 'cd /root/syncar && docker-compose -f docker-compose.prod.yml restart nginx'"
echo ""
