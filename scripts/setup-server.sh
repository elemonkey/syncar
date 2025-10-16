#!/bin/bash
# 🔐 Setup inicial del servidor SYNCAR 2.0
# Este script configura el servidor la PRIMERA VEZ

set -e  # Exit on error

echo "🚀 SYNCAR 2.0 - Setup Servidor"
echo "================================"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVER_IP="45.14.194.85"
SERVER_USER="root"
PROJECT_DIR="/opt/import-app"

echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "Este script necesita que puedas conectarte al servidor con contraseña"
echo "Servidor: $SERVER_USER@$SERVER_IP"
echo ""
read -p "¿Tienes la contraseña del servidor? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${RED}❌ Necesitas la contraseña para continuar${NC}"
    exit 1
fi

echo ""
echo "📋 Este script va a:"
echo "  1. Copiar tu clave SSH pública al servidor"
echo "  2. Instalar Docker y dependencias"
echo "  3. Clonar el repositorio"
echo "  4. Configurar el ambiente"
echo ""
read -p "¿Continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}⏸️  Cancelado${NC}"
    exit 0
fi

echo ""
echo "=========================="
echo "Paso 1: Copiar clave SSH"
echo "=========================="
echo ""

# Copiar clave SSH
echo -e "${YELLOW}📤 Copiando clave SSH al servidor...${NC}"
ssh-copy-id -i ~/.ssh/id_ed25519.pub $SERVER_USER@$SERVER_IP

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Clave SSH copiada exitosamente${NC}"
else
    echo -e "${RED}❌ Error al copiar la clave SSH${NC}"
    exit 1
fi

echo ""
echo "=========================="
echo "Paso 2: Verificar conexión"
echo "=========================="
echo ""

# Verificar conexión sin contraseña
echo -e "${YELLOW}🔍 Verificando conexión SSH...${NC}"
ssh -o BatchMode=yes $SERVER_USER@$SERVER_IP "echo 'Conexión exitosa'"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Conexión SSH sin contraseña funcionando${NC}"
else
    echo -e "${RED}❌ Error: Aún se requiere contraseña${NC}"
    exit 1
fi

echo ""
echo "=========================="
echo "Paso 3: Instalar Docker"
echo "=========================="
echo ""

ssh $SERVER_USER@$SERVER_IP "bash -s" << 'ENDSSH'
    set -e

    echo "📦 Actualizando paquetes..."
    apt update -qq

    echo "🐳 Instalando Docker..."
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com | sh
        systemctl enable docker
        systemctl start docker
        echo "✅ Docker instalado"
    else
        echo "✅ Docker ya está instalado"
    fi

    echo "📦 Instalando dependencias..."
    apt install -y git curl wget htop

    # Instalar docker-compose plugin
    if ! docker compose version &> /dev/null; then
        apt install -y docker-compose-plugin
        echo "✅ Docker Compose instalado"
    else
        echo "✅ Docker Compose ya está instalado"
    fi

    echo ""
    echo "Versiones instaladas:"
    docker --version
    docker compose version
    git --version
ENDSSH

echo -e "${GREEN}✅ Docker y dependencias instaladas${NC}"

echo ""
echo "=========================="
echo "Paso 4: Clonar repositorio"
echo "=========================="
echo ""

ssh $SERVER_USER@$SERVER_IP "bash -s" << 'ENDSSH'
    set -e

    PROJECT_DIR="/opt/import-app"

    # Crear directorio si no existe
    if [ ! -d "$PROJECT_DIR" ]; then
        echo "📁 Creando directorio $PROJECT_DIR..."
        mkdir -p $PROJECT_DIR
    fi

    cd $PROJECT_DIR

    # Clonar repositorio
    if [ ! -d ".git" ]; then
        echo "📥 Clonando repositorio..."
        git clone https://github.com/elemonkey/syncar.git .
        echo "✅ Repositorio clonado"
    else
        echo "✅ Repositorio ya existe"
        echo "🔄 Actualizando..."
        git pull origin main
    fi

    echo ""
    echo "📊 Estado del repositorio:"
    git log --oneline -3
ENDSSH

echo -e "${GREEN}✅ Repositorio clonado${NC}"

echo ""
echo "=========================="
echo "Paso 5: Configurar .env"
echo "=========================="
echo ""

# Copiar .env.production como .env
ssh $SERVER_USER@$SERVER_IP "bash -s" << 'ENDSSH'
    set -e

    PROJECT_DIR="/opt/import-app"
    cd $PROJECT_DIR

    if [ ! -f ".env" ]; then
        echo "📝 Creando archivo .env..."
        if [ -f ".env.production" ]; then
            cp .env.production .env
            echo "✅ Archivo .env creado desde .env.production"
        else
            echo "⚠️  Archivo .env.production no encontrado"
            echo "❌ Debes crear el archivo .env manualmente"
            exit 1
        fi
    else
        echo "✅ Archivo .env ya existe"
    fi

    # Hacer scripts ejecutables
    echo "🔧 Configurando permisos de scripts..."
    chmod +x scripts/*.sh
    echo "✅ Scripts configurados"
ENDSSH

echo -e "${GREEN}✅ Configuración inicial completada${NC}"

echo ""
echo "================================"
echo "✅ SETUP COMPLETADO"
echo "================================"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1. Configurar secrets en GitHub:"
echo "   - SERVER_IP: 45.14.194.85"
echo "   - SERVER_USER: root"
echo "   - SSH_PRIVATE_KEY: (tu clave privada)"
echo ""
echo "   URL: https://github.com/elemonkey/syncar/settings/secrets/actions"
echo ""
echo "2. Hacer deploy:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo "   cd $PROJECT_DIR"
echo "   ./scripts/deploy.sh"
echo ""
echo "3. Configurar SSL:"
echo "   ssh $SERVER_USER@$SERVER_IP"
echo "   apt install certbot python3-certbot-nginx -y"
echo "   certbot --nginx -d syncar.cl -d www.syncar.cl"
echo ""
echo -e "${GREEN}🎉 ¡Listo para deploy!${NC}"
