#!/bin/bash

# Script directo para ver logs en vivo de la importación
# Uso: ./scripts/watch-import.sh

# Configuración
SERVER="root@45.14.194.85"
PASS="AGp231512"

echo "🔥 Monitoreando logs de importación en vivo..."
echo "💡 Ahora ve a https://syncar.cl/importers e inicia una importación"
echo "----------------------------------------"
echo ""

# Ver logs del backend y celery worker combinados
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $SERVER "cd /root/syncar && docker-compose -f docker-compose.prod.yml logs -f --tail=100 backend celery-worker"
