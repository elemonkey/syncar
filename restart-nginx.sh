#!/bin/bash

echo "🔄 Aplicando nueva configuración de nginx..."

cd /www/wwwroot/syncar.cl

echo "📋 Estado actual de contenedores:"
docker ps

echo ""
echo "🔄 Reiniciando nginx con nueva configuración..."
docker-compose restart nginx

echo ""
echo "⏳ Esperando nginx..."
sleep 10

echo ""
echo "📋 Logs de nginx:"
docker logs syncar-nginx-1 --tail 10

echo ""
echo "🔍 Verificando conectividad:"

echo "Backend directo (puerto 8000):"
curl -s http://localhost:8000/api/v1/health && echo " ✅ Backend OK" || echo " ❌ Backend Error"

echo ""
echo "Frontend via nginx (puerto 80):"
curl -s http://localhost/ >/dev/null && echo " ✅ Nginx OK" || echo " ❌ Nginx Error"

echo ""
echo "Acceso externo por IP:"
curl -s http://45.14.194.85/ >/dev/null && echo " ✅ Acceso externo OK" || echo " ❌ Acceso externo Error"

echo ""
echo "🎯 Estado final:"
docker ps | grep nginx

echo ""
echo "🎉 Configuración aplicada!"
echo "📍 Acceso: http://45.14.194.85"
echo "📊 API: http://45.14.194.85/api/v1/health"