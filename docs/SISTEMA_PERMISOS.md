# 🔐 Sistema de Roles y Permisos - Documentación Completa

**Fecha de implementación**: 29 de octubre de 2025
**Versión**: 1.0

---

## 📋 Índice

1. [Visión General](#visión-general)
2. [Arquitectura](#arquitectura)
3. [Backend - API Endpoints](#backend---api-endpoints)
4. [Frontend - Interfaz de Usuario](#frontend---interfaz-de-usuario)
5. [Flujo de Datos](#flujo-de-datos)
6. [Próximos Pasos](#próximos-pasos)

---

## 🎯 Visión General

Sistema completo de gestión de roles y permisos que permite:
- ✅ Definir roles con permisos específicos por página
- ✅ Asignar/revocar permisos mediante interfaz visual
- ✅ Protección especial para el rol "Super Admin"
- ✅ Actualización en tiempo real de permisos
- ✅ Validación de permisos en backend

---

## 🏗️ Arquitectura

### Modelo de Datos

```
┌─────────────┐
│    User     │
├─────────────┤
│ id          │
│ username    │
│ email       │
│ role_id     │──┐
└─────────────┘  │
                 │
                 ▼
         ┌─────────────┐       ┌─────────────────┐
         │    Role     │◄──────┤   Permission    │
         ├─────────────┤       ├─────────────────┤
         │ id          │       │ id              │
         │ name        │       │ role_id         │
         │ description │       │ page_name       │
         │ is_active   │       │ can_access      │
         └─────────────┘       │ created_at      │
                               └─────────────────┘
```

### Relaciones
- **User → Role**: Many-to-One (un usuario tiene un rol)
- **Role → Permission**: One-to-Many (un rol tiene múltiples permisos)

---

## 🔌 Backend - API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints de Roles

#### 1. **GET /roles**
Lista todos los roles con sus permisos

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Super Admin",
    "description": "Acceso total al sistema",
    "is_active": true,
    "permissions": [
      {
        "id": 1,
        "role_id": 1,
        "page_name": "dashboard",
        "can_access": true,
        "created_at": "2025-10-29T00:00:00"
      }
    ]
  }
]
```

---

### Endpoints de Permisos Individuales

#### 2. **POST /roles/{role_id}/permissions**
Crea un nuevo permiso para un rol

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters:**
- `role_id` (integer): ID del rol

**Request Body:**
```json
{
  "page_name": "dashboard",
  "can_access": true
}
```

**Response 201:**
```json
{
  "id": 5,
  "role_id": 2,
  "page_name": "dashboard",
  "can_access": true,
  "created_at": "2025-10-29T20:04:37"
}
```

**Errores:**
- `400 Bad Request`: Permiso ya existe
- `403 Forbidden`: Solo superusuarios pueden crear permisos
- `404 Not Found`: Rol no encontrado

---

#### 3. **PUT /roles/{role_id}/permissions/{permission_id}**
Actualiza un permiso existente

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters:**
- `role_id` (integer): ID del rol
- `permission_id` (integer): ID del permiso

**Request Body:**
```json
{
  "page_name": "dashboard",
  "can_access": false
}
```

**Response 200:**
```json
{
  "id": 5,
  "role_id": 2,
  "page_name": "dashboard",
  "can_access": false,
  "created_at": "2025-10-29T20:04:37"
}
```

**Errores:**
- `403 Forbidden`: Solo superusuarios pueden actualizar permisos
- `404 Not Found`: Permiso no encontrado

---

#### 4. **DELETE /roles/{role_id}/permissions/{permission_id}**
Elimina un permiso

**Headers:**
```
Authorization: Bearer <token>
```

**Path Parameters:**
- `role_id` (integer): ID del rol
- `permission_id` (integer): ID del permiso

**Response 204:** No Content

**Errores:**
- `403 Forbidden`: Solo superusuarios pueden eliminar permisos
- `404 Not Found`: Permiso no encontrado

---

## 🎨 Frontend - Interfaz de Usuario

### Ubicación
```
/configuracion → Tab "Roles y Permisos"
```

### Componentes Implementados

#### 1. **Tab de Roles y Permisos**
- Ubicado entre "Usuarios" e "Importadores"
- Color distintivo: Morado (`purple-500`)
- Icono: Escudo con checkmark

#### 2. **Tarjetas de Rol**
Cada rol tiene:
- **Header**: Nombre, descripción, estado (Activo/Inactivo)
- **Badge especial** para "Super Admin" (acceso total)
- **Grid de permisos**: 2 columnas responsivas

#### 3. **Grid de Permisos**
Cada permiso muestra:
- Nombre de la página
- Descripción breve
- Toggle switch para activar/desactivar
- Actualización en tiempo real

#### 4. **Páginas Configurables**

```typescript
const availablePages = [
  { name: "dashboard", label: "Dashboard", description: "Página principal con estadísticas" },
  { name: "catalogo", label: "Catálogo", description: "Ver y gestionar productos" },
  { name: "importers", label: "Importadores", description: "Gestionar importaciones" },
  { name: "configuracion", label: "Configuración", description: "Configuración del sistema" },
];
```

### Estados Visuales

#### Rol Activo
```
┌─────────────────────────────────────┐
│ Admin              [🟢 Activo]      │
│ Administrador del sistema           │
└─────────────────────────────────────┘
```

#### Rol Inactivo
```
┌─────────────────────────────────────┐
│ Viewer             [⚪ Inactivo]     │
│ Usuario solo lectura                │
└─────────────────────────────────────┘
```

#### Super Admin (Protegido)
```
┌─────────────────────────────────────────────────┐
│ Super Admin  [Acceso Total]  [🟢 Activo]       │
│ Acceso completo al sistema                      │
│                                                  │
│ ⚠️ Este rol tiene acceso completo a todas las   │
│    funciones del sistema                        │
└─────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Datos

### Cargar Roles y Permisos

```
1. Usuario → Abre tab "Roles y Permisos"
2. Frontend → GET /api/v1/roles
3. Backend → Consulta DB con selectinload(permissions)
4. Backend → Retorna roles con permisos embebidos
5. Frontend → Renderiza grid de permisos
```

### Actualizar Permiso

```
1. Usuario → Hace click en toggle switch
2. Frontend → Verifica si permiso existe
3a. Si existe:
    → PUT /api/v1/roles/{role_id}/permissions/{permission_id}
3b. Si no existe:
    → POST /api/v1/roles/{role_id}/permissions
4. Backend → Valida permisos del usuario (superuser)
5. Backend → Actualiza/crea permiso en DB
6. Backend → Retorna permiso actualizado
7. Frontend → Refresca lista de roles
8. Frontend → Muestra mensaje de éxito
```

### Diagrama de Secuencia

```
Usuario     Frontend        Backend         Database
  │            │              │                │
  │──click─────>│              │                │
  │            │──POST/PUT────>│                │
  │            │              │──UPDATE/INSERT──>│
  │            │              │<───Confirm──────┤
  │            │<──Success────┤                │
  │            │──GET roles───>│                │
  │            │              │───SELECT────────>│
  │            │              │<───Data─────────┤
  │            │<──Roles──────┤                │
  │<─Update UI─┤              │                │
```

---

## 🛡️ Seguridad

### Validaciones en Backend

1. **Autenticación**: Todos los endpoints requieren token JWT válido
2. **Autorización**: Solo superusuarios pueden gestionar permisos
3. **Validación de datos**: Schemas Pydantic validan request body
4. **Verificación de existencia**: Se verifica que el rol exista antes de crear permisos
5. **Prevención de duplicados**: No permite crear permisos duplicados para la misma página

### Código de Validación

```python
# backend/app/api/v1/roles.py

@router.post("/{role_id}/permissions", response_model=PermissionResponse)
async def create_permission(
    role_id: int,
    permission_data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # ← Autenticación
):
    # Autorización
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can create permissions",
        )

    # Verificación de existencia del rol
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Prevención de duplicados
    existing = await db.execute(
        select(Permission).where(
            Permission.role_id == role_id,
            Permission.page_name == permission_data.page_name
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Permission already exists")

    # Creación del permiso
    permission = Permission(**permission_data.dict(), role_id=role_id)
    db.add(permission)
    await db.commit()
    return permission
```

---

## 🎯 Funciones Principales del Frontend

### 1. fetchRolesWithPermissions()

Carga todos los roles con sus permisos desde la API.

```typescript
const fetchRolesWithPermissions = async () => {
  setLoadingRoles(true);
  try {
    const response = await fetch(`${API_URL}/roles`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await response.json();
    setRoles(data);
  } catch (err) {
    setRoleError(err.message);
  } finally {
    setLoadingRoles(false);
  }
};
```

### 2. updatePermission()

Crea o actualiza un permiso individual.

```typescript
const updatePermission = async (
  roleId: number,
  pageName: string,
  canAccess: boolean
) => {
  const role = roles.find(r => r.id === roleId);
  const existingPermission = role?.permissions?.find(
    p => p.page_name === pageName
  );

  let response;
  if (existingPermission) {
    // Actualizar existente
    response = await fetch(
      `${API_URL}/roles/${roleId}/permissions/${existingPermission.id}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ page_name: pageName, can_access: canAccess }),
      }
    );
  } else {
    // Crear nuevo
    response = await fetch(`${API_URL}/roles/${roleId}/permissions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ page_name: pageName, can_access: canAccess }),
    });
  }

  if (!response.ok) throw new Error("Error al actualizar permiso");

  setRoleSuccess("Permiso actualizado correctamente");
  await fetchRolesWithPermissions();
  setTimeout(() => setRoleSuccess(""), 3000);
};
```

---

## 📊 Tipos TypeScript

```typescript
interface Permission {
  id: number;
  role_id: number;
  page_name: string;
  can_access: boolean;
  created_at: string;
}

interface Role {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  permissions?: Permission[];
}

interface PageDefinition {
  name: string;
  label: string;
  description: string;
}
```

---

## ✅ Testing

### Endpoints a Probar

1. **Crear permiso nuevo**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/roles/2/permissions \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"page_name": "dashboard", "can_access": true}'
   ```

2. **Actualizar permiso existente**:
   ```bash
   curl -X PUT http://localhost:8000/api/v1/roles/2/permissions/5 \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"page_name": "dashboard", "can_access": false}'
   ```

3. **Eliminar permiso**:
   ```bash
   curl -X DELETE http://localhost:8000/api/v1/roles/2/permissions/5 \
     -H "Authorization: Bearer <token>"
   ```

### Casos de Prueba Frontend

1. ✅ **Cambiar permiso de Admin**: Dashboard OFF → ON
2. ✅ **Crear permiso nuevo**: Viewer sin acceso a Configuración → agregar permiso
3. ✅ **Verificar Super Admin**: Toggle debe estar deshabilitado
4. ✅ **Mensaje de éxito**: Debe aparecer y desaparecer en 3 segundos
5. ✅ **Recarga de datos**: Lista debe actualizarse después de cambio

---

## 🚀 Próximos Pasos

### 1. Protección de Rutas (Frontend)

Implementar verificación de permisos en cada página:

```typescript
// frontend/app/catalogo/page.tsx
const { user } = useAuth();
const hasAccess = user?.role?.permissions?.find(
  p => p.page_name === "catalogo" && p.can_access
);

if (!hasAccess && !user?.is_superuser) {
  return <AccessDenied />;
}
```

### 2. Filtrado de Navegación

Ocultar items del menú según permisos:

```typescript
// frontend/components/Navigation.tsx
const hasPermission = (pageName: string) => {
  if (user?.is_superuser) return true;
  return user?.role?.permissions?.some(
    p => p.page_name === pageName && p.can_access
  ) ?? false;
};

const navItems = [
  { href: "/dashboard", label: "Dashboard", show: hasPermission("dashboard") },
  { href: "/catalogo", label: "Catálogo", show: hasPermission("catalogo") },
  // ...
].filter(item => item.show);
```

### 3. Middleware de Permisos (Backend)

Crear un dependency para validar permisos por página:

```python
# backend/app/api/dependencies.py

async def require_permission(page_name: str):
    async def check_permission(
        current_user: User = Depends(get_current_active_user)
    ):
        if current_user.is_superuser:
            return current_user

        has_permission = any(
            p.page_name == page_name and p.can_access
            for p in current_user.role.permissions
        )

        if not has_permission:
            raise HTTPException(
                status_code=403,
                detail=f"No permission to access {page_name}"
            )

        return current_user

    return check_permission

# Uso:
@router.get("/products")
async def list_products(
    user: User = Depends(require_permission("catalogo"))
):
    # ...
```

### 4. Auditoría de Permisos

Agregar tabla de logs para auditoría:

```sql
CREATE TABLE permission_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50),  -- 'created', 'updated', 'deleted'
    role_id INTEGER REFERENCES roles(id),
    permission_id INTEGER REFERENCES permissions(id),
    old_value JSONB,
    new_value JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 📝 Notas de Implementación

