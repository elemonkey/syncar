#!/bin/bash
set -e

echo "🚀 Desplegando cambios en producción..."

# Conectar y desplegar
sshpass -p 'AGp231512' ssh -o StrictHostKeyChecking=no root@45.14.194.85 << 'ENDSSH'
cd /root/syncar
echo "📥 Haciendo pull..."
git pull origin main

echo "🔨 Rebuilding backend..."
docker-compose -f docker-compose.prod.yml build backend

echo "🔨 Rebuilding frontend..."
docker-compose -f docker-compose.prod.yml build frontend

echo "🔄 Reiniciando servicios..."
docker-compose -f docker-compose.prod.yml up -d backend frontend

echo "✅ Deploy completado!"
docker-compose -f docker-compose.prod.yml ps | grep -E 'backend|frontend'
ENDSSH
