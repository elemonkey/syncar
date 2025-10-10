#!/bin/bash

echo "🔍 Verificador de DNS para SYNCAR"
echo "================================"

echo "🌐 Verificando resolución DNS de syncar.cl..."
SYNCAR_IP=$(nslookup syncar.cl | grep -A1 "Name:" | grep "Address:" | awk '{print $2}' | head -n1)

echo "🌐 Verificando resolución DNS de www.syncar.cl..."
WWW_IP=$(nslookup www.syncar.cl | grep -A1 "Name:" | grep "Address:" | awk '{print $2}' | head -n1)

echo ""
echo "📋 Resultados:"
echo "syncar.cl → $SYNCAR_IP"
echo "www.syncar.cl → $WWW_IP"
echo "IP objetivo → 45.14.194.85"

echo ""
if [ "$SYNCAR_IP" = "45.14.194.85" ] && [ "$WWW_IP" = "45.14.194.85" ]; then
    echo "✅ DNS configurado correctamente"
    echo "🚀 Puedes proceder con la configuración SSL"
    echo ""
    echo "Para configurar SSL, ejecuta en el servidor:"
    echo "curl -fsSL https://raw.githubusercontent.com/elemonkey/syncar/main/setup-ssl.sh | bash"
elif [ "$SYNCAR_IP" = "45.14.194.85" ] || [ "$WWW_IP" = "45.14.194.85" ]; then
    echo "⚠️ DNS parcialmente configurado"
    echo "Configura ambos registros y espera la propagación"
else
    echo "❌ DNS no configurado"
    echo ""
    echo "📋 Configuración necesaria en tu proveedor DNS:"
    echo "Registro 1:"
    echo "  Tipo: A"
    echo "  Nombre: @ (o syncar.cl)"
    echo "  Valor: 45.14.194.85"
    echo "  TTL: 300"
    echo ""
    echo "Registro 2:"
    echo "  Tipo: A"
    echo "  Nombre: www"
    echo "  Valor: 45.14.194.85"
    echo "  TTL: 300"
fi

echo ""
echo "🕐 La propagación DNS puede tomar 5-15 minutos"