# 🔧 Fix: Error ENOENT - Next.js Build Manifest

## 🐛 Problema

Después de modificar archivos en el proyecto, Next.js mostraba el siguiente error:

```
Error: ENOENT: no such file or directory, open '.next/server/app/dashboard/page/app-build-manifest.json'
```

Este error se repetía múltiples veces y impedía que la aplicación funcionara correctamente.

## 🔍 Causa

Este error ocurre cuando el caché de Next.js (`.next` folder) se corrompe o queda en un estado inconsistente. Esto puede suceder cuando:

1. Se modifican archivos mientras el servidor está corriendo
2. El proceso de Next.js se interrumpe abruptamente
3. Hay cambios significativos en la estructura de archivos
4. Los archivos de build están parcialmente generados

## ✅ Solución

### 1. Limpiar el caché de Next.js

```bash
cd frontend
rm -rf .next
```

### 2. Matar cualquier proceso corriendo en el puerto 3000

```bash
lsof -ti:3000 | xargs kill -9
```

### 3. Reiniciar el servidor

```bash
npm run dev
```

## 📝 Solución Completa (Un Solo Comando)

Para automatizar el proceso, puedes usar:

```bash
cd frontend && \
lsof -ti:3000 | xargs kill -9 2>/dev/null; \
rm -rf .next && \
npm run dev
```

## 🔄 Cuándo Aplicar Esta Solución

Limpia el caché de Next.js cuando veas:

- ❌ `ENOENT: no such file or directory` en archivos `.next`
- ❌ `Module not found` después de agregar nuevos archivos
- ❌ Cambios en el código que no se reflejan en el navegador
- ❌ Errores de compilación inexplicables
- ❌ `app-build-manifest.json` no encontrado

## 🎯 Resultado

Después de aplicar la solución:

```
✓ Starting...
✓ Ready in 1679ms
○ Compiling /dashboard ...
✓ Compiled /dashboard in 4.3s
GET /dashboard 200 in 4827ms
```

✅ **Servidor corriendo sin errores**
✅ **Páginas compilando correctamente**
✅ **Respuestas HTTP 200 OK**

## 💡 Prevención

Para evitar este problema en el futuro:

1. **Usa `Ctrl+C` para detener el servidor** en lugar de cerrar la terminal abruptamente
2. **Reinicia el servidor después de cambios estructurales** (nuevos archivos, cambios en `next.config.js`, etc.)
3. **Limpia el caché periódicamente** si trabajas en desarrollo intensivo
4. **No edites archivos en `.next` manualmente** - este folder se genera automáticamente

## 🛠️ Comandos Útiles

### Limpiar todo el caché (incluye node_modules)
```bash
cd frontend
rm -rf .next node_modules package-lock.json
npm install
npm run dev
```

### Ver procesos usando el puerto 3000
```bash
lsof -ti:3000
```

### Verificar que el servidor esté corriendo
```bash
curl http://localhost:3000/dashboard
```

### Build de producción (limpio)
```bash
rm -rf .next
npm run build
```

## 📚 Referencias

- [Next.js Documentation - Caching](https://nextjs.org/docs/app/building-your-application/caching)
- [Next.js Turbopack Mode](https://nextjs.org/docs/architecture/turbopack)
- [GitHub Issues - Similar ENOENT errors](https://github.com/vercel/next.js/issues?q=is%3Aissue+ENOENT+app-build-manifest)

## ✨ Estado Actual

- ✅ Caché limpiado
- ✅ Servidor reiniciado
- ✅ Dashboard compilando correctamente
- ✅ Sin errores ENOENT
- ✅ Aplicación funcionando normalmente
