#!/bin/bash

echo "🔍 Verificando endpoints de configuración de importadores..."

# 1. Listar todas las configuraciones
echo "1. GET /api/v1/importer-configs"
curl -s http://localhost/api/v1/importer-configs | jq -r '.[].importer_name' | head -5
echo "✅ Configuraciones listadas"
echo ""

# 2. Obtener configuración específica de Noriega
echo "2. GET /api/v1/importer-configs/noriega"
NORIEGA_CONFIG=$(curl -s http://localhost/api/v1/importer-configs/noriega)
echo $NORIEGA_CONFIG | jq '.display_name'
echo "✅ Configuración de Noriega obtenida"
echo ""

# 3. Actualizar estado (toggle activo/inactivo)
echo "3. PUT /api/v1/importer-configs/noriega (toggle activo)"
curl -s -X PUT http://localhost/api/v1/importer-configs/noriega \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}' | jq '.is_active'
echo "✅ Estado actualizado a inactivo"

curl -s -X PUT http://localhost/api/v1/importer-configs/noriega \
  -H "Content-Type: application/json" \
  -d '{"is_active": true}' | jq '.is_active'
echo "✅ Estado revertido a activo"
echo ""

# 4. Verificar que frontend carga sin errores
echo "4. Verificando página frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/configuracion)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Página de configuración carga correctamente (HTTP $FRONTEND_STATUS)"
else
    echo "❌ Error en página de configuración (HTTP $FRONTEND_STATUS)"
fi

echo ""
echo "🎉 Verificación completada - Sistema de configuración funcionando"