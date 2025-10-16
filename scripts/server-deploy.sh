#!/bin/bash
# COMANDOS PARA COPIAR Y PEGAR EN EL SERVIDOR
# Ejecuta estos comandos uno por uno

echo "🚀 SYNCAR 2.0 - Deploy Automatizado"
echo "===================================="
echo ""

# PASO 1: Instalar Docker (si no está instalado)
echo "📦 Paso 1: Instalando Docker..."
curl -fsSL https://get.docker.com | sh
apt install -y git docker-compose-plugin certbot python3-certbot-nginx

# PASO 2: Descomprimir proyecto
echo "📂 Paso 2: Descomprimiendo proyecto..."
cd /opt
tar -xzf syncar2.0-deploy.tar.gz

# Renombrar si es necesario
if [ -d "SYNCAR2.0" ]; then
    mv SYNCAR2.0 syncar
fi

cd syncar

# PASO 3: Configurar
echo "⚙️  Paso 3: Configurando..."
cp .env.production .env
chmod +x scripts/*.sh

# PASO 4: Deploy
echo "🚀 Paso 4: Ejecutando deploy..."
./scripts/deploy.sh

# PASO 5: Configurar SSL
echo "🔒 Paso 5: Configurando SSL..."
certbot --nginx -d syncar.cl -d www.syncar.cl --non-interactive --agree-tos --email admin@syncar.cl

# PASO 6: Verificación
echo ""
echo "✅ Deploy completado!"
echo ""
echo "Verificando servicios..."
docker compose -f docker-compose.prod.yml ps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 SYNCAR 2.0 está en producción!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Accede a tu aplicación:"
echo "   https://syncar.cl"
echo "   https://syncar.cl/importers"
echo ""
echo "📊 Monitoreo:"
echo "   https://syncar.cl:5555 (Flower - Celery)"
echo ""
echo "📝 Ver logs:"
echo "   docker compose -f docker-compose.prod.yml logs -f"
echo ""
