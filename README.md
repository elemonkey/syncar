# 🚀 Import App - Plataforma de Importación de Datos

Plataforma centralizada para automatizar la extracción de datos de múltiples proveedores (Alsacia, Refax, Noriega, Emasa) con una arquitectura modular, robusta y escalable.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Stack Tecnológico](#stack-tecnológico)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Desarrollo Local](#desarrollo-local)
- [Deploy a Producción](#deploy-a-producción)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)

## ✨ Características

### Core
- 🕷️ **Scraping robusto** con Playwright y httpx
- ⚡ **Tareas asíncronas** con Celery
- 📊 **Progress tracking** en tiempo real con Server-Sent Events
- 🔄 **Arquitectura modular** por componentes (Auth, Categories, Products, Config)
- 💾 **Base de datos PostgreSQL** con SQLAlchemy async
- 🎨 **UI moderna** con Next.js 14, Tailwind CSS y shadcn/ui

### Funcionalidades
- 📂 **Importación de categorías** desde cada proveedor
- 🛍️ **Importación de productos** con configuración personalizada
- ⚙️ **Configuración por importador** (límites, velocidad, orden)
- 📈 **Dashboard** con KPIs y gráficos
- 🔍 **Catálogo** con búsqueda avanzada y filtros
- 📊 **Reportes** y exportación a CSV/Excel
- 👥 **Sistema de usuarios** con autenticación JWT

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** 0.110+ (Python 3.11)
- **PostgreSQL** 16
- **SQLAlchemy** 2.0 (async)
- **Alembic** (migraciones)
- **Celery** 5.3 + Redis (task queue)
- **Flower** (monitoring Celery)
- **Playwright** 1.41 (browser automation)
- **httpx** (HTTP async client)

### Frontend
- **Next.js** 14 (App Router)
- **TypeScript** 5.3
- **Tailwind CSS** v4
- **shadcn/ui** + Radix UI
- **Framer Motion** (animaciones)
- **TanStack Query** v5
- **Sonner** (toasts)

### DevOps
- **Docker** + Docker Compose
- **GitHub Actions** (CI/CD)
- **Nginx** (reverse proxy)

## 🏗️ Arquitectura

### Flujo de Importación de Categorías
```
1. Usuario → Click "Importar Categorías"
2. Frontend → POST /api/v1/importers/{name}/import-categories
3. Backend → Celery task (import_categories_task)
4. AuthComponent → Login en proveedor
5. CategoriesComponent → Scraping de categorías
6. Guardar en DB → Actualizar UI
```

### Flujo de Importación de Productos
```
1. Usuario → Selecciona categorías → Click "Importar Productos"
2. Frontend → POST /api/v1/importers/{name}/import-products
3. Backend → Celery task (import_products_task)
4. AuthComponent → Login
5. ConfigComponent → Leer configuración
6. ProductsComponent → Scraping de productos (respetando config)
7. Guardar en DB → Actualizar progreso en tiempo real
```

### Componentes Modulares
Cada importador tiene 4 componentes independientes:
- **AuthComponent**: Autenticación en el sitio
- **CategoriesComponent**: Extracción de categorías
- **ConfigComponent**: Lectura de configuración
- **ProductsComponent**: Extracción de productos

## 📦 Instalación

### Requisitos Previos
- Python 3.11+
- Node.js 20+
- Docker y Docker Compose
- Git

### Setup Rápido

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/import-app.git
cd import-app

# 2. Copiar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 3. Instalar dependencias
make install

# O manualmente:
# Backend
cd backend
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
playwright install chromium

# Frontend
cd frontend
npm install
```

## 🚀 Desarrollo Local

### Enfoque Híbrido (Recomendado)
- PostgreSQL y Redis en Docker
- Backend, Frontend y Celery nativos (más rápido)

```bash
# 1. Levantar servicios de infraestructura (PostgreSQL + Redis)
make dev-up

# 2. En terminal 1: Backend
make dev-backend
# → http://localhost:8000
# → API Docs: http://localhost:8000/docs

# 3. En terminal 2: Celery Worker
make dev-celery

# 4. En terminal 3: Frontend
make dev-frontend
# → http://localhost:3000

# 5. (Opcional) Flower para monitorear Celery
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app flower
# → http://localhost:5555
```

### Comandos Útiles

```bash
# Ver base de datos
make shell-db

# Ejecutar tests
make test-local

# Apagar servicios
make dev-down

# Limpiar todo
make clean
```

## 🚢 Deploy a Producción

### Configuración del Servidor

```bash
# En el servidor (SSH)
# 1. Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Clonar repositorio
cd /opt
git clone https://github.com/tu-usuario/import-app.git
cd import-app

# 3. Configurar variables de entorno
cp .env.example .env.prod
nano .env.prod  # Editar con valores de producción

# 4. Construir y levantar servicios
make prod-build
make prod-up

# 5. Ver logs
make prod-logs
```

### Deploy Automático con GitHub Actions

El proyecto incluye CI/CD configurado:

1. **Push a `main`** → GitHub Actions se ejecuta
2. **Tests** → Lint y pruebas de backend/frontend
3. **Build** → Construye imágenes Docker y las sube a GitHub Container Registry
4. **Deploy** → SSH al servidor y actualiza servicios

**Configurar secrets en GitHub:**
- `SERVER_IP`: IP del servidor (45.14.194.85)
- `SERVER_USER`: Usuario SSH
- `SSH_PRIVATE_KEY`: Clave privada SSH

## 📖 Uso

### 1. Importar Categorías

```bash
# UI: Página Importadores → Tab "Alsacia" → Botón "Importar Categorías"

# API:
POST /api/v1/importers/alsacia/import-categories
```

### 2. Importar Productos

```bash
# UI:
# 1. Seleccionar categorías con checkbox
# 2. Click "Importar Productos"

# API:
POST /api/v1/importers/alsacia/import-products
Body: {
  "selected_categories": ["Frenos", "Motor"]
}
```

### 3. Ver Progreso

El modal de progreso se actualiza en tiempo real vía SSE:
```
GET /api/v1/jobs/{job_id}/stream
```

### 4. Configurar Importador

```bash
# UI: Página Configuración → Tab "Alsacia"
# - Productos por categoría
# - Velocidad de scraping
# - Orden de categorías
```

## 📁 Estructura del Proyecto

```
import-app/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # Endpoints FastAPI
│   │   ├── core/             # Config, DB, Logger, Security
│   │   ├── models/           # Modelos SQLAlchemy
│   │   ├── importers/        # Componentes de importación
│   │   │   ├── base.py       # Clases base
│   │   │   ├── orchestrator.py
│   │   │   ├── alsacia/
│   │   │   ├── refax/
│   │   │   ├── noriega/
│   │   │   └── emasa/
│   │   ├── tasks/            # Tareas de Celery
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── scripts/          # Scripts de utilidad
│   │   └── main.py           # Aplicación FastAPI
│   ├── alembic/              # Migraciones de DB
│   ├── tests/                # Tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                  # Pages (App Router)
│   ├── components/           # Componentes React
│   ├── lib/                  # Utilidades
│   ├── package.json
│   └── Dockerfile
├── nginx/
│   └── nginx.conf            # Configuración Nginx
├── .github/workflows/
│   └── deploy.yml            # CI/CD
├── docker-compose.dev.yml    # Dev (solo infra)
├── docker-compose.prod.yml   # Producción (completo)
├── Makefile                  # Comandos útiles
├── .env.example
└── README.md
```

## 🔧 Configuración de Importadores

Edita `/backend/app/importers/{nombre}/` para implementar la lógica de scraping:

```python
# Ejemplo: alsacia/auth.py
class AlsaciaAuthComponent(AuthComponent):
    async def execute(self):
        # 1. Navegar a página de login
        # 2. Llenar formulario
        # 3. Hacer click en submit
        # 4. Guardar session
        # 5. Return session_data
        pass
```

## � Deploy a Producción

SYNCAR 2.0 está completamente preparado para deploy en producción con Docker Compose.

### 📚 Documentación Completa

- 📖 [Guía de Deploy Completa](docs/DEPLOY.md) - Instrucciones paso a paso
- 📊 [Proceso de Deploy](docs/DEPLOY_PROCESS.md) - Arquitectura y checklist detallado

### ⚡ Quick Deploy

#### 1. Deploy Local (Testing)
```bash
# Probar entorno de producción localmente
./scripts/deploy-local.sh

# Acceder
open http://localhost
```

#### 2. Deploy en Servidor

```bash
# 1. Configurar variables de entorno
cp .env.production.example .env
nano .env  # Editar con tus valores reales

# 2. Ejecutar deploy
./scripts/deploy.sh

# 3. Verificar servicios
docker-compose -f docker-compose.prod.yml ps
```

### 📦 Scripts Disponibles

```bash
./scripts/deploy.sh          # Deploy completo a producción
./scripts/deploy-local.sh    # Deploy local para testing
./scripts/backup.sh          # Backup de base de datos
./scripts/restore.sh <file>  # Restaurar backup
```

### 🌐 Servicios en Producción

Después del deploy exitoso:

- **Frontend**: https://tu-dominio.com
- **Backend API**: https://tu-dominio.com/api
- **API Docs**: https://tu-dominio.com/api/docs
- **Flower (Celery Monitor)**: https://tu-dominio.com:5555

### 🏗️ Arquitectura de Producción

```
Internet → Nginx (SSL/Proxy) → Frontend (Next.js) ↔ Backend (FastAPI)
                                                         ↓
                                        PostgreSQL + Redis + Celery Workers
```

### ✅ Checklist de Deploy

- [ ] Servidor configurado (Ubuntu/Debian)
- [ ] Docker y Docker Compose instalados
- [ ] Dominio DNS apuntando al servidor
- [ ] Archivo `.env` configurado con valores reales
- [ ] SSL/HTTPS configurado (certbot)
- [ ] Firewall configurado (puertos 22, 80, 443)
- [ ] Backups automáticos configurados

### 📊 Estado Actual del Proyecto

**✅ Fase 1-2 Completada:**
- Infraestructura base con Docker
- Sistema de importación con Playwright + WebKit
- Extracción de 73 categorías de Noriega
- Almacenamiento en PostgreSQL
- Visualización en frontend
- Sistema de deploy completo

**🔄 Próxima Fase:**
- Extracción de productos
- Importadores adicionales
- Sincronización automática

## �🐛 Troubleshooting

### Error: "Playwright not found"
```bash
cd backend
source venv/bin/activate
playwright install chromium
```

### Error: "Cannot connect to database"
```bash
# Verificar que PostgreSQL está corriendo
make dev-up
docker ps
```

### Error: "Celery worker not processing tasks"
```bash
# Verificar que Redis está corriendo
docker logs importapp-redis-dev

# Verificar que Celery está activo
cd backend
source venv/bin/activate
celery -A app.tasks.celery_app status
```

## 📝 Licencia

Este proyecto es privado y propietario.

## 👥 Contacto

Para preguntas o soporte, contacta al equipo de desarrollo.

---

**⚡ Hecho con FastAPI, Next.js y mucho ☕**
