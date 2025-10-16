# 🔐 CONFIGURAR GITHUB SECRETS - SYNCAR 2.0

## ❗ ERROR ACTUAL

```
Error: missing server host
```

**Causa**: Faltan los secrets de GitHub configurados para el deploy automático.

---

## ✅ SOLUCIÓN: Configurar 3 Secrets

### 📍 Paso 1: Ir a Settings

1. Ve a tu repositorio: **https://github.com/elemonkey/syncar**
2. Click en **Settings** (⚙️) en la parte superior
3. En el menú izquierdo, busca **Secrets and variables**
4. Click en **Actions**
5. Click en **New repository secret**

---

### 🔑 Paso 2: Agregar los 3 Secrets

#### Secret #1: SERVER_IP

- **Name**: `SERVER_IP`
- **Secret**: `45.14.194.85`
- Click **Add secret**

#### Secret #2: SERVER_USER

- **Name**: `SERVER_USER`
- **Secret**: `root`
- Click **Add secret**

#### Secret #3: SSH_PRIVATE_KEY

- **Name**: `SSH_PRIVATE_KEY`
- **Secret**: (Copia TODA la clave de abajo)

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCp8YYa9Of7JhKG7zH+xWeBovBnCBO5JC4pnomwvWNw9wAAAJCgKBe/oCgX
vwAAAAtzc2gtZWQyNTUxOQAAACCp8YYa9Of7JhKG7zH+xWeBovBnCBO5JC4pnomwvWNw9w
AAAEDAz//eOiJlVL7/gT4qpAfPhZkl5MoQZ0Ls3SNmBB+gG6nxhhr05/smEobvMf7FZ4Gi
8GcIE7kkLimeibC9Y3D3AAAADWdpdGh1Yi1kZXBsb3k=
-----END OPENSSH PRIVATE KEY-----
```

⚠️ **Importante**: Copia desde `-----BEGIN` hasta `-----END` (todo incluido)

---

## 🧪 Paso 3: Verificar Secrets

Después de agregar los 3 secrets, deberías ver:

```
Repository secrets
├─ SERVER_IP         (Updated now)
├─ SERVER_USER       (Updated now)
└─ SSH_PRIVATE_KEY   (Updated now)
```

---

## 🚀 Paso 4: Ejecutar Deploy de Nuevo

### Opción A: Push nuevo commit

```bash
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0
git add .
git commit -m "Fix: Configure GitHub secrets for deploy"
git push
```

### Opción B: Re-run el workflow fallido

1. Ve a: https://github.com/elemonkey/syncar/actions
2. Click en el workflow que falló
3. Click en **Re-run all jobs** (arriba a la derecha)

---

## ⏰ ¿Qué pasa después?

Una vez configurados los secrets, GitHub Actions podrá:

1. ✅ Conectarse al servidor vía SSH
2. ✅ Hacer `git pull` del código
3. ✅ Descargar las imágenes Docker
4. ✅ Reiniciar los servicios
5. ✅ Deploy completo automático

**Tiempo estimado:** ~5-10 minutos

---

## 🛑 IMPORTANTE: Primera vez en el servidor

⚠️ **Antes de que el deploy automático funcione**, debes configurar el servidor manualmente **UNA SOLA VEZ**:

```bash
# 1. Conectar al servidor
ssh root@45.14.194.85

# 2. Instalar Docker
curl -fsSL https://get.docker.com | sh

# 3. Instalar dependencias
apt update
apt install -y git docker-compose-plugin

# 4. Crear directorio y clonar
mkdir -p /opt/import-app
cd /opt/import-app
git clone https://github.com/elemonkey/syncar.git .

# 5. Configurar .env
cp .env.production.example .env
nano .env  # Editar con las claves secretas reales

# 6. Deploy inicial
chmod +x scripts/*.sh
./scripts/deploy.sh

# 7. Configurar SSL (opcional pero recomendado)
apt install certbot python3-certbot-nginx -y
certbot --nginx -d syncar.cl -d www.syncar.cl
```

---

## 📊 Verificar que todo funciona

### Después de configurar secrets:

```bash
# Ver el estado del workflow
# Ve a: https://github.com/elemonkey/syncar/actions

# Deberías ver:
✅ Test (3.11, 20) - passed
✅ Build and push - passed
✅ Deploy - passed (después de configurar secrets)
```

### Después del deploy en servidor:

```bash
ssh root@45.14.194.85
cd /opt/import-app
docker-compose -f docker-compose.prod.yml ps

# Deberías ver 8 contenedores corriendo:
# ├─ nginx
# ├─ frontend
# ├─ backend
# ├─ postgres
# ├─ redis
# ├─ celery-worker
# ├─ celery-beat
# └─ flower
```

---

## 🆘 Troubleshooting

### Error: "Permission denied (publickey)"

**Causa**: La clave SSH no es la correcta o no tiene permisos en el servidor.

**Solución**:
```bash
# 1. Verificar que la clave funciona desde tu Mac
ssh -i ~/.ssh/id_ed25519 root@45.14.194.85

# 2. Si funciona, la clave es correcta
# 3. Asegúrate de copiar TODO el contenido (incluyendo BEGIN y END)
```

### Error: "fatal: not a git repository"

**Causa**: El servidor no tiene el repositorio clonado en `/opt/import-app`.

**Solución**:
```bash
ssh root@45.14.194.85
mkdir -p /opt/import-app
cd /opt/import-app
git clone https://github.com/elemonkey/syncar.git .
```

### Error: "docker: command not found"

**Causa**: Docker no está instalado en el servidor.

**Solución**:
```bash
ssh root@45.14.194.85
curl -fsSL https://get.docker.com | sh
```

---

## 🔄 Flujo Normal (después del setup inicial)

```
1. Editas código en tu Mac
2. git add . && git commit -m "Mensaje" && git push
3. GitHub Actions se ejecuta automáticamente:
   ├─ Ejecuta tests
   ├─ Build imágenes Docker
   ├─ Push a GitHub Container Registry
   └─ Deploy al servidor (SSH)
4. Servidor actualiza automáticamente
5. ✅ Cambios en producción
```

**Tiempo total:** ~5-10 minutos desde el push

---

## 🎯 Siguiente Paso

1. **Configurar los 3 secrets** en: https://github.com/elemonkey/syncar/settings/secrets/actions
2. **Hacer push** de un nuevo commit o re-run del workflow
3. **Esperar** ~5 minutos
4. **Verificar** que el deploy funcione

---

## 📚 Documentación Relacionada

- **Setup completo del servidor**: `docs/DEPLOY_SERVIDOR.md`
- **Guía rápida de deploy**: `DEPLOY_RAPIDO.md`
- **Proceso de deploy**: `docs/DEPLOY_PROCESS.md`
- **Git workflow**: `docs/DEPLOY_GIT.md`

---

## ✅ Checklist Final

- [ ] Secret `SERVER_IP` configurado
- [ ] Secret `SERVER_USER` configurado
- [ ] Secret `SSH_PRIVATE_KEY` configurado (clave completa)
- [ ] Servidor tiene Docker instalado
- [ ] Servidor tiene Git instalado
- [ ] Repositorio clonado en `/opt/import-app`
- [ ] Archivo `.env` configurado en servidor
- [ ] Push nuevo commit o re-run workflow
- [ ] Deploy exitoso en GitHub Actions
- [ ] Aplicación accesible en https://syncar.cl

¡Listo para producción! 🚀
