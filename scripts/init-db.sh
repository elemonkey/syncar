#!/bin/bash

# Script para inicializar la base de datos en producción

echo "🔄 Actualizando código desde GitHub..."
git pull origin main

echo ""
echo "🌱 Ejecutando seed de base de datos..."
docker exec importapp-backend python -m app.scripts.seed_db

echo ""
echo "✅ Verificando datos..."
docker exec importapp-postgres psql -U elemonkey -d syncar_db -c "SELECT code, name, is_active FROM importers;"

echo ""
echo "🎉 Inicialización completada"
