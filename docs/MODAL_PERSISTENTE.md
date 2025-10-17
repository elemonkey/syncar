# 🎯 Modal Persistente de Importación - Guía de Uso

## 📋 Resumen de Implementación

Hemos implementado un **sistema de modal persistente** que muestra el progreso de importación de productos con las siguientes características:

### ✅ Características Implementadas

1. **Ventana Minimizable**
   - Se minimiza a una ventana pequeña en la esquina inferior derecha
   - Muestra progreso, tiempo transcurrido e icono de estado
   - Click para maximizar

2. **Persistencia Total**
   - Funciona en **cualquier página** de la aplicación
   - Sobrevive a la navegación entre páginas
   - Se restaura después de refrescar el navegador (usando localStorage)

3. **5 Pasos Detallados**
   - **PASO 1: AUTENTICACIÓN** (0-10%) - "Iniciando sesión..."
   - **PASO 2: NAVEGACIÓN** (10-20%) - "Navegando hacia categoría..."
   - **PASO 3: EXTRACCIÓN** (20-90%) - "Importando producto X de Y"
   - **PASO 4: GUARDANDO** (90-100%) - "Guardando en base de datos..."
   - **PASO 5: COMPLETADO** (100%) - "Importación finalizada"

4. **Control de Usuario**
   - Minimizar/Maximizar ilimitadas veces
   - Solo se puede cerrar cuando termina o hay error
   - Botón de cerrar manual disponible

5. **Información en Tiempo Real**
   - Contador de productos: "Importando producto 15 de 54"
   - Tiempo transcurrido: "05:23" (MM:SS)
   - Barra de progreso visual (0-100%)
   - Iconos animados según estado

---

## 🗂️ Archivos Creados/Modificados

### Nuevos Archivos

1. **`frontend/contexts/ImportJobContext.tsx`** (135 líneas)
   - Context API para estado global de importación
   - Gestión de localStorage para persistencia
   - Métodos: `startJob()`, `updateJob()`, `closeJob()`, `toggleMinimize()`

2. **`frontend/components/PersistentImportModal.tsx`** (350 líneas)
   - Componente dual: Vista minimizada + Vista maximizada
   - Polling cada 2 segundos al backend
   - Mapeo automático de progreso → pasos detallados

### Archivos Modificados

3. **`frontend/app/layout.tsx`**
   - Agregado `<ImportJobProvider>` wrapper
   - Agregado `<PersistentImportModal />` componente

4. **`frontend/components/importers/ImporterPanel.tsx`**
   - Removido modal local viejo
   - Integrado `useImportJob()` hook
   - Llama a `startJob()` al iniciar importación

---

## 🧪 Cómo Probar

### 1️⃣ Iniciar Servidores

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # o tu entorno virtual
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 2️⃣ Abrir Aplicación

Navega a: **http://localhost:3000/importers**

### 3️⃣ Iniciar Importación

1. Selecciona **Noriega** como importador
2. Click en **"Importar Categorías"**
3. Espera a que carguen las categorías
4. Selecciona al menos 1 categoría (checkbox)
5. Click en **"Importar Productos"**

### 4️⃣ Observar Modal

**Deberías ver:**
- Modal maximizado aparece inmediatamente
- Título: "Importación de Productos - Noriega"
- Estado inicial: "PASO 1: AUTENTICACIÓN"
- Barra de progreso comienza a llenarse

### 5️⃣ Probar Minimizar

1. Click en el botón **"−"** (minimizar) en la esquina superior derecha
2. El modal desaparece
3. Aparece ventana pequeña en **esquina inferior derecha** con:
   - 🔄 Icono girando
   - "Productos"
   - "45%" (ejemplo)
   - "03:15" (tiempo)
   - Mini barra de progreso

### 6️⃣ Probar Navegación

1. Con el modal minimizado, navega a **http://localhost:3000/catalogo**
2. La ventana minimizada **permanece visible**
3. Click en la ventana minimizada → Se maximiza el modal
4. Navega a **http://localhost:3000/configuracion**
5. El modal sigue funcionando

### 7️⃣ Probar Refresh

