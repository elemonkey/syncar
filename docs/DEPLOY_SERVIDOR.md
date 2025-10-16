# 🚀 GUÍA DE DEPLOY A PRODUCCIÓN - SYNCAR 2.0
# Servidor: 45.14.194.85 (syncar.cl)

## 📋 CHECKLIST PRE-DEPLOY

### ✅ Preparación Local (Ya completado)
- [x] Aplicación funcionando en desarrollo
- [x] 73 categorías de Noriega importadas
- [x] Backend y Frontend testeados
- [x] Variables de entorno de producción creadas (.env.production)
- [x] Claves secretas generadas

### 🔧 Preparación del Servidor

#### 1. Conectarse al servidor
```bash
ssh root@45.14.194.85
# O si tienes un usuario específico:
ssh usuario@45.14.194.85
```

#### 2. Instalar Docker y Docker Compose
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose (si no está incluido)
sudo apt install docker-compose-plugin -y

# Verificar instalación
docker --version
docker compose version
```

#### 3. Instalar Git
```bash
sudo apt install git -y
```

#### 4. Crear directorio para la aplicación
```bash
sudo mkdir -p /opt/syncar
sudo chown $USER:$USER /opt/syncar
cd /opt/syncar
```

---

## 📦 SUBIR CÓDIGO AL SERVIDOR

### Opción A: Git (Recomendado)

#### 1. Crear repositorio privado en GitHub/GitLab
- Sube tu código a un repositorio privado

#### 2. Clonar en el servidor
```bash
cd /opt/syncar
git clone https://github.com/tu-usuario/syncar2.0.git .
```

### Opción B: SCP (Transferencia directa)

#### Desde tu Mac, ejecuta:
```bash
# Comprimir el proyecto (excluyendo node_modules y venv)
cd /Users/maxberrios/Desktop/REPUESTOS
tar --exclude='SYNCAR2.0/frontend/node_modules' \
    --exclude='SYNCAR2.0/backend/venv' \
    --exclude='SYNCAR2.0/backend/__pycache__' \
    --exclude='SYNCAR2.0/.git' \
    -czf syncar2.0.tar.gz SYNCAR2.0/

# Subir al servidor
scp syncar2.0.tar.gz root@45.14.194.85:/opt/

