# 🚀 Guía de Deploy - SYNCAR 2.0

Esta guía te ayudará a desplegar SYNCAR 2.0 en producción.

## 📋 Requisitos Previos

### Servidor
- **OS**: Ubuntu 22.04 LTS / Debian 11+ / CentOS 8+
- **RAM**: Mínimo 4GB (Recomendado 8GB)
- **CPU**: 2 cores (Recomendado 4 cores)
- **Disco**: 50GB mínimo (para base de datos y logs)
- **Dominio**: Un dominio apuntando a tu servidor (ej: syncar.cl)

### Software Necesario
- Docker Engine 24.0+
- Docker Compose 2.20+
- Git
- (Opcional) Certbot para SSL/HTTPS

---

## 🛠️ Instalación de Dependencias

### 1. Instalar Docker

```bash
# Actualizar paquetes
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker (reloguea después)
sudo usermod -aG docker $USER

# Verificar instalación
docker --version
docker-compose --version
```

### 2. Clonar Repositorio

```bash
cd /opt
sudo git clone https://github.com/tu-usuario/syncar2.0.git
cd syncar2.0
```

---

## ⚙️ Configuración

### 1. Variables de Entorno

```bash
# Copiar ejemplo de variables de entorno
cp .env.production.example .env

# Editar variables con tus valores
nano .env
```

**Variables CRÍTICAS que DEBES cambiar:**

```env
POSTGRES_PASSWORD=TU_PASSWORD_SUPER_SEGURO_AQUI
SECRET_KEY=TU_SECRET_KEY_MUY_LARGO_Y_ALEATORIO
JWT_SECRET_KEY=TU_JWT_SECRET_DIFERENTE_DEL_ANTERIOR
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
NEXT_PUBLIC_API_URL=https://tu-dominio.com/api/v1
```

**Generar claves seguras:**

```bash
# Generar SECRET_KEY
openssl rand -base64 64

# Generar JWT_SECRET_KEY
openssl rand -base64 64
```

### 2. Configurar Dominio

Edita `nginx/nginx.conf` y reemplaza `syncar.cl` con tu dominio:

```nginx
server_name tu-dominio.com www.tu-dominio.com;
```

---

## 🚀 Deploy Inicial

### 1. Dar permisos a scripts

```bash
chmod +x scripts/*.sh
```

### 2. Ejecutar deploy

```bash
./scripts/deploy.sh
```

Este script automáticamente:
- ✅ Crea backup de base de datos existente (si hay)
- ✅ Construye las imágenes Docker
- ✅ Levanta todos los servicios
- ✅ Ejecuta migraciones de base de datos
- ✅ Muestra el estado de los servicios

### 3. Verificar servicios

```bash
# Ver estado de contenedores
docker-compose -f docker-compose.prod.yml ps

# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f

# Ver logs de un servicio específico
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

## 🔒 Configurar SSL/HTTPS (Recomendado)

### 1. Instalar Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Detener Nginx temporalmente

```bash
docker-compose -f docker-compose.prod.yml stop nginx
```

### 3. Obtener certificado

```bash
sudo certbot certonly --standalone -d tu-dominio.com -d www.tu-dominio.com
```

### 4. Copiar certificados a proyecto

```bash
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem nginx/ssl/
sudo chown -R $USER:$USER nginx/ssl
```

### 5. Descomentar configuración HTTPS en `nginx/nginx.conf`

Busca y descomenta la sección de HTTPS (líneas con `# SSL configuration`)

### 6. Reiniciar Nginx

```bash
docker-compose -f docker-compose.prod.yml up -d nginx
```

### 7. Configurar renovación automática

```bash
# Crear script de renovación
sudo nano /etc/cron.daily/certbot-renew

# Agregar:
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem /opt/syncar2.0/nginx/ssl/
cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem /opt/syncar2.0/nginx/ssl/
docker-compose -f /opt/syncar2.0/docker-compose.prod.yml restart nginx

# Dar permisos
sudo chmod +x /etc/cron.daily/certbot-renew
```

---

## 📦 Backups Automáticos

### Configurar Cron Job

```bash
# Editar crontab
crontab -e

# Agregar backup diario a las 3 AM
0 3 * * * /opt/syncar2.0/scripts/backup.sh >> /var/log/syncar-backup.log 2>&1
```

