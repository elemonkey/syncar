# 📦 SCRAPING COMPLETO DE PRODUCTOS NORIEGA

## 🚀 Nueva Estrategia: Navegación a Páginas de Detalle

### ✅ Cambio Implementado

**ANTES** (solo lista):
- Extraer productos de la tabla principal
- Obtener solo 7 campos básicos
- Imágenes, OEM y aplicaciones NO disponibles

**AHORA** (navegación completa):
- ✅ Extraer lista de SKUs de la tabla
- ✅ Por cada SKU, navegar a `producto.jsp?codigo={SKU}`
- ✅ Extraer **TODOS** los datos disponibles
- ✅ Incluye: imágenes, OEM, aplicaciones, etc.

---

## 🎯 Flujo Completo

```
1. Navegar a categoría
   ↓
2. Extraer conteo total (ej: "236 resultados")
   ↓
3. Obtener lista de SKUs de la tabla
   ↓
4. Por cada SKU (respetando límite):
   ├─ Construir URL: producto.jsp?codigo={SKU}
   ├─ Navegar a página de detalle
   ├─ Extraer datos completos
   ├─ Esperar {scraping_speed_ms}
   └─ Siguiente producto
   ↓
5. Guardar todos en base de datos
```

---

## 🔧 Configuración

### Parámetros Clave

```python
config = {
    "products_per_category": 5,      # Límite por categoría (desarrollo)
    "scraping_speed_ms": 2000        # 2 segundos entre productos
}
```

### ⏱️ Tiempos Estimados

| Productos | Velocidad | Tiempo Total |
|-----------|-----------|--------------|
| 5 | 2000ms | ~15 segundos |
| 10 | 2000ms | ~30 segundos |
| 50 | 2000ms | ~2.5 minutos |
| 236 | 2000ms | ~10-15 minutos |

**Nota**: Incluye tiempo de navegación + extracción + delay

---

## 📊 Datos Extraídos

### Campos Principales (tabla `products`)

| Campo | Tipo | Ejemplo |
|-------|------|---------|
| `sku` | String | "006342" |
| `name` | String | "AMORTIGUADOR DELANTERO" |
| `description` | Text | "Amortiguador delantero para vehículos..." |
| `brand` | String | "KIC" |
| `price` | Float | 17920.0 |
| `stock` | Integer | 1 (disponible) / 0 (sin stock) |
| `image_url` | String | URL de imagen principal |
| `images` | JSON | Array con todas las URLs de imágenes |

### Campos Adicionales (JSON `extra_data`)

```json
{
  "origin": "KOREA",
  "oem": ["AB123456", "CD789012"],
  "applications": [
    {
      "car_brand": "Toyota",
      "car_model": "Corolla",
      "year_start": 2015,
      "year_end": 2020
    }
  ]
}
```

---

## 🎨 Selectores CSS (Página de Detalle)

### ⚠️ IMPORTANTE: Selectores Preliminares

Los selectores actuales son genéricos. Deberán ajustarse según el HTML real de `producto.jsp`.

```python
# Datos básicos
name_selector = "h1.product-title, .product-name, h1"
description_selector = ".product-description, .descripcion, p.description"
brand_selector = ".product-brand, .marca, span.brand"
origin_selector = ".product-origin, .origen, span.origin"
price_selector = ".product-price, .precio, span.price, .n_neto"
stock_selector = ".product-stock, .stock, span.stock"

# Imágenes (busca en múltiples selectores)
image_selectors = [
    "img.product-image",
    ".product-gallery img",
    ".images img",
    "img[src*='imagen']"
]

# Datos adicionales
oem_selector = ".oem-codes, .codigos-oem, .equivalencias"
applications_selector = ".applications, .aplicaciones, .compatibility, .vehiculos"
```

### 🔍 Cómo Identificar los Selectores Reales

1. **Inspeccionar HTML**:
   - Abrir: `https://ecommerce.noriegavanzulli.cl/b2b/producto.jsp?codigo=006342`
   - Click derecho → Inspeccionar elemento
   - Identificar las clases CSS reales

2. **Usar Screenshots**:
   - El scraper guarda: `/tmp/noriega_product_{SKU}.png`
   - Comparar con HTML para validar extracción

