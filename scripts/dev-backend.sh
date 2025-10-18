#!/bin/bash
# Script para iniciar el backend con limpieza de procesos al reiniciar

# Función para limpiar procesos de Playwright al salir
cleanup() {
    echo "🧹 Limpiando procesos de Playwright..."
    pkill -f "chromium" 2>/dev/null || true
    pkill -f "playwright" 2>/dev/null || true
    echo "✅ Limpieza completada"
}

# Registrar función de limpieza para SIGTERM y SIGINT
trap cleanup EXIT SIGTERM SIGINT

# Iniciar uvicorn
echo "🚀 Iniciando backend con auto-limpieza..."
cd backend && source venv/bin/activate && \
    uvicorn app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --timeout-graceful-shutdown 3 \
    --reload-exclude 'app/tasks/*' \
    --reload-exclude 'app/importers/*'