### Decisiones de Diseño

1. **Permisos a nivel de página**: Se decidió usar permisos por página en lugar de permisos granulares (ej: "products.create", "products.delete") para simplificar la UI inicial.

2. **Super Admin inmutable**: El rol Super Admin no permite editar permisos desde la UI para evitar que un admin se bloquee a sí mismo.

3. **Actualización en tiempo real**: Se recargan todos los roles después de cada cambio para mantener la UI sincronizada.

4. **Toggle switch visual**: Se eligió un toggle switch en lugar de checkboxes para mejor UX móvil.

### Optimizaciones Futuras

1. **Cache de permisos**: Implementar cache en frontend para evitar recargas innecesarias
2. **Actualizaciones optimistas**: Actualizar UI inmediatamente y revertir si falla
3. **WebSockets**: Notificar cambios de permisos en tiempo real a usuarios conectados
4. **Permisos granulares**: Expandir a nivel de operaciones (CRUD) por recurso

---

## 🎉 Estado Actual

### ✅ Completado

- [x] Modelos de datos (User, Role, Permission)
- [x] Migración de base de datos
- [x] Endpoints CRUD de permisos individuales
- [x] Tab de Roles y Permisos en frontend
- [x] UI de gestión de permisos con toggle switches
- [x] Validación de permisos en backend
- [x] Protección especial para Super Admin
- [x] Mensajes de éxito/error en UI
- [x] Documentación completa

### ⏳ Pendiente

- [ ] Protección de rutas en frontend
- [ ] Filtrado de navegación según permisos
- [ ] Middleware de permisos en backend
- [ ] Auditoría de cambios de permisos
- [ ] Tests unitarios e integración

---

## 📞 Soporte

Para dudas o problemas con el sistema de permisos:

1. Revisar logs del backend en `/backend/logs/`
2. Verificar consola del navegador (F12)
3. Comprobar que el usuario sea superuser para gestionar permisos
4. Validar que el backend esté corriendo en http://localhost:8000

---

**Última actualización**: 29 de octubre de 2025
**Autor**: Sistema SYNCAR v2.0
**Licencia**: Propiedad de SYNCAR
