# 🔒 Configuración SSL/HTTPS para SYNCAR

## Requisitos Previos

- ✅ Dominio apuntando al servidor (syncar.cl → 45.14.194.85)
- ✅ Puerto 80 y 443 abiertos en el firewall
- ✅ Certbot instalado en el servidor

## Opción 1: Script Automático (Recomendado)

### Desde tu máquina local:

```bash
# 1. Copiar el script al servidor
scp scripts/setup-ssl.sh root@45.14.194.85:/root/syncar/scripts/

# 2. Ejecutar el script en el servidor
ssh root@45.14.194.85 "cd /root/syncar && chmod +x scripts/setup-ssl.sh && ./scripts/setup-ssl.sh"
```

El script hará todo automáticamente:
- Detendrá nginx temporalmente
- Obtendrá el certificado SSL de Let's Encrypt
- Copiará los certificados a la carpeta correcta
- Reiniciará nginx con SSL habilitado
- Verificará que todo funcione

## Opción 2: Paso a Paso Manual

### 1. Conectarse al servidor

```bash
ssh root@45.14.194.85
cd /root/syncar
```

### 2. Detener nginx temporalmente

```bash
docker-compose -f docker-compose.prod.yml stop nginx
```

### 3. Obtener certificado SSL

```bash
certbot certonly \
  --standalone \
  --preferred-challenges http \
  --non-interactive \
  --agree-tos \
  --email admin@syncar.cl \
  -d syncar.cl \
  -d www.syncar.cl
```

### 4. Copiar certificados

```bash
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/syncar.cl/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/syncar.cl/privkey.pem nginx/ssl/
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem
```

### 5. Actualizar nginx.conf

Ya está actualizado en el repositorio con SSL habilitado. Solo necesitas hacer pull:

```bash
git pull origin main
```

### 6. Reiniciar nginx

```bash
docker-compose -f docker-compose.prod.yml up -d --force-recreate nginx
```

### 7. Verificar

```bash
# Verificar que redirecciona a HTTPS
curl -I http://syncar.cl

# Verificar HTTPS
curl -I https://syncar.cl
```

## Renovación Automática

Los certificados de Let's Encrypt expiran cada 90 días. Para renovarlos automáticamente:

### Configurar cron job:

```bash
crontab -e
```

Agregar esta línea:

```bash
0 0,12 * * * certbot renew --quiet --deploy-hook 'cd /root/syncar && docker-compose -f docker-compose.prod.yml restart nginx'
```

Esto intentará renovar los certificados 2 veces al día (00:00 y 12:00).

## Verificación de SSL

### Usando SSL Labs

Visita: https://www.ssllabs.com/ssltest/analyze.html?d=syncar.cl

Deberías obtener al menos una calificación "A".

### Desde terminal

```bash
# Verificar certificado
openssl s_client -connect syncar.cl:443 -servername syncar.cl < /dev/null

# Verificar fecha de expiración
echo | openssl s_client -servername syncar.cl -connect syncar.cl:443 2>/dev/null | openssl x509 -noout -dates
```

## URLs después de SSL

- ✅ http://syncar.cl → Redirige a https://syncar.cl
- ✅ http://www.syncar.cl → Redirige a https://www.syncar.cl
- ✅ https://syncar.cl → Sitio principal (seguro)
- ✅ https://www.syncar.cl → Sitio principal (seguro)
- ✅ https://syncar.cl/api/docs → API Documentation
- ✅ https://syncar.cl/flower → Celery Monitor

## Troubleshooting

### Error: "Address already in use"

```bash
# Verificar qué está usando el puerto 80/443
lsof -i:80
lsof -i:443

# Detener todos los contenedores
cd /root/syncar
docker-compose -f docker-compose.prod.yml down

# Reintentar
./scripts/setup-ssl.sh
```

### Error: "Certificate validation failed"

Verifica que:
1. El dominio está apuntando correctamente: `dig syncar.cl`
2. El puerto 80 está accesible desde internet: `telnet syncar.cl 80`
3. No hay firewall bloqueando: `ufw status`

### Certificado no se renueva

```bash
# Probar renovación manualmente
certbot renew --dry-run

# Forzar renovación
certbot renew --force-renewal

# Verificar logs
tail -f /var/log/letsencrypt/letsencrypt.log
```

## Headers de Seguridad

La configuración incluye:

- ✅ **HSTS**: Fuerza HTTPS en navegadores
- ✅ **X-Frame-Options**: Previene clickjacking
- ✅ **X-Content-Type-Options**: Previene MIME sniffing
- ✅ **X-XSS-Protection**: Protección XSS en navegadores antiguos
- ✅ **TLS 1.2/1.3**: Solo protocolos seguros
- ✅ **Ciphers modernos**: Cifrado fuerte

## Próximos Pasos

1. ✅ Configurar SSL - **En este commit**
2. ⏭️ Habilitar HSTS después de verificar que todo funciona
3. ⏭️ Configurar autenticación para Flower
4. ⏭️ Configurar backup automático de certificados

## Soporte

Si tienes problemas, revisa los logs:

```bash
# Logs de nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Logs de certbot
tail -f /var/log/letsencrypt/letsencrypt.log
```
