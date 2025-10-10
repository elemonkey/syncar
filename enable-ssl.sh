#!/bin/bash

echo "🔧 Script de activación SSL para SYNCAR"
echo "Este script debe ejecutarse DESPUÉS de configurar el DNS"

cd /www/wwwroot/syncar.cl

echo "🔍 Verificando que el dominio apunte a este servidor..."
nslookup syncar.cl || { echo "❌ DNS no configurado. Configura syncar.cl para apuntar a esta IP primero."; exit 1; }

echo "🔒 Obteniendo certificado SSL..."
docker-compose stop nginx

certbot certonly --standalone \
  --non-interactive \
  --agree-tos \
  --email admin@syncar.cl \
  -d syncar.cl \
  -d www.syncar.cl

if [ $? -eq 0 ]; then
    echo "✅ Certificado SSL obtenido exitosamente"
    
    echo "🔄 Actualizando nginx.conf con SSL..."
    cat nginx/nginx.conf nginx/ssl.conf > nginx/nginx-temp.conf
    
    # Agregar redirección HTTP -> HTTPS
    cat > nginx/nginx.conf << 'NGINXEOF'
upstream frontend {
    server frontend:3000;
}

upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name syncar.cl www.syncar.cl;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name syncar.cl www.syncar.cl;

    ssl_certificate /etc/letsencrypt/live/syncar.cl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/syncar.cl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /api/ {
        proxy_pass http://backend/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF

    echo "🔄 Reiniciando nginx con SSL..."
    docker-compose up -d nginx
    
    echo "✅ SSL configurado exitosamente!"
    echo "🌐 HTTPS: https://syncar.cl"
    echo "🔒 Redirección HTTP -> HTTPS activada"
else
    echo "❌ Error obteniendo certificado SSL"
    echo "🔄 Reiniciando nginx sin SSL..."
    docker-compose up -d nginx
fi