1. Con la importación corriendo, **refresca el navegador** (F5 o Cmd+R)
2. El modal debería **restaurarse** desde localStorage
3. Continúa mostrando el progreso actual

### 8️⃣ Observar Progreso Detallado

Durante la importación, deberías ver:

**0-10%:**
```
PASO 1: AUTENTICACIÓN
Iniciando sesión en el sistema...
```

**10-20%:**
```
PASO 2: NAVEGACIÓN
Navegando hacia categoría...
```

**20-90%:**
```
PASO 3: EXTRACCIÓN
Importando producto 23 de 54
```

**90-100%:**
```
PASO 4: GUARDANDO
Guardando en base de datos...
```

**100%:**
```
PASO 5: COMPLETADO
✅ Importación finalizada exitosamente
```

---

## 🎨 Vistas del Modal

### Vista Maximizada

```
┌─────────────────────────────────────────────┐
│  Importación de Productos - Noriega    [−][×]│
├─────────────────────────────────────────────┤
│                                             │
│  PASO 3: EXTRACCIÓN                         │
│                                             │
│  Importando producto 23 de 54               │
│                                             │
│  ████████████████░░░░░░  65%                │
│                                             │
│  Tiempo transcurrido: 03:25                 │
│                                             │
│  ① AUTENTICACIÓN        ✅                  │
│  ② NAVEGACIÓN           ✅                  │
│  ③ EXTRACCIÓN           🔄 (En progreso)    │
│  ④ GUARDANDO            ⏳                  │
│  ⑤ COMPLETADO           ⏳                  │
│                                             │
└─────────────────────────────────────────────┘
```

### Vista Minimizada

```
Esquina inferior derecha:

┌────────────────────┐
│ 🔄 Productos       │
│ 65%        03:25   │
│ ████████░░ 65%     │
└────────────────────┘
```

---

## 🔧 Arquitectura Técnica

### Flujo de Datos

```
ImporterPanel.tsx
    │
    │ onClick "Importar Productos"
    │
    ├─→ POST /api/v1/dev/noriega/import-products
    │       │
    │       └─→ Retorna { job_id: "uuid" }
    │
    └─→ startJob(job_id, "products")
            │
            └─→ ImportJobContext
                    │
                    ├─→ Guarda en State
                    ├─→ Guarda en localStorage
                    │
                    └─→ PersistentImportModal
                            │
                            └─→ Polling cada 2s
                                    │
                                    └─→ GET /api/v1/dev/status/{job_id}
                                            │
                                            └─→ updateJob({ progress, status })
```

### Estado del Job

```typescript
interface ImportJob {
  jobId: string;               // "123e4567-e89b-12d3-a456-426614174000"
  jobType: 'products';         // Tipo de importación
  status: 'pending' | 'running' | 'completed' | 'error';
  progress: number;            // 0-100
  currentStep: string;         // "PASO 3: EXTRACCIÓN"
  detailedStatus: string;      // "Importando producto 23 de 54"
  startedAt: Date;             // Hora de inicio
  isMinimized: boolean;        // true/false
}
```

### localStorage

```json
{
  "currentImportJob": {
    "jobId": "abc-123",
    "jobType": "products",
    "status": "running",
    "progress": 45,
    "currentStep": "PASO 3: EXTRACCIÓN",
    "detailedStatus": "Importando producto 15 de 54",
    "startedAt": "2025-10-16T21:30:00.000Z",
    "isMinimized": false
  }
}
```

---

## 🐛 Debugging

### Ver localStorage en DevTools

1. Abre **DevTools** (F12)
2. Ve a la pestaña **Application**
3. En el sidebar, expande **Local Storage**
4. Click en **http://localhost:3000**
5. Busca la clave: **`currentImportJob`**

### Ver Polling en Network

1. Abre **DevTools** (F12)
2. Ve a la pestaña **Network**
3. Filtra por: **`status`**
4. Deberías ver requests cada 2 segundos:
   ```
   GET /api/v1/dev/status/abc-123
   ```

### Logs en Consola

El modal imprime logs útiles:
```javascript
🔄 Iniciando polling para job: abc-123
📊 Progress actualizado: 45% - PASO 3: EXTRACCIÓN
✅ Job completado: abc-123
```

