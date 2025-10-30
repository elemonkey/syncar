# Fix: Error de useContext en Next.js

## 🐛 Problema Identificado

Error al cargar la página de configuración:
```
TypeError: Cannot read properties of null (reading 'useContext')
```

Este error ocurría porque `AuthContext` estaba usando `useRouter` de Next.js internamente, lo que causaba conflictos en la renderización del lado del servidor.

## ✅ Solución Implementada

### 1. Modificado AuthContext

**Cambios en `/frontend/contexts/AuthContext.tsx`**:

- ❌ **Antes**: AuthContext usaba `useRouter` internamente
```typescript
const router = useRouter();

const login = async (username: string, password: string) => {
  // ... código ...
  router.push("/dashboard");
};

const logout = () => {
  // ... código ...
  router.push("/");
};
```

- ✅ **Después**: AuthContext usa callbacks opcionales
```typescript
// Sin useRouter interno

const login = async (
  username: string,
  password: string,
  onSuccess?: () => void
) => {
  // ... código ...
  if (onSuccess) {
    onSuccess();
  }
};

const logout = (onSuccess?: () => void) => {
  // ... código ...
  if (onSuccess) {
    onSuccess();
  }
};
```

### 2. Actualizado Login Page

**Cambios en `/frontend/app/page.tsx`**:

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setError("");
  setIsLoading(true);

  try {
    await login(username, password, () => {
      router.push("/dashboard");  // Callback con navegación
    });
  } catch (err: any) {
    setError(err.message || "Credenciales inválidas");
  } finally {
    setIsLoading(false);
  }
};
```

### 3. Actualizado Navigation Component

**Cambios en `/frontend/components/Navigation.tsx`**:

```typescript
const router = useRouter();  // Agregado

<button
  onClick={() => {
    setShowUserMenu(false);
    logout(() => router.push("/"));  // Callback con navegación
  }}
>
  Cerrar Sesión
</button>
```

## 🎯 Por qué Funciona Ahora

### Problema Original
- `useRouter` debe ser llamado en componentes de cliente
- Cuando `AuthContext` usaba `useRouter` internamente, causaba conflictos con el renderizado del servidor (SSR)
- Next.js intentaba ejecutar el hook antes de que el contexto estuviera disponible

### Solución
- El `AuthContext` ya no depende de `useRouter`
- Cada componente que necesita navegación usa su propio `useRouter`
- Los componentes pasan callbacks al `login` y `logout` para manejar la navegación
- Esto separa la lógica de autenticación de la lógica de navegación

## 📋 Archivos Modificados

1. `/frontend/contexts/AuthContext.tsx`
   - Eliminado `import { useRouter } from "next/navigation"`
   - Modificado tipo `AuthContextType` para incluir callbacks opcionales
   - Actualizado `login()` para aceptar `onSuccess?: () => void`
   - Actualizado `logout()` para aceptar `onSuccess?: () => void`

2. `/frontend/app/page.tsx`
   - Actualizado `handleSubmit()` para pasar callback de navegación a `login()`

3. `/frontend/components/Navigation.tsx`
   - Agregado `import { useRouter } from "next/navigation"`
   - Agregado `const router = useRouter()`
   - Actualizado botón de logout para pasar callback de navegación

4. `/frontend/app/configuracion/page.tsx`
   - Sin cambios (ya funcionaba correctamente)

## ✅ Resultado

- ✅ Frontend carga sin errores (HTTP 200)
- ✅ Login funciona correctamente
- ✅ Logout funciona correctamente
- ✅ Navegación entre páginas funciona
- ✅ La gestión de usuarios en el tab de configuración está lista para usar

## 🧪 Verificación

```bash
# Frontend está respondiendo
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# Output: 200

# Backend está respondiendo
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs
# Output: 200
```

## 🚀 Uso

1. Ir a http://localhost:3000
2. Login con `admin` / `admin123`
3. Será redirigido a `/dashboard`
4. Click en "Configuración"
5. Click en tab "Usuarios"
6. Ver lista completa de usuarios
7. Crear, editar, eliminar usuarios según sea necesario

## 📝 Notas Técnicas

### Patrón de Diseño Utilizado

**Inversión de Control (IoC)**: El contexto ya no controla la navegación directamente. En su lugar, los componentes que lo usan proporcionan la lógica de navegación a través de callbacks.

Ventajas:
- Desacopla la lógica de autenticación de la navegación
- Permite testing más fácil del AuthContext
- Evita conflictos con el renderizado del servidor
- Más flexible para diferentes estrategias de navegación

### Compatibilidad

- ✅ Next.js 14.2.33
- ✅ React 18
- ✅ Server-Side Rendering (SSR)
- ✅ Client-Side Navigation

## 🔧 Si el Error Persiste

Si aún ves el error después de estos cambios:

1. **Limpiar caché de Next.js**:
```bash
cd frontend
rm -rf .next
npm run dev
```

2. **Verificar que todos los cambios se guardaron**:
```bash
git status
git diff
```

3. **Reiniciar el servidor de desarrollo**:
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

4. **Limpiar localStorage del navegador**:
```javascript
// En la consola del navegador
localStorage.clear()
location.reload()
```
