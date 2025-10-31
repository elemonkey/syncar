# 📚 ARQUITECTURA COMPLETA DEL SISTEMA DE SCRAPING - SYNCAR 2.0

## 📋 Índice
1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Flujo de Scraping Detallado](#flujo-de-scraping-detallado)
4. [Manejo de Datos y Duplicados](#manejo-de-datos-y-duplicados)
5. [Componentes del Sistema](#componentes-del-sistema)
6. [Base de Datos](#base-de-datos)
7. [Frontend](#frontend)
8. [Casos de Uso](#casos-de-uso)

---

## 🎯 Visión General

SYNCAR 2.0 es una plataforma de importación automatizada de catálogos de productos desde múltiples proveedores (Noriega, Alsacia, Refax, Emasa). El sistema utiliza **web scraping** con Playwright para extraer datos de productos y almacenarlos en PostgreSQL.

### Características Principales:
- ✅ **Scraping Automatizado**: Usa Playwright + Celery para tareas en background
- ✅ **Multi-Proveedor**: Soporta 4 importadores diferentes
- ✅ **Gestión de Duplicados**: Actualiza productos existentes en lugar de duplicarlos
- ✅ **Control de Velocidad**: Configurable (productos por minuto)
- ✅ **Límites Configurables**: Puedes limitar cuántos productos scrappear por categoría
- ✅ **Tracking en Tiempo Real**: Progreso visible en el frontend
- ✅ **Cancelación Manual**: Puedes detener jobs en ejecución

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                    │
│  - React Components                                          │
│  - API Client (fetch)                                        │
│  - Real-time Progress Tracking                              │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP REST API
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              API Endpoints (/api/v1)                  │  │
│  │  - /importers/{name}/import-categories                │  │
│  │  - /importers/{name}/import-products                  │  │
│  │  - /importers/status/{job_id}                         │  │
│  └────────────────┬──────────────────────────────────────┘  │
│                   │                                          │
│                   ▼                                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         CELERY TASKS (Background Jobs)                │  │
│  │  - import_categories_task()                           │  │
│  │  - import_products_task()                             │  │
│  └────────────────┬──────────────────────────────────────┘  │
│                   │                                          │
│                   ▼                                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            IMPORTERS (Modular Components)             │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Base Classes (Abstract)                        │  │  │
│  │  │  - AuthComponent                                │  │  │
│  │  │  - CategoriesComponent                          │  │  │
│  │  │  - ProductsComponent                            │  │  │
│  │  │  - ConfigComponent                              │  │  │
│  │  └──────────────┬──────────────────────────────────┘  │  │
│  │                 │ Inherited by                         │  │
│  │                 ▼                                       │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Noriega Implementation                         │  │  │
│  │  │  - NoriegaAuthComponent                         │  │  │
│  │  │  - NoriegaCategoriesComponent                   │  │  │
│  │  │  - NoriegaProductsComponent                     │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │  (Alsacia, Refax, Emasa tienen sus propias clases)    │  │
│  └────────────────┬──────────────────────────────────────┘  │
│                   │                                          │
│                   ▼                                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         PLAYWRIGHT (Web Scraping Engine)              │  │
│  │  - Browser Control                                    │  │
│  │  - Page Navigation                                    │  │
│  │  - DOM Manipulation                                   │  │
│  │  - Screenshot Capture                                 │  │
│  └────────────────┬──────────────────────────────────────┘  │
└───────────────────┼──────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATABASE (PostgreSQL)                       │
│  Tables:                                                     │
│  - importers                                                 │
│  - importer_configs                                          │
│  - categories                                                │
│  - products                                                  │
│  - import_jobs                                               │
│  - job_logs                                                  │
│  - users, roles, permissions                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Scraping Detallado

### 📦 CASO 1: Primera Importación de Categorías

```
Usuario Frontend                API FastAPI              Celery Worker            Playwright           PostgreSQL
    │                              │                         │                       │                    │
    │──(1) POST /importers/────────▶│                         │                       │                    │
    │    noriega/import-categories  │                         │                       │                    │
    │                              │                         │                       │                    │
    │                              │──(2) Verify Importer───▶│                       │                    │
    │                              │    in DB                 │                       │                    │
    │                              │◀────────────────────────│                       │                    │
    │                              │                         │                       │                    │
    │                              │──(3) Start Celery Task─▶│                       │                    │
    │                              │    (job_id: uuid)        │                       │                    │
    │                              │                         │                       │                    │
    │◀──(4) Response: job_id───────│                         │                       │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(5) Create ImportJob────────────────────▶│
    │                              │                         │    (status: RUNNING)   │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(6) Launch Browser──▶│                    │
    │                              │                         │    (headless mode)     │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(7) NoriegaAuthComponent                  │
    │                              │                         │    .execute()         │                    │
    │                              │                         │                       │──(8) goto login   │
    │                              │                         │                       │    page            │
    │                              │                         │                       │                    │
    │                              │                         │                       │──(9) fill form    │
    │                              │                         │                       │    (rut, user,     │
    │                              │                         │                       │     password)      │
    │                              │                         │                       │                    │
    │                              │                         │                       │──(10) click submit │
    │                              │                         │                       │                    │
    │                              │                         │                       │◀─(11) redirect to  │
    │                              │                         │                       │      dashboard     │
    │                              │                         │                       │                    │
    │                              │                         │◀─(12) Auth Success───│                    │
    │                              │                         │    (page, context)    │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(13) NoriegaCategoriesComponent           │
    │                              │                         │    .execute()         │                    │
    │                              │                         │                       │                    │
    │                              │                         │                       │──(14) goto         │
    │                              │                         │                       │    categories page │
    │                              │                         │                       │                    │
    │                              │                         │                       │──(15) wait for     │
    │                              │                         │                       │    table load      │
    │                              │                         │                       │                    │
    │                              │                         │                       │──(16) extract data │
    │                              │                         │                       │    from table rows │
    │                              │                         │                       │                    │
    │                              │                         │◀─(17) Categories[]────│                    │
    │                              │                         │    [{name, url, ...}] │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(18) Save Categories────────────────────▶│
    │                              │                         │    FOREACH category:   │                    │
    │                              │                         │    - Check if exists   │◀────(19) Query────│
    │                              │                         │    - INSERT if new     │                    │
    │                              │                         │    - UPDATE if exists  │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(20) Update Job──────────────────────────▶│
    │                              │                         │    status: COMPLETED   │                    │
    │                              │                         │    progress: 100       │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(21) Close Browser──▶│                    │
    │                              │                         │                       │                    │
    │──(22) GET /importers/────────▶│                         │                       │                    │
    │     status/{job_id}           │──(23) Query Job───────────────────────────────────────────────────▶│
    │                              │◀──────────────────────────────────────────────────(24) Job data────│
    │◀─(25) {status: COMPLETED}────│                         │                       │                    │
    │     {categories: 45}          │                         │                       │                    │
```

### 🛍️ CASO 2: Primera Importación de Productos

```
Usuario Frontend                API FastAPI              Celery Worker            Playwright           PostgreSQL
    │                              │                         │                       │                    │
    │──(1) POST /importers/────────▶│                         │                       │                    │
    │    noriega/import-products    │                         │                       │                    │
    │    Body: {                    │                         │                       │                    │
    │      selected_categories: [   │                         │                       │                    │
    │        "123", "456", "789"    │                         │                       │                    │
    │      ]                        │                         │                       │                    │
    │    }                          │                         │                       │                    │
    │                              │                         │                       │                    │
    │                              │──(2) Verify Importer───▶│                       │                    │
    │                              │    & Categories          │                       │                    │
    │                              │                         │                       │                    │
    │                              │──(3) Generate job_id────│                       │                    │
    │                              │    (UUID)                │                       │                    │
    │                              │                         │                       │                    │
    │                              │──(4) Start Celery Task─▶│                       │                    │
    │                              │    with job_id           │                       │                    │
    │                              │                         │                       │                    │
    │◀──(5) Response: job_id───────│                         │                       │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(6) Create ImportJob────────────────────▶│
    │                              │                         │    (status: RUNNING)   │                    │
    │                              │                         │    params: {selected_  │                    │
    │                              │                         │      categories}       │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(7) Load Config──────────────────────────▶│
    │                              │                         │◀───(8) {              │                    │
    │                              │                         │    products_per_cat:   │                    │
    │                              │                         │      100,              │                    │
    │                              │                         │    scraping_speed_ms:  │                    │
    │                              │                         │      1000              │                    │
    │                              │                         │    }                   │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(9) Launch Browser──▶│                    │
    │                              │                         │                       │                    │
    │                              │                         │──(10) Auth (same as   │                    │
    │                              │                         │    categories flow)   │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(11) NoriegaProductsComponent             │
    │                              │                         │    .execute()         │                    │
    │                              │                         │                       │                    │
    │                              │                         │    FOREACH category:  │                    │
    │                              │                         │                       │                    │
    │                              │                         │    ┌─────────────────────────────────────┐│
    │                              │                         │    │ (12) Get Category from DB          ││
    │                              │                         │    │      by ID                         ││
    │                              │                         │    │◀──────────────────────────────────┐││
    │                              │                         │    │                                   │││
    │                              │                         │    │ (13) Build Category URL           │││
    │                              │                         │    │      (por medida o fabricante)    │││
    │                              │                         │    │                                   │││
    │                              │                         │    │                  │                │││
    │                              │                         │    │──(14) goto URL──▶│                │││
    │                              │                         │    │                  │                │││
    │                              │                         │    │                  │──(15) wait for │││
    │                              │                         │    │                  │    product list│││
    │                              │                         │    │                  │                │││
    │                              │                         │    │                  │──(16) extract  │││
    │                              │                         │    │                  │    SKU list    │││
    │                              │                         │    │◀─(17) [SKU1,     │                │││
    │                              │                         │    │       SKU2, ...]  │                │││
    │                              │                         │    │                                   │││
    │                              │                         │    │ FOREACH SKU (max: products_per_  │││
    │                              │                         │    │                   category):      │││
    │                              │                         │    │                                   │││
    │                              │                         │    │   ┌──────────────────────────────┐│││
    │                              │                         │    │   │ (18) goto product detail    ││││
    │                              │                         │    │   │      page                    ││││
    │                              │                         │    │   │      /producto.jsp?         ││││
    │                              │                         │    │   │      codigo={SKU}           ││││
    │                              │                         │    │   │                  │          ││││
    │                              │                         │    │   │──(19) Extract:──▶│          ││││
    │                              │                         │    │   │      - name      │          ││││
    │                              │                         │    │   │      - desc      │          ││││
    │                              │                         │    │   │      - price     │          ││││
    │                              │                         │    │   │      - stock     │          ││││
    │                              │                         │    │   │      - brand     │          ││││
    │                              │                         │    │   │      - images    │          ││││
    │                              │                         │    │   │      - oem       │          ││││
    │                              │                         │    │   │      - apps      │          ││││
    │                              │                         │    │   │                  │          ││││
    │                              │                         │    │   │◀─(20) Product────│          ││││
    │                              │                         │    │   │      Data        │          ││││
    │                              │                         │    │   │                             ││││
    │                              │                         │    │   │ (21) Sleep                  ││││
    │                              │                         │    │   │      (1000ms)               ││││
    │                              │                         │    │   └─────────────────────────────┘│││
    │                              │                         │    │                                   │││
    │                              │                         │    │ (22) Save Products to DB          │││
    │                              │                         │    │──────────────────────────────────▶│││
    │                              │                         │    │                                    ││
    │                              │                         │    │ FOREACH product:                   ││
    │                              │                         │    │   - Query by SKU───────────────────▶│
    │                              │                         │    │◀──- If exists: UPDATE             ││
    │                              │                         │    │   - If new: INSERT                 ││
    │                              │                         │    │                                    ││
    │                              │                         │    │ (23) Update category.product_count ││
    │                              │                         │    │──────────────────────────────────▶ ││
    │                              │                         │    └────────────────────────────────────┘│
    │                              │                         │                       │                    │
    │                              │                         │──(24) Update Job──────────────────────────▶│
    │                              │                         │    progress: X%        │                    │
    │                              │                         │    result: {           │                    │
    │                              │                         │      current_item,     │                    │
    │                              │                         │      current_sku       │                    │
    │                              │                         │    }                   │                    │
    │                              │                         │                       │                    │
    │──(25) Polling: GET /status───▶│──(26) Query Job───────────────────────────────────────────────────▶│
    │     /{job_id}                 │◀──────────────────────────────────────────────(27) Job data────────│
    │◀─(28) {progress: 45%}─────────│                         │                       │                    │
    │                              │                         │                       │                    │
    │                              │                         │──(29) Close Browser──▶│                    │
    │                              │                         │                       │                    │
    │                              │                         │──(30) Update Job──────────────────────────▶│
    │                              │                         │    status: COMPLETED   │                    │
    │                              │                         │    progress: 100       │                    │
    │                              │                         │    result: {           │                    │
    │                              │                         │      products_count,   │                    │
    │                              │                         │      categories_proc   │                    │
    │                              │                         │    }                   │                    │
```

### 🔁 CASO 3: Re-scraping (Segunda Importación del Mismo Importador)

**¿Qué pasa si vuelvo a scrapear el mismo importador/proveedor?**

```python
# En _save_products() (noriega/products.py, línea 905)

for product_data in products:
    # 🔍 BUSCAR SI EL PRODUCTO YA EXISTE (por SKU)
    result = await self.db.execute(
        select(Product).where(
            Product.importer_id == category.importer_id,
            Product.sku == product_data["sku"],
        )
    )
    existing_product = result.scalar_one_or_none()

    if existing_product:
        # ✅ PRODUCTO EXISTE -> ACTUALIZAR
        for key, value in product_data.items():
            if hasattr(existing_product, key):
                setattr(existing_product, key, value)
        existing_product.last_scraped_at = func.now()
        logger.info(f"✓ Actualizado: {product_data.get('name')}")
    else:
        # ✅ PRODUCTO NUEVO -> INSERTAR
        new_product = Product(
            importer_id=category.importer_id,
            category_id=category.id,
            sku=product_data.get("sku"),
            name=product_data.get("name"),
            # ... otros campos
        )
        self.db.add(new_product)
        logger.info(f"✓ Nuevo: {product_data.get('name')}")

    await self.db.commit()
```

#### **Comportamiento en Re-scraping:**

1. **Primera Importación** (categoría "Frenos"):
   ```
   - Scrapea 100 productos
   - Inserta 100 registros nuevos en la BD
   - category.product_count = 100
   ```

2. **Segunda Importación** (misma categoría "Frenos"):
   ```
   - Scrapea los mismos 100 productos
   - Encuentra que todos ya existen (por SKU)
   - Actualiza los 100 registros existentes:
     * Precio actualizado (si cambió)
     * Stock actualizado (si cambió)
     * Descripción actualizada (si cambió)
     * last_scraped_at = NOW()
   - NO crea duplicados
   - category.product_count sigue siendo 100
   ```

3. **¿Qué pasa si selecciono nuevas categorías?**
   ```
   Primera vez: "Frenos" (100 productos)
   Segunda vez: "Frenos" + "Embragues" (100 + 150 productos)

   Resultado:
   - "Frenos": 100 productos actualizados
   - "Embragues": 150 productos nuevos insertados
   - Total en BD: 250 productos
   ```

4. **¿Qué pasa si el proveedor eliminó un producto?**
   ```
   - El producto NO será scapeado
   - El registro permanece en la BD
   - El campo last_scraped_at NO se actualiza
   - Puedes detectar productos obsoletos por last_scraped_at antiguo
   ```

---

## 🔧 Componentes del Sistema

### 1. Base Classes (Abstractas)

**Ubicación:** `backend/app/importers/base.py`

#### `ImporterComponentBase`
Clase base abstracta para todos los componentes. Define:
- `execute()`: Método abstracto que deben implementar todas las subclases
- `update_progress()`: Actualiza el progreso en BD y logs
- `is_job_cancelled()`: Verifica si el usuario canceló el job
- `mark_job_status()`: Marca el estado del job (RUNNING, COMPLETED, FAILED)

#### `AuthComponent`
Responsable de:
- Login en el sitio del proveedor
- Guardar session/cookies
- Dejar la página lista en dashboard

#### `CategoriesComponent`
Responsable de:
- Navegar a URL de categorías
- Extraer datos de categorías (nombre, slug, URL, tipo)
- Almacenar en tabla `categories`

#### `ConfigComponent`
Responsable de:
- Leer configuración del importador desde BD
- Aplicar límites y velocidad

#### `ProductsComponent`
Responsable de:
- Iterar por categorías seleccionadas
- Para cada categoría:
  * Construir URLs de productos
  * Navegar a cada URL
  * Extraer información completa
  * Almacenar/actualizar en tabla `products`
  * Respetar límites y delays

### 2. Noriega Implementation

**Ubicación:** `backend/app/importers/noriega/`

#### `NoriegaAuthComponent`
```python
async def execute(self) -> Dict[str, Any]:
    # 1. Crear contexto del navegador
    context = await browser.new_context()
    page = await context.new_page()

    # 2. Navegar a login
    await page.goto("https://ecommerce.noriegavanzulli.cl/b2b/loginvip.jsp")

    # 3. Completar formulario
    await page.fill('input[name="trut"]', credentials["rut"])
    await page.fill('input[name="tuser"]', credentials["username"])
    await page.fill('input[name="tpass"]', credentials["password"])

    # 4. Submit
    await page.click('input[name="Ingresar"]')

    # 5. Cerrar modal si existe
    # ... lógica de detección de modal

    return {
        "success": True,
        "page": page,
        "context": context
    }
```

#### `NoriegaCategoriesComponent`
```python
async def execute(self) -> Dict[str, Any]:
    # 1. Navegar a página de categorías
    await page.goto("https://ecommerce.noriegavanzulli.cl/b2b/consultacodigos.jsp")

    # 2. Extraer datos de la tabla
    rows = await page.query_selector_all("table tr")
    categories = []

    for row in rows:
        name = await row.query_selector("td:nth-child(1)")
        tipo = await row.query_selector("td:nth-child(2)")
        # ... extraer más datos

        categories.append({
            "name": name_text,
            "tipo": tipo_text,
            "url": self._build_category_url(name_text, tipo_text)
        })

    # 3. Guardar en BD
    for cat_data in categories:
        # Buscar si existe
        existing = await db.execute(
            select(Category).where(
                Category.importer_id == importer.id,
                Category.name == cat_data["name"]
            )
        )

        if existing:
            # Actualizar
            existing.url = cat_data["url"]
        else:
            # Insertar
            new_cat = Category(**cat_data)
            db.add(new_cat)

    await db.commit()

    return {
        "success": True,
        "categories": categories,
        "count": len(categories)
    }
```

#### `NoriegaProductsComponent`
```python
async def execute(self) -> Dict[str, Any]:
    total_products = 0

    # Por cada categoría seleccionada
    for category_id in selected_categories:
        # 1. Obtener categoría de BD
        category = await db.get(Category, category_id)

        # 2. Construir URL según tipo
        if category.tipo == "POR_MEDIDA":
            url = f"https://...?medida={category.name}"
        else:
            url = f"https://...?fabricante={category.name}"

        # 3. Navegar
        await page.goto(url)

        # 4. Extraer lista de SKUs
        skus = await self._extract_sku_list()

        # 5. Limitar si es necesario
        if self.products_per_category:
            skus = skus[:self.products_per_category]

        # 6. Por cada SKU
        products = []
        for sku in skus:
            # 6.1 Navegar a detalle
            await page.goto(f"https://.../producto.jsp?codigo={sku}")

            # 6.2 Extraer datos
            product_data = await self._extract_product_detail(sku)
            products.append(product_data)

            # 6.3 Respetar velocidad
            await asyncio.sleep(self.scraping_speed_ms / 1000)

        # 7. Guardar productos en BD
        await self._save_products(products, category)

        total_products += len(products)

    return {
        "success": True,
        "products_count": total_products
    }

async def _extract_product_detail(self, sku: str) -> Dict:
    """Extrae todos los datos de un producto"""
    data = {"sku": sku}

    # Nombre
    name_elem = await page.query_selector("#titulo")
    data["name"] = await name_elem.text_content()

    # Precio
    price_elem = await page.query_selector("#precio_lista .valor")
    data["price"] = self._parse_price(await price_elem.text_content())

    # Stock
    stock_elem = await page.query_selector("#disponibilidad")
    data["stock"] = self._parse_stock(await stock_elem.text_content())

    # Marca
    brand_elem = await page.query_selector("#marca")
    data["brand"] = await brand_elem.text_content()

    # Imágenes
    images = []
    img_elements = await page.query_selector_all("#fotos img")
    for img in img_elements:
        src = await img.get_attribute("src")
        images.append(src)
    data["images"] = images

    # OEM
    oem_elem = await page.query_selector("#numero_original")
    oem2_elem = await page.query_selector("#numero_fabrica")
    data["extra_data"] = {
        "oem": [await oem_elem.text_content(), await oem2_elem.text_content()]
    }

    # Aplicaciones (tabla)
    apps = []
    rows = await page.query_selector_all("table.tablaAA tbody tr.contenidoAA")
    for row in rows:
        cells = await row.query_selector_all("td")
        app = {
            "car_brand": await cells[0].text_content(),
            "car_model": await cells[1].text_content(),
            "year_start": int(await cells[2].text_content()),
            "year_end": int(await cells[3].text_content()),
        }
        apps.append(app)
    data["extra_data"]["applications"] = apps

    return data

async def _save_products(self, products: List[Dict], category: Category):
    """Guarda o actualiza productos en BD"""
    for product_data in products:
        # 🔍 BUSCAR PRODUCTO EXISTENTE POR SKU
        result = await db.execute(
            select(Product).where(
                Product.importer_id == category.importer_id,
                Product.sku == product_data["sku"]
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # ✅ ACTUALIZAR
            for key, value in product_data.items():
                setattr(existing, key, value)
            existing.last_scraped_at = func.now()
            logger.info(f"✓ Actualizado: {product_data['name']}")
        else:
            # ✅ INSERTAR NUEVO
            new_product = Product(
                importer_id=category.importer_id,
                category_id=category.id,
                **product_data
            )
            db.add(new_product)
            logger.info(f"✓ Nuevo: {product_data['name']}")

    await db.commit()
```

### 3. Orchestrator

**Ubicación:** `backend/app/importers/orchestrator.py`

Orquesta la ejecución de componentes en el orden correcto:

```python
class ImportOrchestrator:
    async def import_categories(self):
        # 1. Autenticación
        auth_component = AuthComponent(...)
        auth_result = await auth_component.execute()

        # 2. Categorías
        categories_component = CategoriesComponent(...)
        result = await categories_component.execute()

        return result

    async def import_products(self, selected_categories):
        # 1. Autenticación
        auth_component = AuthComponent(...)
        auth_result = await auth_component.execute()

        # 2. Configuración
        config_component = ConfigComponent(...)
        config = await config_component.execute()

        # 3. Productos
        products_component = ProductsComponent(..., config)
        result = await products_component.execute()

        return result
```

### 4. Celery Tasks

**Ubicación:** `backend/app/tasks/import_tasks.py`

```python
@celery_app.task(name="import_categories")
def import_categories_task(importer_name: str):
    job_id = str(uuid.uuid4())

    # Crear event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(
            _run_import_categories(importer_name, job_id)
        )
    finally:
        loop.close()

async def _run_import_categories(importer_name: str, job_id: str):
    async with AsyncSessionLocal() as db:
        # 1. Crear ImportJob
        job = ImportJob(
            job_id=job_id,
            importer_id=importer.id,
            job_type=JobType.CATEGORIES,
            status=JobStatus.RUNNING
        )
        db.add(job)
        await db.commit()

        # 2. Ejecutar con Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            try:
                # 3. Usar componentes específicos
                auth = NoriegaAuthComponent(...)
                auth_result = await auth.execute()

                categories = NoriegaCategoriesComponent(...)
                result = await categories.execute()

                # 4. Actualizar job
                job.status = JobStatus.COMPLETED
                job.result = result
                await db.commit()

                return result
            finally:
                await browser.close()
```

---

## 💾 Base de Datos

### Schema Completo

```sql
-- Tabla de importadores
CREATE TABLE importers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,  -- NORIEGA, ALSACIA, REFAX, EMASA
    display_name VARCHAR(100) NOT NULL,
    base_url VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Configuración de cada importador
CREATE TABLE importer_configs (
    id SERIAL PRIMARY KEY,
    importer_id INTEGER REFERENCES importers(id) UNIQUE,
    credentials JSONB,  -- {rut, username, password}
    is_active BOOLEAN DEFAULT TRUE,
    products_per_category INTEGER,  -- NULL = sin límite, scrapea todos
    scraping_speed_ms INTEGER DEFAULT 1000,  -- Delay entre productos
    category_order JSONB,  -- Orden preferido de categorías
    extra_config JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Categorías de productos
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    importer_id INTEGER REFERENCES importers(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    url VARCHAR(500),
    external_id VARCHAR(100),
    product_count INTEGER DEFAULT 0,
    selected BOOLEAN DEFAULT FALSE,  -- Usuario seleccionó esta categoría
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(importer_id, name)
);

-- Productos
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    importer_id INTEGER REFERENCES importers(id),
    category_id INTEGER REFERENCES categories(id),

    -- Identificación
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,

    -- Precios
    price FLOAT,
    original_price FLOAT,
    currency VARCHAR(10) DEFAULT 'CLP',

    -- Stock
    stock INTEGER,
    available BOOLEAN DEFAULT TRUE,

    -- Metadata
    external_id VARCHAR(100),
    url VARCHAR(500),
    image_url VARCHAR(500),
    images JSONB,  -- Array de URLs
    brand VARCHAR(100),
    model VARCHAR(100),
    year_start INTEGER,
    year_end INTEGER,

    -- Datos adicionales flexibles
    extra_data JSONB,  -- {origin, oem[], applications[], characteristics[]}

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_scraped_at TIMESTAMP,  -- Última vez que se scrapeo este producto

    UNIQUE(importer_id, sku)  -- ⚠️ CLAVE: Evita duplicados
);

-- Jobs de importación
CREATE TABLE import_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(100) UNIQUE NOT NULL,  -- UUID
    importer_id INTEGER REFERENCES importers(id),
    job_type VARCHAR(20) NOT NULL,  -- 'categories' o 'products'
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, running, completed, failed, cancelled
    params JSONB,  -- {selected_categories: [...]}
    progress INTEGER DEFAULT 0,  -- 0-100
    total_items INTEGER,
    processed_items INTEGER DEFAULT 0,
    result JSONB,  -- Resultado final
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Logs de los jobs
CREATE TABLE job_logs (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES import_jobs(id),
    level VARCHAR(20) NOT NULL,  -- INFO, WARNING, ERROR
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### Índices Importantes

```sql
-- Para búsquedas rápidas de productos
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_importer_sku ON products(importer_id, sku);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_brand ON products(brand);

-- Para tracking de jobs
CREATE INDEX idx_jobs_status ON import_jobs(status);
CREATE INDEX idx_jobs_job_id ON import_jobs(job_id);

-- Para categorías
CREATE INDEX idx_categories_importer ON categories(importer_id);
CREATE INDEX idx_categories_selected ON categories(selected);
```

---

## 🖥️ Frontend

### Páginas Principales

#### 1. Dashboard (`/dashboard`)
- Muestra resumen de productos
- Gráficos de inventario
- Links rápidos a importación

#### 2. Catálogo (`/catalogo`)
- Lista todos los productos
- Filtros por importador y categoría
- Búsqueda por nombre, SKU, marca

#### 3. Importadores (`/importers`)
**Componente clave para iniciar scraping**

```tsx
// frontend/app/importers/page.tsx

export default function ImportersPage() {
  const [selectedImporter, setSelectedImporter] = useState("noriega");
  const [categories, setCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [jobId, setJobId] = useState(null);
  const [progress, setProgress] = useState(0);

  // 1. Cargar categorías del importador
  const loadCategories = async () => {
    const response = await fetch(
      `/api/v1/importers/categories?importer=${selectedImporter}`
    );
    const data = await response.json();
    setCategories(data.categories);
  };

  // 2. Iniciar importación de categorías
  const startCategoryImport = async () => {
    const response = await fetch(
      `/api/v1/importers/${selectedImporter}/import-categories`,
      { method: "POST" }
    );
    const data = await response.json();
    setJobId(data.job_id);

    // Iniciar polling
    pollJobStatus(data.job_id);
  };

  // 3. Iniciar importación de productos
  const startProductImport = async () => {
    const response = await fetch(
      `/api/v1/importers/${selectedImporter}/import-products`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          selected_categories: selectedCategories
        })
      }
    );
    const data = await response.json();
    setJobId(data.job_id);

    // Iniciar polling
    pollJobStatus(data.job_id);
  };

  // 4. Polling de estado del job
  const pollJobStatus = (jobId) => {
    const interval = setInterval(async () => {
      const response = await fetch(`/api/v1/importers/status/${jobId}`);
      const data = await response.json();

      setProgress(data.progress);

      if (data.status === "completed" || data.status === "failed") {
        clearInterval(interval);
      }
    }, 1000);  // Poll cada 1 segundo
  };

  return (
    <div>
      {/* Selector de importador */}
      <select value={selectedImporter} onChange={(e) => setSelectedImporter(e.target.value)}>
        <option value="noriega">Noriega</option>
        <option value="alsacia">Alsacia</option>
        <option value="refax">Refax</option>
        <option value="emasa">Emasa</option>
      </select>

      {/* Botón para importar categorías */}
      <button onClick={startCategoryImport}>
        Importar Categorías
      </button>

      {/* Lista de categorías con checkboxes */}
      {categories.map((cat) => (
        <label key={cat.id}>
          <input
            type="checkbox"
            checked={selectedCategories.includes(cat.id)}
            onChange={(e) => {
              if (e.target.checked) {
                setSelectedCategories([...selectedCategories, cat.id]);
              } else {
                setSelectedCategories(selectedCategories.filter(id => id !== cat.id));
              }
            }}
          />
          {cat.name} ({cat.product_count} productos)
        </label>
      ))}

      {/* Botón para importar productos */}
      <button onClick={startProductImport} disabled={selectedCategories.length === 0}>
        Importar Productos ({selectedCategories.length} categorías)
      </button>

      {/* Barra de progreso */}
      {jobId && (
        <div>
          <progress value={progress} max={100}></progress>
          <p>{progress}% completado</p>
        </div>
      )}
    </div>
  );
}
```

#### 4. Configuración (`/configuracion`)
- **Tab Usuarios**: Gestión de usuarios y roles
- **Tab Roles y Permisos**: Asignar permisos a roles
- **Tab Importadores**: Configurar credenciales, límites y velocidad

```tsx
// Ejemplo de configuración guardada:
{
  "id": "noriega",
  "name": "NORIEGA",
  "rut": "12345678-9",
  "username": "admin",
  "password": "********",
  "enabled": true,
  "categoryLimit": 100,  // Max productos por categoría
  "productsPerMinute": 60  // = 1000ms entre productos
}
```

---

## 📊 Casos de Uso Completos

### Caso de Uso 1: Importar Catálogo Completo de Noriega (Primera Vez)

```
PASO 1: Configurar Credenciales
├─ Usuario va a /configuracion → Tab Importadores
├─ Completa:
│  ├─ RUT: 12345678-9
│  ├─ Usuario: admin
│  ├─ Password: ********
│  ├─ Límite por categoría: 100
│  └─ Velocidad: 60 productos/min
└─ Click en "Guardar"

PASO 2: Importar Categorías
├─ Usuario va a /importers
├─ Selecciona importador: Noriega
├─ Click en "Importar Categorías"
├─ Backend:
│  ├─ Crea job en BD (status: RUNNING)
│  ├─ Lanza tarea Celery
│  ├─ Playwright abre navegador
│  ├─ Login en Noriega
│  ├─ Navega a página de categorías
│  ├─ Extrae 45 categorías
│  └─ Guarda en tabla categories
├─ Frontend muestra progreso: 100%
└─ Resultado: 45 categorías disponibles

PASO 3: Seleccionar Categorías
├─ Usuario ve lista de 45 categorías
├─ Selecciona 5 categorías:
│  ├─ [✓] Frenos (150 productos)
│  ├─ [✓] Embragues (200 productos)
│  ├─ [✓] Suspensión (180 productos)
│  ├─ [✓] Filtros (220 productos)
│  └─ [✓] Aceites (90 productos)
└─ Total estimado: 840 productos

PASO 4: Importar Productos
├─ Click en "Importar Productos (5 categorías)"
├─ Backend:
│  ├─ Crea job en BD (status: RUNNING)
│  ├─ Lanza tarea Celery
│  ├─ Playwright abre navegador
│  ├─ Login en Noriega
│  ├─ POR CADA CATEGORÍA:
│  │  ├─ Navega a lista de productos
│  │  ├─ Extrae SKUs (máx 100 por límite)
│  │  ├─ POR CADA SKU:
│  │  │  ├─ Navega a detalle
│  │  │  ├─ Extrae datos completos
│  │  │  ├─ Espera 1000ms (60/min)
│  │  │  └─ Guarda en BD (INSERT)
│  │  └─ Actualiza category.product_count
│  └─ Cierra navegador
├─ Frontend muestra progreso en tiempo real:
│  ├─ 0%: Autenticando...
│  ├─ 10%: Procesando Frenos (1/5)
│  ├─ 30%: Producto 45/100 - SKU 12345
│  ├─ 50%: Procesando Embragues (2/5)
│  └─ 100%: Completado
└─ Resultado: 500 productos insertados (100 por categoría)
```

### Caso de Uso 2: Actualizar Precios (Re-scraping)

```
PASO 1: Usuario vuelve a /importers
PASO 2: Selecciona las mismas 5 categorías
PASO 3: Click en "Importar Productos (5 categorías)"
PASO 4: Backend:
├─ Scrapea las mismas categorías
├─ POR CADA PRODUCTO:
│  ├─ Busca en BD por (importer_id, sku)
│  ├─ Producto YA EXISTE
│  ├─ ACTUALIZA:
│  │  ├─ price: 15990 → 17990 (aumentó)
│  │  ├─ stock: 5 → 3 (disminuyó)
│  │  ├─ description: [actualizada]
│  │  └─ last_scraped_at: NOW()
│  └─ NO CREA DUPLICADO
└─ Resultado: 500 productos actualizados, 0 nuevos
```

### Caso de Uso 3: Agregar Nuevas Categorías

```
PASO 1: Usuario selecciona categorías diferentes
├─ Categorías anteriores: Frenos, Embragues, Suspensión, Filtros, Aceites
├─ Nuevas categorías: Frenos (mantiene), Transmisión (nueva), Motor (nueva)
└─ Total: 3 categorías

PASO 2: Click en "Importar Productos"
PASO 3: Backend:
├─ Categoría "Frenos":
│  ├─ 100 productos encontrados
│  ├─ Todos existen en BD
│  └─ 100 actualizados
├─ Categoría "Transmisión":
│  ├─ 150 productos encontrados
│  ├─ Todos son nuevos
│  └─ 150 insertados
└─ Categoría "Motor":
   ├─ 200 productos encontrados
   ├─ Todos son nuevos
   └─ 200 insertados

PASO 4: Resultado Final en BD:
├─ Productos de scraping anterior: 500
├─ Productos actualizados: 100
├─ Productos nuevos: 350
└─ Total en BD: 850 productos
```

### Caso de Uso 4: Producto Descontinuado en Proveedor

```
Situación:
├─ Primera importación: Producto SKU "ABC123" existe
├─ Proveedor elimina el producto de su catálogo
└─ Segunda importación: Producto SKU "ABC123" no se scrapea

Resultado:
├─ Registro en BD:
│  ├─ id: 456
│  ├─ sku: "ABC123"
│  ├─ name: "Pastillas de Freno"
│  ├─ last_scraped_at: 2025-10-01 (fecha antigua)
│  └─ [todos los demás datos intactos]
└─ El producto NO se elimina, permanece en BD

Detección de productos obsoletos:
SELECT *
FROM products
WHERE last_scraped_at < NOW() - INTERVAL '30 days';
```

---

## 🔍 Monitoreo y Debugging

### Logs del Sistema

```bash
# Ver logs del backend
tail -f backend/logs/app.log

# Ver logs de Celery
tail -f backend/logs/celery.log

# Ver logs de un job específico
SELECT * FROM job_logs WHERE job_id = 123 ORDER BY timestamp DESC;
```

### Screenshots de Debug

Playwright captura screenshots automáticamente:
```python
# En NoriegaAuthComponent
await page.screenshot(path="/tmp/noriega_antes_login.png")
await page.screenshot(path="/tmp/noriega_despues_completar.png")

# En NoriegaProductsComponent
await page.screenshot(path=f"/tmp/noriega_category_{index}_{category_name}.png")
```

### Tracking de Jobs en BD

```sql
-- Ver todos los jobs
SELECT
    job_id,
    job_type,
    status,
    progress,
    processed_items,
    total_items,
    created_at,
    completed_at
FROM import_jobs
ORDER BY created_at DESC;

-- Ver logs de un job
SELECT
    level,
    message,
    timestamp
FROM job_logs
WHERE job_id = (SELECT id FROM import_jobs WHERE job_id = 'uuid-aqui')
ORDER BY timestamp DESC;

-- Ver productos por importador
SELECT
    i.name AS importador,
    COUNT(p.id) AS total_productos,
    COUNT(DISTINCT p.category_id) AS categorias_con_productos,
    MAX(p.last_scraped_at) AS ultimo_scraping
FROM products p
JOIN importers i ON p.importer_id = i.id
GROUP BY i.name;
```

---

## ⚙️ Configuración Avanzada

### Variables de Entorno

```bash
# .env
HEADLESS=true  # false para ver el navegador en desarrollo
SCRAPING_MODE=prod  # 'dev' o 'prod'

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=syncar_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
```

### Límites Recomendados

```python
# Para desarrollo/testing
products_per_category: 10  # Solo 10 productos por categoría
scraping_speed_ms: 500  # 0.5 segundos entre productos (120/min)

# Para producción normal
products_per_category: 100  # 100 productos por categoría
scraping_speed_ms: 1000  # 1 segundo entre productos (60/min)

# Para scraping completo (sin límites)
products_per_category: None  # Scrapea todos los productos
scraping_speed_ms: 2000  # 2 segundos entre productos (30/min, más seguro)
```

### Manejo de Errores

```python
# Los componentes manejan errores automáticamente:

try:
    result = await component.execute()
except Exception as e:
    logger.error(f"Error: {e}")
    job.status = JobStatus.FAILED
    job.error_message = str(e)
    await db.commit()

    # Cerrar navegador
    await browser.close()
```

---

## 📈 Métricas y Performance

### Tiempos Estimados

```
Importación de Categorías (45 categorías):
├─ Autenticación: 5-10 segundos
├─ Navegación: 2-3 segundos
├─ Scraping tabla: 3-5 segundos
└─ Guardado en BD: 1-2 segundos
TOTAL: ~15-20 segundos

Importación de Productos (100 productos/categoría):
├─ Autenticación: 5-10 segundos
├─ Por categoría:
│  ├─ Navegación: 2-3 segundos
│  ├─ Extracción SKUs: 1-2 segundos
│  └─ Por producto (100x):
│     ├─ Navegación: 1-2 segundos
│     ├─ Scraping: 1-2 segundos
│     ├─ Guardado: 0.1 segundos
│     └─ Delay: 1 segundo (configurable)
│     SUBTOTAL: ~4-5 segundos/producto
└─ TOTAL: ~7-8 minutos por categoría

5 categorías x 100 productos = 35-40 minutos (60 prod/min)
```

### Optimizaciones Posibles

1. **Paralelización**: Scrapear múltiples categorías en paralelo (requiere múltiples navegadores)
2. **Cache de sesión**: Reutilizar la misma sesión autenticada
3. **Batch inserts**: Insertar productos en lotes en lugar de uno por uno
4. **Índices de BD**: Ya implementados para búsquedas rápidas

---

## 🎓 Conclusiones

### ✅ Lo que la app HACE:
1. **Scrapea catálogos completos** de proveedores
2. **Actualiza precios y stock** automáticamente
3. **Evita duplicados** usando (importer_id, sku) como clave única
4. **Respeta límites** configurables por categoría
5. **Controla velocidad** para no saturar servidores
6. **Tracking en tiempo real** del progreso
7. **Maneja errores** y reintentos
8. **Guarda logs detallados** de cada operación

### ❌ Lo que la app NO HACE:
1. **NO elimina productos automáticamente** si el proveedor los descontinúa
2. **NO scrapea en paralelo** (secuencial por diseño)
3. **NO tiene sistema de notificaciones** cuando cambian precios
4. **NO valida calidad de datos** extraídos
5. **NO tiene sistema de rollback** si falla a mitad de importación

### 🔮 Próximas Mejoras Sugeridas:
1. Implementar sistema de detección de productos obsoletos
2. Agregar notificaciones por email/Slack cuando finaliza importación
3. Dashboard de métricas de scraping (tiempo, errores, productos/hora)
4. Sistema de priorización de categorías más vendidas
5. Validación de integridad de datos antes de guardar
6. Backup automático antes de cada importación
7. API webhooks para integración con otros sistemas

---

**Autor**: SYNCAR Development Team
**Fecha**: 30 de Octubre de 2025
**Versión**: 2.0
**Última Actualización**: Este documento
