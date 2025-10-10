#!/bin/bash
set -e

echo "🚀 Configurando servidor Ubuntu limpio para SYNCAR..."

# 1. Actualizar sistema
echo "📦 Actualizando sistema..."
apt-get update
apt-get upgrade -y

# 2. Instalar dependencias básicas
echo "🔧 Instalando dependencias básicas..."
apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw

# 3. Instalar Docker
echo "🐳 Instalando Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# 4. Instalar Docker Compose
echo "📋 Instalando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 5. Iniciar y habilitar Docker
echo "▶️ Iniciando Docker..."
systemctl start docker
systemctl enable docker

# 6. Instalar Certbot para Let's Encrypt
echo "🔒 Instalando Certbot..."
apt-get install -y certbot

# 7. Configurar firewall básico
echo "🛡️ Configurando firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 8. Crear directorio de despliegue
echo "📁 Creando directorios..."
mkdir -p /www/wwwroot/syncar.cl
mkdir -p /etc/letsencrypt
mkdir -p /var/log/syncar

# 9. Configurar permisos
echo "🔐 Configurando permisos..."
chmod 755 /www/wwwroot/syncar.cl
chown -R root:root /www/wwwroot/syncar.cl

# 10. Verificar instalaciones
echo "✅ Verificando instalaciones..."
docker --version
docker-compose --version
git --version
certbot --version

echo "🎉 Servidor configurado exitosamente!"
echo "📍 Directorio de trabajo: /www/wwwroot/syncar.cl"
echo "🔥 Firewall configurado para puertos 22, 80, 443"
echo "🐳 Docker y Docker Compose listos"
echo "🔒 Certbot instalado para SSL"