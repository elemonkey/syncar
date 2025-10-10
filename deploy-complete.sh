#!/bin/bash
set -e

echo "🚀 DESPLEGANDO SYNCAR COMPLETO EN SERVIDOR LIMPIO..."

# 1. Actualizar sistema e instalar dependencias
echo "📦 Actualizando sistema..."
apt-get update
apt-get upgrade -y

echo "🔧 Instalando dependencias básicas..."
apt-get install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release ufw

# 2. Instalar Docker
echo "🐳 Instalando Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# 3. Instalar Docker Compose
echo "📋 Instalando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 4. Iniciar Docker
echo "▶️ Iniciando Docker..."
systemctl start docker
systemctl enable docker

# 5. Instalar Certbot
echo "🔒 Instalando Certbot..."
apt-get install -y certbot

# 6. Configurar firewall
echo "🛡️ Configurando firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 7. Crear directorios y clonar proyecto
echo "📁 Preparando proyecto..."
mkdir -p /www/wwwroot/syncar.cl
cd /www/wwwroot/syncar.cl
rm -rf * .[!.]* 2>/dev/null || true
git clone https://github.com/elemonkey/syncar .

# 8. Crear archivo .env
echo "⚙️ Configurando variables de entorno..."
cat > .env << 'ENVEOF'
COMPOSE_PROJECT_NAME=syncar
POSTGRES_DB=syncar_db
POSTGRES_USER=syncar_admin
POSTGRES_PASSWORD=syncar123456
DATABASE_URL=postgresql://syncar_admin:syncar123456@postgres:5432/syncar_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=supersecretkey-for-production-change-this-key-12345678
FRONTEND_URL=https://syncar.cl
NODE_ENV=production
ENV=production
NEXT_PUBLIC_API_URL=/api/v1
ENVEOF

# 9. Limpiar procesos en puertos
echo "🧹 Limpiando puertos..."
lsof -ti:80 | xargs -r kill -9 2>/dev/null || true
lsof -ti:443 | xargs -r kill -9 2>/dev/null || true
lsof -ti:8000 | xargs -r kill -9 2>/dev/null || true

# 10. Desplegar aplicación
echo "🚀 Desplegando aplicación..."
export COMPOSE_HTTP_TIMEOUT=300
docker-compose down --remove-orphans 2>/dev/null || true
docker system prune -f
docker-compose up -d --build

# 11. Esperar a que los servicios estén listos
echo "⏳ Esperando servicios..."
sleep 60

# 12. Obtener certificado SSL
echo "🔒 Configurando SSL..."
docker-compose stop nginx
certbot certonly --standalone \
  --non-interactive \
  --agree-tos \
  --email admin@syncar.cl \
  -d syncar.cl \
  -d www.syncar.cl || echo "⚠️ Error SSL, continuando..."

# 13. Reiniciar nginx
docker-compose up -d nginx

# 14. Verificaciones finales
echo "🔍 Verificando despliegue..."
sleep 30

echo "📋 Estado de contenedores:"
docker ps

echo "🔧 Verificando backend:"
curl -f http://localhost:8000/api/v1/health && echo "✅ Backend OK" || echo "❌ Backend Error"

echo "🌐 Verificando frontend:"
curl -f http://localhost/ && echo "✅ Frontend OK" || echo "❌ Frontend Error"

echo "🎉 DESPLIEGUE COMPLETADO!"
echo "🌐 HTTP: http://syncar.cl"
echo "🔒 HTTPS: https://syncar.cl"
echo "📊 API: https://syncar.cl/api/v1/health"