# 🚀 SYNCAR 2.0 - Proceso de Deploy

## 📊 Arquitectura de Producción

```
                                   Internet
                                      |
                                   [Nginx]
                                  (Port 80/443)
                                      |
                    +-----------------+-----------------+
                    |                                   |
              [Frontend]                           [Backend API]
            (Next.js 14)                          (FastAPI)
              Port 3000                            Port 8000
                    |                                   |
                    +----------------+------------------+
                                     |
                    +----------------+-----------------+
                    |                |                 |
              [PostgreSQL]       [Redis]        [Celery Workers]
               Port 5432        Port 6379           (2x)
                    |                |                 |
              [Volumen de       [Volumen de     [Procesamiento]
               Datos]            Cache]          [Background]
```

## 🎯 Servicios Desplegados

### 1. **Nginx** (Reverse Proxy)
- ✅ Maneja todas las peticiones HTTP/HTTPS
- ✅ Sirve frontend en `/`
- ✅ Proxy a backend API en `/api/`
- ✅ SSL/TLS termination
- ✅ Rate limiting y seguridad
- ✅ Cache de assets estáticos
- **Puerto**: 80 (HTTP), 443 (HTTPS)

### 2. **Frontend** (Next.js)
- ✅ Aplicación React con Server-Side Rendering
- ✅ UI moderna y responsive
- ✅ Optimización automática de imágenes
- ✅ Hot reload en desarrollo
- **Puerto interno**: 3000

### 3. **Backend** (FastAPI)
- ✅ API REST con documentación automática
- ✅ Endpoints de importación (dev/prod)
- ✅ Sistema de autenticación JWT
- ✅ WebSocket para actualizaciones en tiempo real
- **Puerto interno**: 8000

### 4. **PostgreSQL**
- ✅ Base de datos relacional
- ✅ Volumen persistente para datos
- ✅ Backups automáticos diarios
- ✅ Health checks integrados
- **Puerto interno**: 5432

### 5. **Redis**
- ✅ Cache de sesiones y datos
- ✅ Message broker para Celery
- ✅ Volumen persistente (AOF)
- **Puerto interno**: 6379

### 6. **Celery Workers** (2 instancias)
- ✅ Procesamiento asíncrono de tareas
- ✅ Scraping de sitios en background
- ✅ Auto-scaling según carga
- ✅ Reinicio automático en caso de error

### 7. **Celery Beat**
- ✅ Scheduler para tareas programadas
- ✅ Sincronizaciones automáticas
- ✅ Limpieza de datos antiguos

### 8. **Flower** (Monitor de Celery)
- ✅ Dashboard web para monitoreo
- ✅ Estadísticas en tiempo real
- ✅ Gestión de workers
- **Puerto**: 5555

---

## 📝 Checklist de Deploy

### Pre-Deploy
- [ ] Servidor configurado (Ubuntu/Debian)
- [ ] Docker y Docker Compose instalados
- [ ] Dominio DNS apuntando al servidor
- [ ] Firewall configurado (puertos 22, 80, 443)
- [ ] Usuario no-root con acceso sudo

### Configuración
- [ ] Archivo `.env` creado y configurado
- [ ] Variables de entorno verificadas
- [ ] Claves secretas generadas (SECRET_KEY, JWT_SECRET_KEY)
- [ ] Dominio configurado en nginx.conf
- [ ] SSL/HTTPS configurado (certbot)

### Deploy
- [ ] Código clonado en `/opt/syncar2.0`
- [ ] Scripts de deploy con permisos ejecutables
- [ ] `./scripts/deploy.sh` ejecutado exitosamente
- [ ] Todos los contenedores corriendo (`docker ps`)
- [ ] Migraciones de BD aplicadas

### Verificación
- [ ] Frontend accesible en https://tu-dominio.com
- [ ] Backend API accesible en https://tu-dominio.com/api
- [ ] API Docs en https://tu-dominio.com/api/docs
- [ ] Flower accesible en https://tu-dominio.com:5555
- [ ] Logs sin errores críticos
- [ ] Health checks pasando

### Post-Deploy
- [ ] Backup automático configurado (cron)
- [ ] Monitoreo configurado (logs, alertas)
- [ ] Documentación actualizada
- [ ] Equipo notificado del deploy
- [ ] Test de funcionalidades críticas

---