---

## ❓ Solución de Problemas

### El modal no aparece

**Posibles causas:**
- ImportJobProvider no está en layout.tsx
- Error en el contexto (revisa consola)
- Backend no retorna `job_id`

**Solución:**
```bash
# Verifica que layout.tsx tenga:
<ImportJobProvider>
  <Navigation />
  {children}
  <PersistentImportModal />
</ImportJobProvider>
```

### El modal desaparece al cambiar de página

**Causa:** Context no está en el layout raíz

**Solución:** Verifica que `ImportJobProvider` esté en `app/layout.tsx`, no en páginas individuales

### El modal no se restaura después de refresh

**Causa:** localStorage no se está guardando

**Solución:**
1. Verifica localStorage en DevTools
2. Revisa que `currentImportJob` exista
3. Comprueba que `startedAt` sea válido

### Los pasos no se muestran correctamente

**Causa:** Backend no está enviando `progress` correcto

**Solución:** Verifica que el endpoint `/status/{job_id}` retorne:
```json
{
  "status": "running",
  "progress": 45,
  "current_item": 23,
  "total_items": 54
}
```

### El contador de productos no aparece

**Causa:** Backend no envía `total_items`

**Solución:** El modal calcula el producto actual así:
```typescript
const processed = Math.floor((progress - 20) / 70 * totalItems);
```

Asegúrate de que el backend envíe `total_items` en la respuesta.

---

## 🎯 Próximos Pasos

### Mejoras Futuras (Opcional)

1. **Notificación de Escritorio**
   ```typescript
   if (Notification.permission === 'granted') {
     new Notification('Importación Completada', {
       body: '54 productos importados exitosamente'
     });
   }
   ```

2. **Sonido al Completar**
   ```typescript
   const audio = new Audio('/notification.mp3');
   audio.play();
   ```

3. **Lista de Productos Importados**
   - Mostrar tabla con productos importados
   - Link para ver en catálogo

4. **Historial de Importaciones**
   - Guardar historial en localStorage
   - Mostrar últimas 10 importaciones

5. **WebSockets** (Avanzado)
   - Reemplazar polling con WebSocket
   - Actualizaciones en tiempo real

---

## 📚 Documentación de Referencia

- **React Context API**: https://react.dev/reference/react/useContext
- **localStorage**: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
- **Tailwind CSS**: https://tailwindcss.com/docs

---

## ✅ Checklist de Validación

Marca cada item después de probarlo:

- [ ] Modal aparece al iniciar importación
- [ ] Botón minimizar funciona
- [ ] Ventana minimizada aparece en esquina inferior derecha
- [ ] Ventana minimizada muestra: icono, tipo, %, tiempo, barra
- [ ] Click en ventana minimizada maximiza el modal
- [ ] Modal persiste al navegar a /catalogo
- [ ] Modal persiste al navegar a /configuracion
- [ ] Modal se restaura después de refresh (F5)
- [ ] Paso 1 (0-10%): "AUTENTICACIÓN" aparece
- [ ] Paso 2 (10-20%): "NAVEGACIÓN" aparece
- [ ] Paso 3 (20-90%): "EXTRACCIÓN" con contador aparece
- [ ] Paso 4 (90-100%): "GUARDANDO" aparece
- [ ] Paso 5 (100%): "COMPLETADO" aparece
- [ ] Tiempo transcurrido actualiza cada segundo
- [ ] Barra de progreso se llena correctamente
- [ ] Botón cerrar solo aparece al completar/error
- [ ] Puedes minimizar/maximizar múltiples veces
- [ ] Al completar, muestra ✅ checkmark verde
- [ ] Al tener error, muestra ❌ icono rojo

---

## 🎉 ¡Listo para Probar!

Ahora puedes:
1. Iniciar una importación de productos
2. Minimizar el modal
3. Navegar a cualquier página
4. Maximizar cuando quieras ver el detalle
5. El modal se mantiene hasta que termine

**Disfruta de tu nuevo sistema de importación con seguimiento persistente! 🚀**
