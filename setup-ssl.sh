#!/bin/bash
set -e

echo "🔒 Script de configuración SSL automático para SYNCAR"
echo "=================================================="

cd /www/wwwroot/syncar.cl

echo "🔍 Verificando que el dominio apunte a este servidor..."
echo "Probando resolución DNS de syncar.cl..."

# Verificar DNS
if nslookup syncar.cl | grep -q "45.14.194.85"; then
    echo "✅ DNS configurado correctamente"
else
    echo "❌ DNS no configurado o no propagado aún"
    echo "📋 Configuración necesaria en tu proveedor DNS:"
    echo "   Tipo: A, Nombre: @, Valor: 45.14.194.85"
    echo "   Tipo: A, Nombre: www, Valor: 45.14.194.85"
    echo ""
    echo "⏳ Espera 5-15 minutos para la propagación DNS y vuelve a ejecutar este script"
    exit 1
fi

echo "🛑 Deteniendo nginx temporalmente para obtener certificados..."
docker-compose stop nginx

echo "🔒 Obteniendo certificados SSL con Let's Encrypt..."
certbot certonly --standalone \
  --non-interactive \
  --agree-tos \
  --email admin@syncar.cl \
  -d syncar.cl \
  -d www.syncar.cl \
  --rsa-key-size 4096

if [ $? -eq 0 ]; then
    echo "✅ Certificados SSL obtenidos exitosamente"
    
    echo "🔄 Actualizando nginx.conf para HTTPS..."
    cat > nginx/nginx.conf << 'NGINXEOF'
upstream frontend {
    server frontend:3000;
}

upstream backend {
    server backend:8000;
}

# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name syncar.cl www.syncar.cl;
    
    # Permitir Let's Encrypt challenges
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirigir todo lo demás a HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# Servidor HTTPS principal
server {
    listen 443 ssl http2;
    server_name syncar.cl www.syncar.cl;

    # Configuración SSL
    ssl_certificate /etc/letsencrypt/live/syncar.cl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/syncar.cl/privkey.pem;
    
    # Configuración SSL moderna
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Headers de seguridad
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Proxy para frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_cache_bypass $http_upgrade;
        proxy_buffering off;
    }

    # Proxy para backend API
    location /api/ {
        proxy_pass http://backend/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_http_version 1.1;
        proxy_buffering off;
    }

    # Optimización para archivos estáticos
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINXEOF

    echo "🔄 Actualizando variables de entorno para HTTPS..."
    sed -i 's/FRONTEND_URL=http:/FRONTEND_URL=https:/' .env
    
    echo "🔄 Reiniciando servicios con HTTPS..."
    docker-compose up -d
    
    echo "⏳ Esperando servicios..."
    sleep 15
    
    echo "🔍 Verificando configuración HTTPS..."
    echo "Backend directo:"
    curl -f http://localhost:8000/api/v1/health && echo " ✅" || echo " ❌"
    
    echo "HTTPS (interno):"
    curl -f -k https://localhost/ >/dev/null 2>&1 && echo " ✅" || echo " ❌"
    
    echo "HTTP redirect:"
    curl -I http://syncar.cl 2>/dev/null | grep -q "301" && echo " ✅" || echo " ❌"
    
    echo "HTTPS externo:"
    curl -f https://syncar.cl/ >/dev/null 2>&1 && echo " ✅" || echo " ❌"
    
    echo ""
    echo "🎉 ¡SSL configurado exitosamente!"
    echo "🌐 HTTP: http://syncar.cl (redirige a HTTPS)"
    echo "🔒 HTTPS: https://syncar.cl"
    echo "📊 API: https://syncar.cl/api/v1/health"
    echo ""
    echo "📋 Configuración de renovación automática:"
    echo "Ejecuta este comando para configurar renovación automática:"
    echo "echo '0 2 * * * certbot renew --quiet && docker-compose restart nginx' | crontab -"
    
else
    echo "❌ Error obteniendo certificados SSL"
    echo "🔄 Reiniciando nginx sin SSL..."
    docker-compose up -d nginx
    echo "💡 Verifica que el DNS esté correctamente configurado y propagado"
fi