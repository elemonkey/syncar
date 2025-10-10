#!/bin/bash

echo "🔍 Verificando configuración DNS de syncar.cl"
echo "============================================="

echo ""
echo "1️⃣ Probando resolución local:"
nslookup syncar.cl 127.0.0.1

echo ""
echo "2️⃣ Probando desde servidor DNS:"
nslookup syncar.cl 45.14.194.85

echo ""
echo "3️⃣ Probando www.syncar.cl:"
nslookup www.syncar.cl 45.14.194.85

echo ""
echo "4️⃣ Verificando nameservers:"
nslookup -type=NS syncar.cl 45.14.194.85

echo ""
echo "5️⃣ Estado del servicio BIND9:"
systemctl status bind9 --no-pager -l

echo ""
echo "6️⃣ Logs de BIND9 (últimas 10 líneas):"
tail -10 /var/log/syslog | grep named

echo ""
echo "✅ Verificación completa!"
echo ""
echo "Si todo está OK, procede con SSL:"
echo "sudo ./setup-ssl.sh"