# En el servidor, descomprimir
ssh root@45.14.194.85
cd /opt
tar -xzf syncar2.0.tar.gz
mv SYNCAR2.0 syncar
cd syncar
```

---

## ⚙️ CONFIGURACIÓN EN EL SERVIDOR

### 1. Copiar archivo de producción
```bash
cd /opt/syncar
cp .env.production .env
```

### 2. Editar variables sensibles (si es necesario)
```bash
nano .env
```

Verifica especialmente:
- `POSTGRES_PASSWORD` (ya configurado: Monochico1982***)
- `DOMAIN_NAME` (ya configurado: syncar.cl)
- Credenciales de importadores (si las tienes)

### 3. Dar permisos a scripts
```bash
chmod +x scripts/*.sh
```

---

## 🌐 CONFIGURAR NGINX Y SSL

### 1. Actualizar nginx.conf con tu dominio
```bash
nano nginx/nginx.conf
```

Busca y reemplaza `syncar.cl` si es necesario (ya debería estar correcto).

### 2. Instalar Certbot para SSL (HTTPS)
```bash
sudo apt install certbot python3-certbot-nginx -y
```

---

## 🚀 EJECUTAR DEPLOY

### 1. Ejecutar script de deploy
```bash
cd /opt/syncar
./scripts/deploy.sh
```

Este script automáticamente:
- ✅ Hace backup de la base de datos
- ✅ Construye las imágenes Docker
- ✅ Inicia todos los servicios
- ✅ Ejecuta migraciones
- ✅ Verifica que todo esté funcionando

### 2. Configurar SSL con Certbot (después del primer deploy)
```bash
sudo certbot --nginx -d syncar.cl -d www.syncar.cl
```

Sigue las instrucciones de Certbot:
- Ingresa tu email
- Acepta términos
- Certbot configurará SSL automáticamente

### 3. Renovación automática de SSL
```bash
# Certbot crea un cron job automáticamente, pero verifica:
sudo certbot renew --dry-run
```

---

## ✅ VERIFICACIÓN POST-DEPLOY

### 1. Verificar servicios corriendo
```bash
docker compose -f docker-compose.prod.yml ps
```

Deberías ver:
- postgres (healthy)
- redis (healthy)
- backend (healthy)
- frontend (running)
- celery-worker (running)
- celery-beat (running)
- flower (running)
- nginx (running)

### 2. Ver logs
```bash
# Todos los servicios
docker compose -f docker-compose.prod.yml logs -f

# Solo backend
docker logs importapp-backend -f

# Solo frontend
docker logs importapp-frontend -f
```

### 3. Verificar base de datos
```bash
docker exec -it importapp-postgres psql -U elemonkey -d syncar_db

# Dentro de psql:
\dt  # Listar tablas
SELECT COUNT(*) FROM categories;  # Debe mostrar 0 (base nueva)
\q   # Salir
```

### 4. Probar la aplicación
```bash
# Desde el servidor
curl http://localhost/health

# Desde tu navegador
https://syncar.cl
https://syncar.cl/importers
https://syncar.cl/api/docs (si DEBUG=true)
```

---

## 🔄 IMPORTAR DATOS EXISTENTES

### Opción 1: Backup desde desarrollo
```bash
# En tu Mac, hacer backup de la BD de desarrollo
docker exec importapp-postgres-dev pg_dump -U elemonkey syncar_db > backup_desarrollo.sql

# Subir al servidor
scp backup_desarrollo.sql root@45.14.194.85:/opt/syncar/backups/

# En el servidor, restaurar
docker exec -i importapp-postgres psql -U elemonkey syncar_db < /opt/syncar/backups/backup_desarrollo.sql
```

### Opción 2: Reimportar desde Noriega
Una vez desplegado, simplemente:
1. Ir a https://syncar.cl/importers
2. Seleccionar NORIEGA
3. Clic en "Importar Categorías"
4. Esperar a que se importen las 73 categorías

---

## 📊 MONITOREO

### Flower (Monitor de Celery)
```
https://syncar.cl:5555
```

### Logs en tiempo real
```bash
docker compose -f docker-compose.prod.yml logs -f
```

### Recursos del sistema
```bash
htop
docker stats
```

---

## 🔥 FIREWALL Y SEGURIDAD

### Configurar UFW (firewall)
```bash
# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

---

## 🛠️ MANTENIMIENTO

### Reiniciar servicios
```bash
docker compose -f docker-compose.prod.yml restart
```

### Detener servicios
```bash
docker compose -f docker-compose.prod.yml down
```

### Actualizar aplicación
```bash
cd /opt/syncar
git pull
./scripts/deploy.sh
```

### Ver uso de disco
```bash
df -h
docker system df
```

### Limpiar imágenes antiguas
```bash
docker system prune -a
```

---

## 🆘 TROUBLESHOOTING

### Servicios no inician
```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs

# Reconstruir imágenes
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### Puerto ya en uso
```bash
sudo lsof -i :80
sudo lsof -i :443
# Matar proceso si es necesario
sudo kill -9 PID
```

### Reinicio automático tras reboot del servidor
Los contenedores ya tienen configurado `restart: unless-stopped`, pero verifica:
```bash
docker compose -f docker-compose.prod.yml ps
```

---

## 📞 RESUMEN RÁPIDO

```bash
# 1. Conectar al servidor
ssh root@45.14.194.85

# 2. Instalar dependencias
curl -fsSL https://get.docker.com | sh
apt install git docker-compose-plugin certbot python3-certbot-nginx -y

# 3. Subir código
cd /opt && mkdir syncar && cd syncar
# (git clone o scp)

# 4. Configurar
cp .env.production .env
chmod +x scripts/*.sh

# 5. Deploy
./scripts/deploy.sh

# 6. SSL
certbot --nginx -d syncar.cl -d www.syncar.cl

# 7. Verificar
curl http://localhost/health
```

---

## ✅ CHECKLIST FINAL

- [ ] Servidor actualizado
- [ ] Docker instalado
- [ ] Código subido a /opt/syncar
- [ ] .env.production copiado a .env
- [ ] Scripts con permisos de ejecución
- [ ] Deploy ejecutado exitosamente
- [ ] SSL configurado con Certbot
- [ ] Servicios corriendo (docker ps)
- [ ] Aplicación accesible en https://syncar.cl
- [ ] Datos importados o listos para importar
- [ ] Firewall configurado
- [ ] Backups programados

---

**¡Listo! Tu aplicación SYNCAR 2.0 está en producción! 🚀**
