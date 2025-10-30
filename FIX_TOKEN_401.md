# 🔐 Fix: Error 401 "Could not validate credentials"

## 🐛 Problema Identificado

Los endpoints protegidos (`/api/v1/users`, `/api/v1/roles`) devolvían **401 Unauthorized** a pesar de que el login era exitoso.

### Causa Raíz

La biblioteca `python-jose` requiere que el campo `sub` (subject) en el payload del JWT sea un **string**, pero el código lo estaba enviando como un **integer** (`user.id`).

Error específico de jose:
```
JWTClaimsError: Subject must be a string.
```

## ⚠️ IMPORTANTE: Limpiar Tokens Viejos

**Después de aplicar el fix y reiniciar el backend, los tokens generados ANTES del reinicio seguirán causando 401**.

### Solución Rápida para el Usuario

1. **Abrir DevTools** (F12 o Cmd+Option+I)
2. **En la consola ejecutar**:
```javascript
localStorage.clear()
location.reload()
```
3. **Hacer login nuevamente** para obtener un token con formato correcto

## ✅ Solución Aplicada

### Cambios en `backend/app/api/v1/auth.py`:

1. **En el endpoint `/login`** (línea ~107):
   ```python
   # ANTES
   access_token = create_access_token(
       data={"sub": user.id}, expires_delta=access_token_expires
   )

   # DESPUÉS
   access_token = create_access_token(
       data={"sub": str(user.id)}, expires_delta=access_token_expires
   )
   ```

2. **En el endpoint `/token`** (línea ~143):
   ```python
   # ANTES
   access_token = create_access_token(
       data={"sub": user.id}, expires_delta=access_token_expires
   )

   # DESPUÉS
   access_token = create_access_token(
       data={"sub": str(user.id)}, expires_delta=access_token_expires
   )
   ```

3. **En la función `get_current_user`** (línea ~38):
   ```python
   # ANTES
   user_id: int = payload.get("sub")
   if user_id is None:
       raise credentials_exception

   # DESPUÉS
   user_id_str: str = payload.get("sub")
   if user_id_str is None:
       raise credentials_exception
   user_id = int(user_id_str)
   ```

4. **Cambio adicional** - OAuth2PasswordBearer tokenUrl:
   ```python
   # ANTES
   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

   # DESPUÉS
   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
   ```

## 🧪 Verificación

### Script de debug creado: `backend/debug_token.py`

Resultado antes del fix:
```
❌ ERROR al decodificar: Subject must be a string.
```

Resultado después del fix:
```
✅ Token decodificado exitosamente!
Payload: {'sub': '1', 'exp': 1761222355}
User ID extraído: 1
✅ User ID válido: 1 (tipo: <class 'str'>)
```

## 📝 Próximos Pasos

1. **Reiniciar el backend**:
   ```bash
   # Detener el proceso actual (Ctrl+C)
   # Luego ejecutar:
   cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0
   make dev-backend
   ```

2. **Probar la autenticación**:
   ```bash
   # Login
   TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

   # Probar endpoint protegido
   curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users | jq
   ```

3. **Verificar en el frontend**:
   - Ir a `http://localhost:3000`
   - Login con `admin` / `admin123`
   - Navegar a **Configuración → Usuarios**
   - Debe mostrar la lista de usuarios sin errores 401

## 📚 Contexto Técnico

### JWT Standard (RFC 7519)

El estándar JWT especifica que el claim `sub` debe ser un **StringOrURI**:

> "sub" (Subject) Claim: The "sub" (subject) claim identifies the
> principal that is the subject of the JWT.  The Claims in a JWT are
> normally statements about the subject.  The subject value MUST be
> either a string containing a StringOrURI value or a number.

Aunque el estándar permite números, la implementación de `python-jose` es más estricta y **requiere strings**.

### Otras bibliotecas JWT en Python

- **PyJWT**: Acepta tanto int como string para `sub`
- **python-jose**: **Solo acepta string** (más estricto)

Nuestro proyecto usa `python-jose`, por lo que debemos seguir su especificación.

## 🔍 Archivos Modificados

- ✅ `backend/app/api/v1/auth.py` - Correcciones en login, token y get_current_user
- ✅ Backend reiniciado el 29/10/2025 a las 19:27

## 🔄 Estado del Backend

```
Backend reiniciado: 29 Oct 2025 19:27
Proceso: PID 6927
Puerto: http://localhost:8000
Estado: ✅ Corriendo con JWT fix aplicado
```

## ✅ Cómo Verificar que Funcionó

### 1. Después de limpiar localStorage y hacer login:

Verificar que los endpoints respondan correctamente:
```bash
# En el navegador, ver Network tab (F12 → Network)
# Debería mostrar:
GET /api/v1/users → 200 OK
GET /api/v1/roles → 200 OK
GET /api/v1/auth/me → 200 OK
```

### 2. Inspeccionar el nuevo token:

```javascript
// En la consola del navegador
const token = localStorage.getItem('auth_token') // o la key que uses
const payload = JSON.parse(atob(token.split('.')[1]))
console.log('Token payload:', payload)
console.log('Type of sub:', typeof payload.sub)  // Debe ser "string"
```

### 3. Verificar en la UI:

- Ir a **Configuración → Usuarios**
- La tabla de usuarios debe cargar sin errores 401
- Los roles deben aparecer correctamente

## 📊 Timeline del Fix

| Fecha | Hora | Evento |
|-------|------|--------|
| 29 Oct | 08:00 | Backend con bug (sub: int) |
| 29 Oct | 19:27 | Backend reiniciado con fix (sub: string) |
| 29 Oct | 19:30 | Tokens viejos causan 401 ❌ |
| 29 Oct | 19:35 | Usuario limpia localStorage ✅ |

## ⚠️ Nota Importante

Después de este cambio, **todos los tokens existentes en localStorage serán inválidos** porque tienen el `sub` como integer. Los usuarios deberán:

1. Cerrar sesión (o limpiar localStorage)
2. Iniciar sesión nuevamente

Los nuevos tokens tendrán el formato correcto con `sub` como string.