### Backup Manual

```bash
./scripts/backup.sh
```

### Restaurar Backup

```bash
# Listar backups disponibles
ls -lh backups/

# Restaurar un backup específico
./scripts/restore.sh backups/syncar_backup_20251016_030000.sql.gz
```

---

## 🔄 Actualizar Aplicación

### 1. Pull últimos cambios

```bash
cd /opt/syncar2.0
git pull origin main
```

### 2. Ejecutar deploy

```bash
./scripts/deploy.sh
```

---

## 📊 Monitoreo

### Acceder a servicios

- **Frontend**: http://tu-dominio.com
- **Backend API**: http://tu-dominio.com/api
- **API Docs**: http://tu-dominio.com/api/docs
- **Flower (Celery)**: http://tu-dominio.com:5555

### Ver logs

```bash
# Logs de todos los servicios
docker-compose -f docker-compose.prod.yml logs -f

# Logs del backend
docker-compose -f docker-compose.prod.yml logs -f backend

# Logs de Celery
docker-compose -f docker-compose.prod.yml logs -f celery-worker

# Últimas 100 líneas
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Recursos del sistema

```bash
# Ver uso de recursos de contenedores
docker stats

# Ver espacio en disco
df -h
docker system df
```

---

## 🛑 Comandos Útiles

### Detener aplicación

```bash
docker-compose -f docker-compose.prod.yml stop
```

### Iniciar aplicación

```bash
docker-compose -f docker-compose.prod.yml start
```

### Reiniciar aplicación

```bash
docker-compose -f docker-compose.prod.yml restart
```

### Detener y eliminar contenedores

```bash
docker-compose -f docker-compose.prod.yml down
```

### Acceder a un contenedor

```bash
# Backend
docker exec -it importapp-backend bash

# PostgreSQL
docker exec -it importapp-postgres psql -U syncar_user -d syncar_prod

# Redis
docker exec -it importapp-redis redis-cli
```

### Limpiar recursos

```bash
# Limpiar contenedores detenidos
docker container prune -f

# Limpiar imágenes sin usar
docker image prune -a -f

# Limpiar volúmenes sin usar
docker volume prune -f

# Limpiar todo (¡CUIDADO!)
docker system prune -a --volumes -f
```

---

## 🔧 Troubleshooting

### Servicio no inicia

```bash
# Ver logs detallados
docker-compose -f docker-compose.prod.yml logs backend

# Verificar configuración
docker-compose -f docker-compose.prod.yml config

# Reconstruir contenedor
docker-compose -f docker-compose.prod.yml up -d --build backend
```

### Base de datos no conecta

```bash
# Verificar que PostgreSQL está corriendo
docker-compose -f docker-compose.prod.yml ps postgres

# Ver logs de PostgreSQL
docker-compose -f docker-compose.prod.yml logs postgres

# Verificar conectividad desde backend
docker exec importapp-backend ping postgres
```

### Problemas de permisos

```bash
# Arreglar permisos de volúmenes
sudo chown -R $USER:$USER .
```

### Out of Memory

```bash
# Ver uso de memoria
docker stats

# Aumentar límites en docker-compose.prod.yml
```

---

## 🎯 Checklist de Deploy

- [ ] Servidor con requisitos mínimos cumplidos
- [ ] Docker y Docker Compose instalados
- [ ] Dominio apuntando al servidor
- [ ] Variables de entorno configuradas (`.env`)
- [ ] Claves secretas generadas y seguras
- [ ] SSL/HTTPS configurado (certbot)
- [ ] Backups automáticos configurados (cron)
- [ ] Monitoreo configurado
- [ ] Firewall configurado (puertos 80, 443, 22)
- [ ] Deploy exitoso ejecutado
- [ ] Aplicación accesible desde el dominio
- [ ] Logs verificados sin errores críticos

---

## 🆘 Soporte

Si tienes problemas con el deploy:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica variables de entorno en `.env`
3. Consulta la documentación: `docs/`
4. Contacta al equipo de desarrollo

---

## 📚 Recursos Adicionales

- [Documentación de Docker](https://docs.docker.com/)
- [Documentación de Docker Compose](https://docs.docker.com/compose/)
- [Documentación de Nginx](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**¡SYNCAR 2.0 en Producción! 🚀**
