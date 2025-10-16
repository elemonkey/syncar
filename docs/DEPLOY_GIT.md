# 🚀 DEPLOY CON GIT - SYNCAR 2.0

Esta es la forma PROFESIONAL y RECOMENDADA de hacer deploy.

## ✅ Ventajas de usar Git:
- 📝 Control de versiones
- 🔄 Fácil actualizar en producción (`git pull`)
- 📊 Historial de cambios
- 🔒 Repositorio seguro (privado)
- 👥 Colaboración en equipo
- ⏮️ Rollback fácil si algo falla

---

## 📦 PREPARACIÓN (YA COMPLETADO)

✅ Git inicializado
✅ Primer commit creado
✅ 72 archivos incluidos

---

## 🔑 OPCIÓN 1: GitHub (Recomendado)

### Paso 1: Crear repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `syncar2.0`
3. **Importante**: Marca como **PRIVADO** 🔒
4. NO agregues README, .gitignore ni licencia (ya los tienes)
5. Clic en "Create repository"

### Paso 2: Conectar tu proyecto local con GitHub

```bash
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0

# Agregar el repositorio remoto (reemplaza con tu usuario)
git remote add origin https://github.com/TU_USUARIO/syncar2.0.git

# Subir el código
git push -u origin main
```

GitHub te pedirá autenticación. Opciones:
- **Personal Access Token** (recomendado)
- **SSH Key**

#### Crear Personal Access Token:
1. Ve a https://github.com/settings/tokens
2. Clic en "Generate new token" → "Classic"
3. Nombre: "SYNCAR Deploy"
4. Permisos: Marca `repo` (acceso completo al repositorio)
5. Clic en "Generate token"
6. **Copia el token** (no lo volverás a ver)

Al hacer `git push`, usa:
- **Usuario**: tu_usuario_github
- **Password**: el token que copiaste

### Paso 3: Deploy en el servidor

```bash
# Conectar al servidor
ssh root@45.14.194.85

# Instalar Docker (si no está)
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin git

# Clonar el repositorio
cd /opt
git clone https://github.com/TU_USUARIO/syncar2.0.git syncar
cd syncar

# Configurar y desplegar
cp .env.production .env
chmod +x scripts/*.sh
./scripts/deploy.sh

# SSL
apt install certbot python3-certbot-nginx -y
certbot --nginx -d syncar.cl -d www.syncar.cl
```

### Paso 4: Actualizar en el futuro (SUPER FÁCIL)

Cuando hagas cambios en tu Mac:

```bash
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0
git add .
git commit -m "Descripción de los cambios"
git push
```

En el servidor:

```bash
ssh root@45.14.194.85
cd /opt/syncar
git pull
./scripts/deploy.sh  # Redeploy con los cambios
```

---

## 🦊 OPCIÓN 2: GitLab (Alternativa)

### Paso 1: Crear repositorio en GitLab

1. Ve a https://gitlab.com/projects/new
2. Nombre: `syncar2.0`
3. Visibility: **Private** 🔒
4. Clic en "Create project"

### Paso 2: Conectar y subir

```bash
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0

# Agregar repositorio remoto
git remote add origin https://gitlab.com/TU_USUARIO/syncar2.0.git

# Subir código
git push -u origin main
```

### Paso 3: Deploy (igual que GitHub)

```bash
ssh root@45.14.194.85
cd /opt
git clone https://gitlab.com/TU_USUARIO/syncar2.0.git syncar
cd syncar
cp .env.production .env
chmod +x scripts/*.sh
./scripts/deploy.sh
```

---

## 🔐 CONFIGURAR SSH (Opcional, más seguro)

Si prefieres no usar tokens:

### Generar SSH Key:

```bash
ssh-keygen -t ed25519 -C "tu_email@ejemplo.com"
# Presiona Enter 3 veces (usa valores por defecto)

# Copiar la clave pública
cat ~/.ssh/id_ed25519.pub
```