## 🔄 Flujo de Deploy

```
┌─────────────────────────────────────────────────────────┐
│  1. PREPARACIÓN                                         │
│  - Crear backup de BD actual                            │
│  - Detener servicios antiguos                           │
│  - Limpiar imágenes Docker antiguas (opcional)          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  2. BUILD                                               │
│  - Construir imagen de Backend (Python + Playwright)    │
│  - Construir imagen de Frontend (Next.js)               │
│  - Validar configuraciones                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  3. DEPLOY                                              │
│  - Levantar PostgreSQL y Redis                          │
│  - Esperar health checks                                │
│  - Levantar Backend                                     │
│  - Levantar Celery Workers y Beat                       │
│  - Levantar Frontend                                    │
│  - Levantar Nginx                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  4. MIGRACIÓN DE BD                                     │
│  - Ejecutar alembic upgrade head                        │
│  - Verificar integridad de datos                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  5. VERIFICACIÓN                                        │
│  - Verificar todos los servicios corriendo              │
│  - Probar endpoints críticos                            │
│  - Revisar logs de errores                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  6. MONITOREO                                           │
│  - Observar logs en tiempo real                         │
│  - Verificar uso de recursos                            │
│  - Confirmar funcionalidad completa                     │
└─────────────────────────────────────────────────────────┘
```

---

## ⏱️ Tiempos Estimados

| Fase | Tiempo Estimado |
|------|-----------------|
| Preparación de servidor | 30-60 min |
| Instalación de Docker | 10-15 min |
| Configuración de variables | 15-30 min |
| First deploy (build) | 10-20 min |
| Configuración SSL | 10-15 min |
| Configuración de backups | 5-10 min |
| Testing y verificación | 15-30 min |
| **TOTAL** | **~2-3 horas** |

Deploys subsecuentes: **~5-10 minutos**

---

## 🎯 Comandos Quick Reference

### Deploy
```bash
./scripts/deploy.sh
```

### Verificar estado
```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

### Backup manual
```bash
./scripts/backup.sh
```

### Restaurar backup
```bash
./scripts/restore.sh backups/syncar_backup_YYYYMMDD_HHMMSS.sql.gz
```

### Ver logs de un servicio
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f celery-worker
```

### Reiniciar un servicio
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### Acceder a un contenedor
```bash
docker exec -it importapp-backend bash
docker exec -it importapp-postgres psql -U syncar_user -d syncar_prod
```

---

## 🆘 Rollback en caso de problemas

Si algo sale mal durante el deploy:

```bash
# 1. Detener servicios nuevos
docker-compose -f docker-compose.prod.yml down

# 2. Restaurar backup anterior
./scripts/restore.sh backups/backup_ANTES_DEL_DEPLOY.sql.gz

# 3. Volver a versión anterior del código
git checkout COMMIT_ANTERIOR

# 4. Re-deploy versión anterior
./scripts/deploy.sh
```

---

## 📊 Recursos Recomendados por Escala

### Startup / Testing (hasta 100 usuarios)
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disco**: 50GB
- **Costo**: ~$20-40/mes (DigitalOcean, Linode)

### Producción Pequeña (100-1000 usuarios)
- **CPU**: 4 cores
- **RAM**: 8GB
- **Disco**: 100GB SSD
- **Costo**: ~$40-80/mes

### Producción Media (1000-10000 usuarios)
- **CPU**: 8 cores
- **RAM**: 16GB
- **Disco**: 200GB SSD
- **Costo**: ~$100-200/mes

### Producción Grande (10000+ usuarios)
- **Arquitectura**: Multi-server, Load Balancer
- **DB**: PostgreSQL dedicado + réplicas
- **Cache**: Redis Cluster
- **CDN**: CloudFlare / AWS CloudFront
- **Costo**: $500+/mes

---

## ✅ Deploy Exitoso - Próximos Pasos

Una vez desplegado exitosamente:

1. **Monitoreo**: Configurar alertas (Sentry, UptimeRobot)
2. **Analytics**: Integrar Google Analytics o similar
3. **SEO**: Configurar meta tags y sitemap
4. **Performance**: Optimizar queries lentas
5. **Seguridad**: Auditoría de seguridad
6. **Documentación**: Mantener docs actualizadas

---

**¡SYNCAR 2.0 listo para producción! 🚀**
