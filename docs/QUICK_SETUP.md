# ⚡ SETUP RÁPIDO DEL SERVIDOR

## 🎯 Situación Actual

- ✅ Repositorio en GitHub: `elemonkey/syncar`
- ✅ Clave SSH disponible: `~/.ssh/id_ed25519`
- ❌ Servidor NO configurado aún
- ❌ GitHub Secrets NO configurados

---

## 🚀 PASO 1: Configurar Servidor (5 minutos)

### Opción A: Script Automático (Recomendado)

```bash
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0
./scripts/setup-server.sh
```

El script te pedirá:
1. **Contraseña del servidor** (para copiar la clave SSH)
2. Confirmación para continuar

**Luego hará automáticamente:**
- ✅ Copiar tu clave SSH al servidor
- ✅ Instalar Docker
- ✅ Instalar Git y dependencias
- ✅ Clonar el repositorio
- ✅ Configurar el ambiente

**Tiempo:** ~5 minutos

---

### Opción B: Manual (si el script falla)

```bash
# 1. Copiar clave SSH
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@45.14.194.85
# (Te pedirá la contraseña del servidor)

# 2. Conectar al servidor
ssh root@45.14.194.85

# 3. Instalar Docker
curl -fsSL https://get.docker.com | sh

# 4. Instalar dependencias
apt update
apt install -y git docker-compose-plugin

# 5. Clonar repositorio
mkdir -p /opt/import-app
cd /opt/import-app
git clone https://github.com/elemonkey/syncar.git .

# 6. Configurar .env
cp .env.production .env
nano .env  # Verificar que las claves secretas estén correctas

# 7. Permisos
chmod +x scripts/*.sh

# 8. Deploy inicial
./scripts/deploy.sh
```

---

## 🔐 PASO 2: Configurar GitHub Secrets (2 minutos)

### Ve a: https://github.com/elemonkey/syncar/settings/secrets/actions

Agrega estos 3 secrets:

#### 1. SERVER_IP
```
45.14.194.85
```

#### 2. SERVER_USER
```
root
```

#### 3. SSH_PRIVATE_KEY
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCp8YYa9Of7JhKG7zH+xWeBovBnCBO5JC4pnomwvWNw9wAAAJCgKBe/oCgX
vwAAAAtzc2gtZWQyNTUxOQAAACCp8YYa9Of7JhKG7zH+xWeBovBnCBO5JC4pnomwvWNw9w
AAAEDAz//eOiJlVL7/gT4qpAfPhZkl5MoQZ0Ls3SNmBB+gG6nxhhr05/smEobvMf7FZ4Gi
8GcIE7kkLimeibC9Y3D3AAAADWdpdGh1Yi1kZXBsb3k=
-----END OPENSSH PRIVATE KEY-----
```

⚠️ **Copia TODO** (desde BEGIN hasta END)

---

## 🎨 PASO 3: Deploy Inicial (10 minutos)

### Después de configurar el servidor:

```bash
ssh root@45.14.194.85
cd /opt/import-app
./scripts/deploy.sh
```

**Esto hará:**
- 🐳 Build de imágenes Docker
- 🚀 Iniciar 8 servicios
- 📊 Verificar que todo esté corriendo

**Tiempo:** ~10 minutos (la primera vez)

---

## 🔒 PASO 4: Configurar SSL (Opcional, 2 minutos)

```bash
ssh root@45.14.194.85
apt install certbot python3-certbot-nginx -y
certbot --nginx -d syncar.cl -d www.syncar.cl
```

---

## ✅ PASO 5: Verificar

### En el servidor:

```bash
ssh root@45.14.194.85
cd /opt/import-app
docker compose -f docker-compose.prod.yml ps
```

**Deberías ver 8 contenedores corriendo:**
```
✅ nginx
✅ frontend
✅ backend
✅ postgres
✅ redis
✅ celery-worker
✅ celery-beat
✅ flower
```

### En el navegador:

- **Frontend**: https://syncar.cl (o http://45.14.194.85)
- **API Docs**: https://syncar.cl/api/v1/docs
- **Health**: https://syncar.cl/api/v1/health

---

## 🔄 PASO 6: Probar CI/CD Automático

```bash
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0
echo "# Test deploy" >> README.md
git add .
git commit -m "Test: Deploy automático"
git push
```

**Ve a:** https://github.com/elemonkey/syncar/actions

**Deberías ver:**
```
✅ Test (3.11, 20)
✅ Build and push
✅ Deploy
```

**Tiempo:** ~5-10 minutos

---

## 🆘 Troubleshooting

### ❌ "Permission denied (publickey,password)"

**Causa**: La clave SSH no está en el servidor.

**Solución**:
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@45.14.194.85
```

### ❌ "docker: command not found"

**Causa**: Docker no instalado.

**Solución**:
```bash
ssh root@45.14.194.85
curl -fsSL https://get.docker.com | sh
```

### ❌ "fatal: not a git repository"

**Causa**: Repositorio no clonado.

**Solución**:
```bash
ssh root@45.14.194.85
mkdir -p /opt/import-app
cd /opt/import-app
git clone https://github.com/elemonkey/syncar.git .
```

### ❌ Deploy falla en GitHub Actions

**Causa**: Secrets no configurados.

**Solución**: Configurar los 3 secrets en:
https://github.com/elemonkey/syncar/settings/secrets/actions

---

## 📊 Checklist Completo

### Setup Inicial:
- [ ] Ejecutar `./scripts/setup-server.sh` O configurar manualmente
- [ ] Verificar conexión SSH sin contraseña
- [ ] Docker instalado en servidor
- [ ] Repositorio clonado en `/opt/import-app`
- [ ] Archivo `.env` configurado

### GitHub:
- [ ] Secret `SERVER_IP` agregado
- [ ] Secret `SERVER_USER` agregado
- [ ] Secret `SSH_PRIVATE_KEY` agregado

### Deploy:
- [ ] Deploy inicial ejecutado
- [ ] 8 contenedores corriendo
- [ ] Frontend accesible
- [ ] API respondiendo
- [ ] SSL configurado (opcional)

### CI/CD:
- [ ] Push de prueba funciona
- [ ] GitHub Actions pasa todos los tests
- [ ] Deploy automático funciona

---

## 🎯 Resumen Ultra-Rápido

```bash
# 1. Setup servidor (desde tu Mac)
./scripts/setup-server.sh

# 2. Deploy inicial (en el servidor)
ssh root@45.14.194.85
cd /opt/import-app
./scripts/deploy.sh

# 3. Configurar secrets en GitHub
# Ve a: https://github.com/elemonkey/syncar/settings/secrets/actions
# Agrega: SERVER_IP, SERVER_USER, SSH_PRIVATE_KEY

# 4. Probar
git push  # Esto debería triggear deploy automático

# 5. Verificar
curl https://syncar.cl/api/v1/health
```

**Tiempo total:** ~20 minutos

---

## 📚 Documentación Completa

- **Esta guía**: `docs/QUICK_SETUP.md`
- **GitHub Secrets**: `docs/GITHUB_SECRETS.md`
- **Deploy Servidor**: `docs/DEPLOY_SERVIDOR.md`
- **Deploy Rápido**: `DEPLOY_RAPIDO.md`
- **Git Workflow**: `docs/DEPLOY_GIT.md`

---

## 🚀 ¡Listo!

Ahora cada `git push` hará deploy automático en ~5 minutos. 🎉
