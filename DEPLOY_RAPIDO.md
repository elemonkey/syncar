# 🚀 DEPLOY RÁPIDO - SYNCAR 2.0

## 📦 Archivo preparado: `syncar2.0-deploy.tar.gz`

---

## PASO 1: Subir al servidor (desde tu Mac)

```bash
scp /Users/maxberrios/Desktop/REPUESTOS/syncar2.0-deploy.tar.gz root@45.14.194.85:/opt/
```

---

## PASO 2: Conectar al servidor

```bash
ssh root@45.14.194.85
```

---

## PASO 3: Ejecutar deploy automático

```bash
cd /opt
chmod +x syncar2.0-deploy/scripts/server-deploy.sh
./syncar2.0-deploy/scripts/server-deploy.sh
```

**O ejecuta paso a paso:**

```bash
# Instalar Docker (si no está)
curl -fsSL https://get.docker.com | sh
apt install -y docker-compose-plugin certbot python3-certbot-nginx

# Descomprimir
cd /opt
tar -xzf syncar2.0-deploy.tar.gz
cd SYNCAR2.0  # o 'syncar'

# Configurar
cp .env.production .env
chmod +x scripts/*.sh

# Deploy
./scripts/deploy.sh

# SSL (HTTPS)
certbot --nginx -d syncar.cl -d www.syncar.cl
```

---

## ✅ Verificación

```bash
# Ver servicios
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🌐 Acceder a la aplicación

- **Frontend**: https://syncar.cl
- **Importadores**: https://syncar.cl/importers
- **API Docs**: https://syncar.cl/api/docs
- **Flower** (Monitor): https://syncar.cl:5555

---

## 📝 Comandos útiles

```bash
# Reiniciar servicios
docker compose -f docker-compose.prod.yml restart

# Detener servicios
docker compose -f docker-compose.prod.yml down

# Ver logs de un servicio específico
docker logs importapp-backend -f

# Acceder a la base de datos
docker exec -it importapp-postgres psql -U elemonkey -d syncar_db
```

---

## 🔄 Importar categorías de Noriega

Una vez desplegado, ve a https://syncar.cl/importers y:
1. Selecciona NORIEGA
2. Haz clic en "Importar Categorías"
3. Espera a que se importen las 73 categorías

---

## 🆘 Problemas?

Revisa la documentación completa en:
- `docs/DEPLOY_SERVIDOR.md` - Guía detallada
- `docs/DEPLOY.md` - Documentación técnica
- `docs/DEPLOY_RESUMEN.md` - Resumen ejecutivo

---

**Tiempo estimado: 15-20 minutos**

¡Buena suerte con el deploy! 🚀