### En GitHub/GitLab:
1. Ve a Settings → SSH Keys
2. Pega la clave
3. Guarda

### Cambiar URL del repositorio a SSH:

```bash
git remote set-url origin git@github.com:TU_USUARIO/syncar2.0.git
# O para GitLab:
git remote set-url origin git@gitlab.com:TU_USUARIO/syncar2.0.git
```

---

## 📋 COMANDOS GIT ÚTILES

```bash
# Ver estado de archivos
git status

# Ver historial de commits
git log --oneline

# Ver archivos que cambiaron
git diff

# Deshacer cambios locales
git checkout -- archivo.txt

# Ver repositorio remoto configurado
git remote -v

# Crear una nueva rama
git checkout -b feature/nueva-funcionalidad

# Volver a la rama main
git checkout main
```

---

## 🔄 FLUJO DE TRABAJO TÍPICO

### En tu Mac (desarrollo):

```bash
# 1. Hacer cambios en el código
# 2. Ver qué cambió
git status

# 3. Agregar cambios
git add .
# O agregar archivos específicos:
git add backend/app/main.py

# 4. Hacer commit
git commit -m "Feat: Agregar importador de productos"

# 5. Subir a GitHub/GitLab
git push
```

### En el servidor (producción):

```bash
# 1. Conectar
ssh root@45.14.194.85

# 2. Actualizar código
cd /opt/syncar
git pull

# 3. Redeploy
./scripts/deploy.sh

# 4. Verificar
docker compose -f docker-compose.prod.yml ps
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Error: "Git no está instalado en el servidor"
```bash
apt install git -y
```

### Error: "Permission denied (publickey)"
- Usa HTTPS en lugar de SSH
- O configura SSH keys correctamente

### Error: "Repository not found"
- Verifica que el repositorio sea público o tengas acceso
- Verifica la URL: `git remote -v`

### Conflictos al hacer `git pull`
```bash
# Opción 1: Forzar los cambios remotos (cuidado, pierdes cambios locales)
git fetch origin
git reset --hard origin/main

# Opción 2: Hacer backup y resolver manualmente
git stash
git pull
```

---

## 📊 COMPARACIÓN: GIT vs SCP

| Característica | Git (GitHub/GitLab) | SCP Directo |
|----------------|---------------------|-------------|
| **Setup inicial** | 5-10 minutos | 1 minuto |
| **Actualizaciones** | `git pull` (5 segundos) | Subir archivo completo |
| **Control de versiones** | ✅ Sí | ❌ No |
| **Rollback** | ✅ Fácil | ❌ Manual |
| **Colaboración** | ✅ Sí | ❌ No |
| **Profesional** | ✅✅✅ | ⚠️ Solo pruebas |
| **Recomendado para producción** | ✅ SÍ | ❌ NO |

---

## ✅ RESUMEN RÁPIDO

### Primera vez (GitHub):

```bash
# En tu Mac
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0
git remote add origin https://github.com/TU_USUARIO/syncar2.0.git
git push -u origin main

# En el servidor
ssh root@45.14.194.85
cd /opt
git clone https://github.com/TU_USUARIO/syncar2.0.git syncar
cd syncar
cp .env.production .env
chmod +x scripts/*.sh
./scripts/deploy.sh
```

### Actualizaciones futuras:

```bash
# Mac
git add . && git commit -m "Cambios" && git push

# Servidor
ssh root@45.14.194.85
cd /opt/syncar && git pull && ./scripts/deploy.sh
```

---

## 🎯 SIGUIENTE PASO

1. **Crea tu repositorio en GitHub** (https://github.com/new)
2. **Marca como PRIVADO** 🔒
3. **Ejecuta los comandos de arriba**
4. **¡Listo para producción!** 🚀

---

**¿Necesitas ayuda?** Revisa:
- Documentación de GitHub: https://docs.github.com
- Documentación de Git: https://git-scm.com/doc
