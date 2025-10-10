#!/bin/bash

echo "=== Configurando Nginx para syncar.cl ==="

# 1. Crear la configuración principal de Nginx
echo "Creando configuración principal de Nginx..."
cat > /www/server/nginx/conf/nginx.conf << 'EOF'
user  www-data;
worker_processes  auto;
error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;

    include /etc/nginx/sites-enabled/*;
}
EOF

# 2. Crear la configuración del sitio syncar.cl
echo "Creando configuración del sitio syncar.cl..."
cat > /etc/nginx/sites-available/syncar << 'EOF'
server {
    listen 80;
    server_name syncar.cl;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 3. Crear enlace simbólico si no existe
echo "Creando enlace simbólico..."
if [ ! -L /etc/nginx/sites-enabled/syncar ]; then
    ln -s /etc/nginx/sites-available/syncar /etc/nginx/sites-enabled/syncar
fi

# 4. Verificar configuración
echo "Verificando configuración de Nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuración de Nginx válida"
    echo "Reiniciando Nginx..."
    systemctl restart nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx reiniciado correctamente"
        echo "🚀 syncar.cl debería estar funcionando ahora"
    else
        echo "❌ Error al reiniciar Nginx"
    fi
else
    echo "❌ Error en la configuración de Nginx"
fi

echo "=== Configuración completada ==="