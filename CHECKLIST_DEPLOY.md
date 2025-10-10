# Checklist Automatizado de Deploy y Cambios Syncar

## 1. Validación de configuración
- [ ] Comparar `.env` local vs producción (variables, credenciales, claves secretas)
- [ ] Comparar `docker-compose.yml` local vs producción (servicios, volúmenes, puertos)
- [ ] Comparar `nginx.conf` local vs producción (rutas, dominios, certificados)
- [ ] Validar que los secrets en GitHub Actions coincidan con los valores de producción

## 2. Migraciones y base de datos
- [ ] Verificar que los volúmenes de Postgres estén configurados para persistencia
- [ ] Ejecutar y validar migraciones Alembic en ambos entornos
- [ ] Confirmar que las tablas y datos críticos existen en la base de datos

## 3. Pruebas y endpoints
- [ ] Ejecutar tests automáticos antes de cada deploy
- [ ] Probar endpoints críticos (`/api/v1/health`, `/api/v1/importer-configs`, `/api/v1/categories/...`)
- [ ] Revisar logs de backend y celery_worker post-deploy

## 4. Seguridad y secrets
- [ ] Validar que el `SECRET_KEY` sea seguro y diferente en producción
- [ ] Mantener credenciales sensibles fuera del `.env` público
- [ ] Usar GitHub Actions secrets para credenciales de importadores

## 5. Documentación y rollback
- [ ] Documentar cada cambio relevante en el README
- [ ] Mantener scripts de backup y restauración de base de datos
- [ ] Tener un procedimiento de rollback ante fallos

## 6. Automatización y monitoreo
- [ ] Automatizar la comparación de archivos clave antes de cada deploy
- [ ] Automatizar la verificación de migraciones Alembic
- [ ] Configurar alertas básicas de monitoreo (errores 500, caídas de servicios)

---

> **Recomendación:** Usa este checklist antes de cada cambio o deploy para evitar caídas y asegurar consistencia entre local y producción.
