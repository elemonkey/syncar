#!/bin/bash

# Script para preparar el paquete de deploy para el servidor
# Ejecuta este script desde tu Mac para crear el archivo a subir

echo "🚀 Preparando paquete de deploy para SYNCAR 2.0"
echo "==============================================="
echo ""

# Directorio actual
PROJECT_DIR="/Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0"
cd "$PROJECT_DIR"

echo "📦 Creando archivo comprimido..."
echo ""

# Crear archivo tar.gz excluyendo archivos innecesarios
tar --exclude='frontend/node_modules' \
    --exclude='frontend/.next' \
    --exclude='backend/venv' \
    --exclude='backend/__pycache__' \
    --exclude='backend/app/__pycache__' \
    --exclude='backend/app/*/__pycache__' \
    --exclude='backend/app/*/*/__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='backups/*.sql' \
    --exclude='.DS_Store' \
    --exclude='.env.dev.backup' \
    -czf ../syncar2.0-deploy.tar.gz .

echo "✅ Paquete creado: /Users/maxberrios/Desktop/REPUESTOS/syncar2.0-deploy.tar.gz"
echo ""
echo "📊 Tamaño del archivo:"
ls -lh ../syncar2.0-deploy.tar.gz
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📤 SIGUIENTE PASO: Subir al servidor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Ejecuta este comando para subir al servidor:"
echo ""
echo "scp /Users/maxberrios/Desktop/REPUESTOS/syncar2.0-deploy.tar.gz root@45.14.194.85:/opt/"
echo ""
echo "Luego, en el servidor, ejecuta:"
echo ""
echo "ssh root@45.14.194.85"
echo "cd /opt"
echo "tar -xzf syncar2.0-deploy.tar.gz"
echo "mv SYNCAR2.0 syncar  # (si es necesario)"
echo "cd syncar"
echo "cp .env.production .env"
echo "chmod +x scripts/*.sh"
echo "./scripts/deploy.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 Para más detalles, revisa: docs/DEPLOY_SERVIDOR.md"
echo ""
