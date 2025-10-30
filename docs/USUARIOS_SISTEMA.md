# Sistema de Gestión de Usuarios - SYNCAR 2.0

## ✅ Estado Actual

El sistema de autenticación y gestión de usuarios está completamente funcional.

## 👥 Perfiles de Usuario

El sistema cuenta con 3 perfiles (roles) configurados:

### 1. Super Admin
- **Descripción**: Acceso total al sistema con privilegios especiales
- **Permisos**: Catálogo, Importadores, Configuración
- **Características**: Es superusuario, puede crear otros superusuarios
- **Color badge**: Morado

### 2. Admin
- **Descripción**: Acceso completo a todas las funcionalidades
- **Permisos**: Catálogo, Importadores, Configuración
- **Características**: Administrador regular
- **Color badge**: Azul

### 3. Viewer
- **Descripción**: Acceso solo para visualizar el catálogo de productos
- **Permisos**: Solo Catálogo
- **Características**: Usuario de solo lectura
- **Color badge**: Verde

## 🔐 Usuarios Creados

### Usuario Principal
```
Usuario: admin
Password: admin123
Email: admin@syncar.cl
Rol: Super Admin
Tipo: Superusuario
```

### Usuarios de Prueba

```
Usuario: superadmin
Password: super123
Email: superadmin@syncar.cl
Rol: Super Admin
Tipo: Superusuario
```

```
Usuario: admin1
Password: admin123
Email: admin1@syncar.cl
Rol: Admin
Tipo: Usuario regular
```

```
Usuario: viewer1
Password: viewer123
Email: viewer1@syncar.cl
Rol: Viewer
Tipo: Usuario regular
```

## 📋 Funcionalidades Implementadas

### Backend ✅
- ✅ Modelos de User, Role, Permission
- ✅ Endpoints de autenticación (/auth/login, /auth/token)
- ✅ Endpoints de gestión de usuarios (GET, POST, PUT, DELETE)
- ✅ Endpoints de gestión de roles (GET, POST, PUT, DELETE)
- ✅ Validación de permisos y superusuarios
- ✅ Carga eager de relaciones (selectinload) para evitar errores async
- ✅ Migración de base de datos aplicada

### Frontend ✅
- ✅ AuthContext con localStorage
- ✅ Página de login (/)
- ✅ Dashboard después del login
- ✅ Navegación con logout
- ✅ Página de configuración con tabs
  - Tab "Usuarios": Link a gestión de usuarios
  - Tab "Importadores": Configuración de credenciales
- ✅ Página de gestión de usuarios (/configuracion/usuarios)
  - Lista completa de usuarios
  - Crear nuevo usuario
  - Editar usuario existente
  - Eliminar usuario
  - Asignar roles
  - Toggle activo/inactivo
  - Toggle superusuario
- ✅ Badges de roles con colores distintivos

## 🚀 Cómo Usar

### 1. Iniciar sesión
1. Ir a `http://localhost:3000`
2. Usar cualquiera de las credenciales de arriba
3. Click en "Iniciar Sesión"

### 2. Gestionar Usuarios
1. Click en "Configuración" en la navegación
2. Click en tab "Usuarios"
3. Click en "Gestión de Usuarios"
4. Ahora puedes:
   - Ver lista de todos los usuarios
   - Crear nuevos usuarios con el botón "Nuevo Usuario"
   - Editar usuarios existentes (ícono lápiz)
   - Eliminar usuarios (ícono basura)
   - Asignar roles desde el dropdown
   - Marcar como activo/inactivo
   - Marcar como superusuario

### 3. Configurar Importadores
1. Click en "Configuración" en la navegación
2. Click en tab "Importadores"
3. Configurar credenciales para cada importador:
   - Noriega (azul)
   - Alsacia (verde)
   - Refax (morado)
   - Emasa (naranja)
4. Click en "Guardar Configuración"

## 🔧 Scripts Útiles

### Actualizar roles existentes
```bash
cd backend
source venv/bin/activate
PYTHONPATH=/Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0/backend python app/scripts/update_roles.py
```

### Crear usuarios de prueba
```bash
cd backend
source venv/bin/activate
PYTHONPATH=/Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0/backend python app/scripts/create_test_users.py
```

### Inicializar roles y admin (primera vez)
```bash
cd backend
source venv/bin/activate
PYTHONPATH=/Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0/backend python app/scripts/init_users.py
```

### Listar usuarios
```bash
cd backend
source venv/bin/activate
PYTHONPATH=/Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0/backend python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models import User, Role
from sqlalchemy import select
from sqlalchemy.orm import joinedload

async def list_users():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).options(joinedload(User.role)))
        users = result.unique().scalars().all()
        for user in users:
            print(f'{user.username}: {user.role.name if user.role else \"Sin rol\"}')

asyncio.run(list_users())
"
```

## 📊 Estructura de Base de Datos

### Tabla: users
- id (PK)
- username (unique)
- email (unique)
- hashed_password
- full_name
- is_active
- is_superuser
- role_id (FK → roles.id)
- created_at
- updated_at

### Tabla: roles
- id (PK)
- name (unique)
- description
- is_active
- created_at
- updated_at

### Tabla: permissions
- id (PK)
- role_id (FK → roles.id)
- page_name (catalogo, importers, configuracion)
- can_access (boolean)
- created_at

## 🎯 Próximos Pasos

1. **Proteger rutas del frontend**: Agregar verificación de autenticación en todas las páginas
2. **Role Management UI**: Crear página para gestionar roles y permisos
3. **Filtrado de navegación**: Mostrar/ocultar items según permisos del usuario
4. **Cambiar contraseña por defecto**: En producción, cambiar admin123 por una segura

## ⚠️ Seguridad

- Las contraseñas se hashean con bcrypt
- Los tokens JWT expiran después de 30 días
- Solo superusuarios pueden crear otros superusuarios
- Los usuarios solo pueden editar su propio perfil (excepto superusuarios)

## 🐛 Troubleshooting

### Error: "Could not validate credentials"
- Verificar que el backend está corriendo
- Verificar que el token no ha expirado
- Hacer logout y login nuevamente

### Los usuarios no aparecen en la lista
- Verificar que el backend está corriendo
- Verificar la conexión a la base de datos
- Revisar la consola del navegador para errores

### Error al crear usuario
- Verificar que username y email son únicos
- Verificar que el rol existe
- Verificar que tienes permisos (debes estar autenticado)
