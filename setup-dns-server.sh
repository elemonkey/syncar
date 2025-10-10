#!/bin/bash
set -e

echo "🌐 Configurando servidor DNS para syncar.cl"
echo "============================================"

# Actualizar paquetes
echo "📦 Actualizando sistema..."
apt-get update

# Instalar BIND9
echo "🔧 Instalando BIND9..."
apt-get install -y bind9 bind9utils bind9-doc

# Crear configuración principal
echo "⚙️ Configurando BIND9..."
cat > /etc/bind/named.conf.local << 'EOF'
zone "syncar.cl" {
    type master;
    file "/etc/bind/db.syncar.cl";
};
EOF

# Crear zona DNS para syncar.cl
echo "📋 Creando zona DNS..."
cat > /etc/bind/db.syncar.cl << 'EOF'
$TTL    604800
@       IN      SOA     ns1.syncar.cl. admin.syncar.cl. (
                     2025101001         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL

; Name servers
@       IN      NS      ns1.syncar.cl.
@       IN      NS      ns2.syncar.cl.

; A records
@       IN      A       45.14.194.85
www     IN      A       45.14.194.85
ns1     IN      A       45.14.194.85
ns2     IN      A       45.14.194.85

; CNAME records (opcional)
mail    IN      CNAME   @
ftp     IN      CNAME   @
EOF

# Configurar opciones de BIND
echo "🔧 Configurando opciones de BIND..."
cat > /etc/bind/named.conf.options << 'EOF'
options {
    directory "/var/cache/bind";
    
    // Permitir consultas desde cualquier lugar
    allow-query { any; };
    
    // Escuchar en todas las interfaces
    listen-on { any; };
    listen-on-v6 { any; };
    
    // Forwarders para consultas externas
    forwarders {
        8.8.8.8;
        8.8.4.4;
        1.1.1.1;
    };
    
    // Configuración de seguridad
    dnssec-validation auto;
    recursion yes;
    allow-recursion { any; };
    
    auth-nxdomain no;
};
EOF

# Verificar configuración
echo "🔍 Verificando configuración..."
named-checkconf
named-checkzone syncar.cl /etc/bind/db.syncar.cl

# Reiniciar y habilitar BIND
echo "🔄 Reiniciando BIND9..."
systemctl restart bind9
systemctl enable bind9

# Configurar firewall para DNS
echo "🛡️ Configurando firewall para DNS..."
ufw allow 53/tcp
ufw allow 53/udp

# Verificar estado
echo "📋 Verificando estado del servicio..."
systemctl status bind9 --no-pager

echo ""
echo "🔍 Probando configuración DNS..."
sleep 5

# Probar resolución local
echo "Probando resolución local:"
nslookup syncar.cl 127.0.0.1 || echo "❌ Error en resolución local"

echo ""
echo "✅ Servidor DNS configurado!"
echo ""
echo "📋 Configuración creada:"
echo "• ns1.syncar.cl → 45.14.194.85"
echo "• ns2.syncar.cl → 45.14.194.85"
echo "• syncar.cl → 45.14.194.85"  
echo "• www.syncar.cl → 45.14.194.85"
echo ""
echo "⏳ Espera 5-15 minutos para propagación DNS global"
echo ""
echo "🧪 Para probar desde externa:"
echo "nslookup syncar.cl 45.14.194.85"