3. **Actualizar código**:
   ```python
   # En products.py, método _extract_product_detail()
   name_selector = "h1.titulo-real"  # ← Reemplazar con clase real
   ```

---

## 🧪 Testing

### 1. Ejecutar con 1 Producto
```bash
# En backend/app/core/config.py o vía API
products_per_category: 1
scraping_speed_ms: 1000
```

### 2. Verificar Logs
```
📦 Producto 1/1: SKU 006342
   🔗 Navegando a: https://ecommerce.noriegavanzulli.cl/b2b/producto.jsp?codigo=006342
   ✓ Nombre: AMORTIGUADOR DELANTERO...
   ✓ Descripción: 150 caracteres
   ✓ Marca: KIC
   ✓ Origen: KOREA
   ✓ Precio: 17920.0
   ✓ Stock: 1
   ✓ Imágenes: 3 encontradas
   ✓ OEM: 2 códigos
   ✓ Aplicaciones: 5 vehículos
   📸 Screenshot guardado: /tmp/noriega_product_006342.png
   ✅ Extraído: AMORTIGUADOR DELANTERO...
```

### 3. Verificar Base de Datos
```sql
SELECT
    sku,
    name,
    brand,
    price,
    stock,
    image_url,
    images,
    extra_data
FROM products
WHERE sku = '006342';
```

**Resultado esperado**:
```json
{
  "sku": "006342",
  "name": "AMORTIGUADOR DELANTERO",
  "brand": "KIC",
  "price": 17920.0,
  "stock": 1,
  "image_url": "https://...",
  "images": ["https://...", "https://..."],
  "extra_data": {
    "origin": "KOREA",
    "oem": ["AB123456"],
    "applications": [...]
  }
}
```

---

## 📝 Próximos Pasos

### 1. Ajustar Selectores
- [ ] Inspeccionar `producto.jsp` con DevTools
- [ ] Identificar clases CSS reales
- [ ] Actualizar selectores en `_extract_product_detail()`
- [ ] Validar extracción completa

### 2. Optimizaciones
- [ ] Manejo de errores por producto (continuar si falla uno)
- [ ] Reintentos automáticos (3 intentos por producto)
- [ ] Cache de imágenes (evitar duplicados)
- [ ] Paginación (si hay más de 100 productos por categoría)

### 3. Producción
- [ ] Aumentar `products_per_category` a 100+
- [ ] Ajustar `scraping_speed_ms` según carga del servidor
- [ ] Implementar tareas Celery (async)
- [ ] Agregar progreso real-time en frontend

---

## 🐛 Troubleshooting

### Problema: "No se pudo extraer nombre"
**Solución**: El selector `h1.product-title` es incorrecto. Inspeccionar HTML y actualizar.

### Problema: "Imágenes: 0 encontradas"
**Solución**: Los selectores de imágenes no coinciden. Buscar `img` en el HTML de detalle.

### Problema: Scraping muy lento
**Solución**:
- Reducir `scraping_speed_ms` (min: 500ms)
- Reducir `products_per_category` para pruebas
- Usar Celery en producción (async)

### Problema: "Screenshot: Permission denied"
**Solución**: Crear directorio `/tmp` o cambiar ruta a `/Users/{user}/Desktop/screenshots/`

---

## 📚 Referencias

- **URL Lista**: `https://ecommerce.noriegavanzulli.cl/b2b/resultado_medida.jsp?medida={CATEGORIA}`
- **URL Detalle**: `https://ecommerce.noriegavanzulli.cl/b2b/producto.jsp?codigo={SKU}`
- **Código**: `backend/app/importers/noriega/products.py`
- **Método**: `_extract_product_detail(sku: str)`

---

## ✅ Estado Actual

- ✅ Navegación a páginas de detalle implementada
- ✅ Extracción de lista de SKUs
- ✅ Loop por cada producto con delay
- ✅ Screenshots automáticos
- ✅ Guardado en base de datos
- ⏳ **PENDIENTE**: Ajustar selectores según HTML real de `producto.jsp`

**Próximo paso**: Ejecutar scraper con 1 producto y revisar screenshot + logs para identificar selectores reales.
