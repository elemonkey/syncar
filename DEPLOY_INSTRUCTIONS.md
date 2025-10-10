# 🚀 DESPLIEGUE EN SERVIDOR LIMPIO - SYNCAR

## Secretos de GitHub necesarios

Para el despliegue automático, configura estos secretos en tu repositorio GitHub:

**Settings → Secrets and variables → Actions → Repository secrets**

```
SERVER_HOST=45.14.194.85
SERVER_USER=root
SERVER_SSH_KEY=[tu clave SSH privada completa]
POSTGRES_PASSWORD=tu_password_seguro_aqui
SECRET_KEY=una_clave_jwt_muy_larga_y_aleatoria_aqui
```

## Pasos para el despliegue completo

### 1. Configurar secretos en GitHub
Ve a tu repositorio GitHub:
- `https://github.com/elemonkey/syncar/settings/secrets/actions`
- Agrega los 5 secretos listados arriba

### 2. Ejecutar el despliegue
Una vez configurados los secretos, solo necesitas:

```bash
git add .
git commit -m "Deploy to clean server"
git push origin main
```

El GitHub Action automáticamente:
1. ✅ Configurará el servidor limpio (Docker, firewall, etc.)
2. ✅ Clonará el código y creará el `.env`
3. ✅ Levantará todos los contenedores
4. ✅ Obtendrá certificados SSL automáticamente
5. ✅ Configurará redirects HTTP → HTTPS
6. ✅ Verificará que todo esté funcionando

### 3. Verificar el despliegue
Después del despliegue:
- HTTP: `http://syncar.cl` (redirige a HTTPS)
- HTTPS: `https://syncar.cl` ✅
- API: `https://syncar.cl/api/v1/health` ✅

## Qué incluye este despliegue

- 🐳 **Docker & Docker Compose** completo
- 🔒 **SSL automático** con Let's Encrypt
- 🛡️ **Firewall configurado** (22, 80, 443)
- 🌐 **Nginx optimizado** con headers de seguridad
- 📊 **PostgreSQL + Redis** persistentes
- ⚡ **Frontend Next.js** en modo producción  
- 🚀 **Backend FastAPI** con Celery worker
- 🔄 **Redirects automáticos** HTTP → HTTPS

## Si algo falla

Revisa los logs del GitHub Action y verifica que:
1. Los secretos estén configurados correctamente
2. El servidor tenga acceso a internet
3. Los puertos 22, 80, 443 estén abiertos
4. El dominio syncar.cl apunte a la IP del servidor

## Monitoreo post-despliegue

Una vez desplegado, puedes monitorear con:

```bash
# Conectarse al servidor
ssh root@45.14.194.85

# Ver estado de contenedores
cd /www/wwwroot/syncar.cl
docker ps

# Ver logs en tiempo real
docker-compose logs -f

# Verificar certificado SSL
certbot certificates
```