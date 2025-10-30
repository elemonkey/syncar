# FIX: Error 401 - "Could not validate credentials"

## 🐛 Problema

Los tokens JWT generados durante el login no podían ser validados en endpoints protegidos, resultando en errores 401 Unauthorized con el mensaje "Could not validate credentials".

## 🔍 Causa Raíz

La biblioteca `python-jose` que se usa para JWT requiere que el campo `sub` (subject) en el payload del token sea un **string**, no un entero.

El código estaba creando tokens con:
```python
data={"sub": user.id}  # user.id es un int
```

Cuando `jose` intentaba decodificar el token, lanzaba un `JWTClaimsError: Subject must be a string`.

## ✅ Solución

Se modificaron 3 partes del código en `backend/app/api/v1/auth.py`:

### 1. Endpoint `/login` - Línea ~111
**Antes:**
```python
access_token = create_access_token(
    data={"sub": user.id}, expires_delta=access_token_expires
)
```

**Después:**
```python
access_token = create_access_token(
    data={"sub": str(user.id)}, expires_delta=access_token_expires
)
```

### 2. Endpoint `/token` - Línea ~145
**Antes:**
```python
access_token = create_access_token(
    data={"sub": user.id}, expires_delta=access_token_expires
)
```

**Después:**
```python
access_token = create_access_token(
    data={"sub": str(user.id)}, expires_delta=access_token_expires
)
```

### 3. Función `get_current_user` - Línea ~38
**Antes:**
```python
try:
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
except JWTError:
    raise credentials_exception
```

**Después:**
```python
try:
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    user_id = int(user_id_str)
except JWTError:
    raise credentials_exception
```

## 🧪 Verificación

Ejecutar el script de debug:
```bash
cd backend
python3 debug_token.py
```

Resultado esperado:
```
✅ Token decodificado exitosamente!
Payload: {'sub': '1', 'exp': 1761222355}
User ID extraído: 1
✅ User ID válido: 1 (tipo: <class 'str'>)
```

## 📝 Cambio Adicional

También se corrigió el `tokenUrl` en el `OAuth2PasswordBearer`:

**Antes:**
```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
```

**Después:**
```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
```

Esto apunta al endpoint OAuth2 estándar (`/token`) en lugar del endpoint custom (`/login`).

## 🚀 Cómo Aplicar

1. Detener el backend si está corriendo
2. Los cambios ya están aplicados en `backend/app/api/v1/auth.py`
3. Reiniciar el backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Probar el login y acceso a endpoints protegidos

## ✅ Testing

Una vez reiniciado el backend, probar con curl:
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 2. Verificar token
echo "Token: ${TOKEN:0:50}..."

# 3. Probar endpoint protegido
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users | jq

# Debería retornar 200 OK con la lista de usuarios
```

## 📚 Referencias

- [python-jose documentation](https://python-jose.readthedocs.io/)
- [JWT Standard - RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519) - El campo `sub` debe ser un StringOrURI
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
