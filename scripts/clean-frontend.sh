#!/bin/bash

# Script para limpiar el caché de Next.js y reiniciar el servidor
# Útil cuando se encuentran errores ENOENT o problemas de compilación

echo "🧹 Limpiando caché de Next.js..."

# Ir al directorio del frontend
cd "$(dirname "$0")/../frontend" || exit 1

# Matar procesos en puerto 3000
echo "🔪 Matando procesos en puerto 3000..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || echo "   No hay procesos corriendo en el puerto 3000"

# Eliminar caché de Next.js
echo "🗑️  Eliminando carpeta .next..."
rm -rf .next

echo ""
echo "✅ Caché limpiado exitosamente"
echo ""
echo "🚀 Iniciando servidor de desarrollo..."
echo ""

# Iniciar servidor
npm run dev
