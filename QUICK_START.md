# 🚀 Inicio Rápido - Comandos Comunes

## 🔧 Desarrollo Local

### Iniciar servicios básicos (PostgreSQL + Redis)
```bash
make dev-up
```

### Iniciar Backend
```bash
make dev-backend
```

### Iniciar Frontend
```bash
make dev-frontend
```

## 🛠️ Comandos de Utilidad

### Limpiar caché de Next.js (cuando hay errores ENOENT)
```bash
make clean-frontend
```

O directamente:
```bash
./scripts/clean-frontend.sh
```

### Limpiar todos los volúmenes Docker
```bash
make clean
```

### Acceder a la base de datos
```bash
make shell-db
```

## 🐛 Solución de Problemas Comunes

### Error: ENOENT en Next.js
**Síntoma**: `Error: ENOENT: no such file or directory, open '.next/server/app/.../app-build-manifest.json'`

**Solución**:
```bash
make clean-frontend
```

### Backend no inicia
**Síntoma**: Error de conexión a PostgreSQL

**Solución**:
```bash
# Verificar que Docker esté corriendo
make dev-up

# Reiniciar backend
make dev-backend
```

### Frontend no compila
**Síntoma**: Errores de módulos no encontrados o caché corrupto

**Solución**:
```bash
# Limpiar caché y reinstalar
cd frontend
rm -rf .next node_modules package-lock.json
npm install
npm run dev
```

### Puerto 3000 ocupado
**Síntoma**: `Error: listen EADDRINUSE: address already in use :::3000`

**Solución**:
```bash
lsof -ti:3000 | xargs kill -9
make dev-frontend
```

### Puerto 8000 ocupado
**Síntoma**: Backend no puede iniciar en puerto 8000

**Solución**:
```bash
lsof -ti:8000 | xargs kill -9
make dev-backend
```

## 📋 Comandos del Makefile

Ver todos los comandos disponibles:
```bash
make help
```

Salida:
```
📋 Comandos disponibles:

🔧 DESARROLLO LOCAL:
  make dev-up          - Levantar PostgreSQL y Redis (Docker)
  make dev-down        - Apagar servicios de desarrollo
  make dev-backend     - Ejecutar backend (nativo)
  make dev-celery      - Ejecutar Celery worker (nativo)
  make dev-frontend    - Ejecutar frontend (nativo)

🚀 PRODUCCIÓN:
  make prod-build      - Construir imágenes Docker
  make prod-up         - Levantar todos los servicios
  make prod-down       - Apagar todos los servicios
  make prod-logs       - Ver logs en tiempo real

🧪 TESTING:
  make test-local      - Ejecutar tests localmente

🛠️ UTILIDADES:
  make shell-db        - Abrir shell de PostgreSQL
  make clean           - Limpiar volúmenes y caché
  make clean-frontend  - Limpiar caché de Next.js y reiniciar
```

## 🔄 Flujo de Trabajo Típico

### Inicio del día
```bash
# 1. Levantar servicios Docker
make dev-up

# 2. En una terminal: Backend
make dev-backend

# 3. En otra terminal: Frontend
make dev-frontend
```

### Durante el desarrollo
```bash
# Si hay errores en Next.js
make clean-frontend

# Si necesitas ver la base de datos
make shell-db

# Si necesitas reiniciar todo
make dev-down
make clean
make dev-up
```

### Final del día
```bash
# Apagar servicios Docker
make dev-down
```

## 🌐 URLs Importantes

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

## 🔐 Credenciales por defecto

### Usuario Administrador
- **Username**: `admin`
- **Password**: `admin123`

### Base de Datos
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `importapp_db`
- **User**: `admin`
- **Password**: `password`

### Redis
- **Host**: `localhost`
- **Port**: `6379`

## 📦 Instalación Inicial (Primera vez)

```bash
# Instalar dependencias
make install

# O por separado:
make install-backend
make install-frontend

# Levantar servicios
make dev-up

# Aplicar migraciones
cd backend
source venv/bin/activate
alembic upgrade head

# Crear usuario admin
python -m app.scripts.init_users

# Iniciar desarrollo
make dev-backend  # Terminal 1
make dev-frontend # Terminal 2
```

## 🎯 Scripts Útiles

### Backend
```bash
# Activar entorno virtual
cd backend
source venv/bin/activate

# Aplicar migraciones
alembic upgrade head

# Crear nueva migración
alembic revision --autogenerate -m "descripcion"

# Ejecutar tests
pytest -v

# Ver usuarios en la BD
python -c "from app.core.database import SessionLocal; from app.models import User; db = SessionLocal(); print([u.username for u in db.query(User).all()])"
```

### Frontend
```bash
# Limpiar caché
rm -rf .next

# Build de producción
npm run build

# Ver análisis del bundle
npm run build -- --analyze

# Verificar tipos
npm run type-check
```

## 💡 Tips

1. **Siempre usa `make dev-up` antes de iniciar** - asegura que PostgreSQL y Redis estén corriendo
2. **Si algo no funciona, limpia el caché** - `make clean-frontend`
3. **Usa el Makefile** - simplifica los comandos complejos
4. **Lee los logs** - ayudan a identificar problemas rápidamente
5. **Documenta cambios** - mantén el README actualizado

## 📚 Más Información

- [README.md](../README.md) - Documentación completa
- [DEPLOY_AHORA.md](../DEPLOY_AHORA.md) - Guía de deployment
- [docs/](../docs/) - Documentación técnica
