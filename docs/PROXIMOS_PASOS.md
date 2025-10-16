# 📋 Próximos Pasos - Guía de Implementación

## ✅ Lo que ya está listo

### Backend (Completo al 80%)
- ✅ Estructura de directorios
- ✅ Configuración (config.py, database.py, security.py, logger.py)
- ✅ Modelos de base de datos (User, Importer, Category, Product, ImportJob, etc.)
- ✅ Componentes base de importación (AuthComponent, CategoriesComponent, ProductsComponent, ConfigComponent)
- ✅ Orquestador de importación
- ✅ Celery configurado
- ✅ Tareas de Celery (import_categories_task, import_products_task)
- ✅ API endpoints base (/importers)
- ✅ Dockerfile multi-stage
- ✅ requirements.txt

### DevOps (Completo al 100%)
- ✅ Docker Compose para desarrollo (solo infra)
- ✅ Docker Compose para producción (completo)
- ✅ Makefile con comandos útiles
- ✅ GitHub Actions CI/CD
- ✅ Nginx configurado
- ✅ .env.example
- ✅ .gitignore

### Frontend (Completo al 30%)
- ✅ Next.js 14 configurado
- ✅ Tailwind CSS configurado
- ✅ package.json con dependencias
- ✅ Dockerfile
- ✅ Página de inicio placeholder

### Documentación (Completo al 100%)
- ✅ README.md comprehensivo
- ✅ Este archivo de próximos pasos

---

## 🚀 Pasos para Comenzar a Trabajar

### 1. **Setup Inicial** (5 minutos)

```bash
# En la raíz del proyecto
cd /Users/maxberrios/Desktop/REPUESTOS/SYNCAR2.0

# Copiar .env
cp .env.example .env
# Editar .env con tus credenciales reales de los proveedores

# Instalar dependencias
make install

# Levantar servicios de desarrollo
make dev-up
```

### 2. **Verificar que todo funciona** (5 minutos)

```bash
# Terminal 1: Backend
make dev-backend
# Ir a: http://localhost:8000/docs

# Terminal 2: Celery
make dev-celery

# Terminal 3: Frontend
cd frontend
npm install  # Si no lo hiciste con make install
npm run dev
# Ir a: http://localhost:3000
```

### 3. **Crear datos iniciales en la base de datos** (10 minutos)

Necesitas crear los registros de importadores en la DB. Puedes hacerlo de 2 formas:

**Opción A: Script Python**

```python
# backend/app/scripts/seed_importers.py (crear este archivo)

import asyncio
from app.core.database import AsyncSessionLocal
from app.models import Importer, ImporterType

async def seed_importers():
    async with AsyncSessionLocal() as db:
        importers = [
            Importer(
                name=ImporterType.ALSACIA,
                display_name="Alsacia",
                base_url="https://alsacia.example.com",
                is_active=True
            ),
            Importer(
                name=ImporterType.REFAX,
                display_name="Refax",
                base_url="https://refax.example.com",
                is_active=True
            ),
            Importer(
                name=ImporterType.NORIEGA,
                display_name="Noriega",
                base_url="https://noriega.example.com",
                is_active=True
            ),
            Importer(
                name=ImporterType.EMASA,
                display_name="Emasa",
                base_url="https://emasa.example.com",
                is_active=True
            ),
        ]
        
        for importer in importers:
            db.add(importer)
        
        await db.commit()
        print("✅ Importadores creados")

if __name__ == "__main__":
    asyncio.run(seed_importers())
```

```bash
# Ejecutar
cd backend
source venv/bin/activate
python -m app.scripts.seed_importers
```

**Opción B: SQL directo**

```bash
make shell-db

# En el shell de PostgreSQL:
INSERT INTO importers (name, display_name, base_url, is_active, created_at) VALUES
('alsacia', 'Alsacia', 'https://alsacia.example.com', true, NOW()),
('refax', 'Refax', 'https://refax.example.com', true, NOW()),
('noriega', 'Noriega', 'https://noriega.example.com', true, NOW()),
('emasa', 'Emasa', 'https://emasa.example.com', true, NOW());

\q
```

---

## 🎯 Fase 1: Implementar Alsacia (El Importador Piloto)

### **Paso 1.1: Auth Component** (30-60 min)

Edita: `backend/app/importers/alsacia/auth.py`

```python
from playwright.async_api import Page
from app.importers.base import AuthComponent
from app.core.config import settings

class AlsaciaAuthComponent(AuthComponent):
    async def execute(self):
        await self.update_progress("🔐 Conectando a Alsacia...", 5)
        
        # 1. Crear página
        if not self.browser:
            raise Exception("Browser not initialized")
        
        context = await self.browser.new_context()
        page = await context.new_page()
        
        # 2. Navegar a login
        await page.goto(settings.ALSACIA_URL + "/login")
        
        # 3. AQUÍ: Inspecciona el HTML y rellena los selectores correctos
        await page.fill('input[name="username"]', settings.ALSACIA_USERNAME)
        await page.fill('input[name="password"]', settings.ALSACIA_PASSWORD)
        
        # 4. Click en login
        await page.click('button[type="submit"]')
        
        # 5. Esperar a que navegue (ajustar según el sitio)
        await page.wait_for_url('**/dashboard', timeout=10000)
        
        await self.update_progress("✅ Autenticación exitosa", 15)
        
        # 6. Guardar session
        session_data = {
            'cookies': await context.cookies(),
            'localStorage': await page.evaluate('() => Object.assign({}, localStorage)')
        }
        
        return {
            'success': True,
            'session_data': session_data,
            'page': page,
            'context': context
        }
```

**🔍 Cómo investigar el sitio:**

```bash
# Ejecuta Playwright en modo visible (headless=False)
# Edita temporalmente backend/app/core/config.py:
# HEADLESS = False

# Luego abre Python interactivo:
cd backend
source venv/bin/activate
python

>>> from playwright.sync_api import sync_playwright
>>> with sync_playwright() as p:
...     browser = p.chromium.launch(headless=False)
...     page = browser.new_page()
...     page.goto('https://alsacia.example.com/login')
...     # Interactúa manualmente
...     input("Presiona Enter cuando termines...")
...     browser.close()
```

### **Paso 1.2: Categories Component** (1-2 horas)

Edita: `backend/app/importers/alsacia/categories.py`

```python
from app.importers.base import CategoriesComponent
from app.models import Category
from slugify import slugify

class AlsaciaCategoriesComponent(CategoriesComponent):
    async def execute(self):
        await self.update_progress("📂 Navegando a categorías...", 20)
        
        # 1. Restaurar session del AuthComponent
        page = self.session_data.get('page')
        if not page:
            return {'success': False, 'error': 'No page in session'}
        
        # 2. Navegar a página de categorías
        await page.goto('https://alsacia.example.com/categorias')
        
        # 3. AQUÍ: Extraer categorías (ajusta los selectores)
        categories_raw = await page.locator('.category-item').all()
        
        categories = []
        for cat_element in categories_raw:
            name = await cat_element.locator('.category-name').text_content()
            url = await cat_element.locator('a').get_attribute('href')
            
            categories.append({
                'name': name,
                'slug': slugify(name),
                'url': url
            })
        
        await self.update_progress(f"💾 Guardando {len(categories)} categorías...", 70)
        
        # 4. Guardar en DB
        from sqlalchemy import select
        result = await self.db.execute(
            select(Importer).where(Importer.name == self.importer_name)
        )
        importer = result.scalar_one()
        
        for cat_data in categories:
            category = Category(
                importer_id=importer.id,
                name=cat_data['name'],
                slug=cat_data['slug'],
                url=cat_data['url']
            )
            self.db.add(category)
        
        await self.db.commit()
        
        await self.update_progress(f"✅ {len(categories)} categorías importadas", 100)
        
        return {
            'success': True,
            'categories': categories,
            'count': len(categories)
        }
```

### **Paso 1.3: Products Component** (2-4 horas)

Edita: `backend/app/importers/alsacia/products.py`

Este es el más complejo. Aquí un esqueleto:

```python
import asyncio
from app.importers.base import ProductsComponent
from app.models import Product, Category
from sqlalchemy import select

class AlsaciaProductsComponent(ProductsComponent):
    async def execute(self):
        await self.update_progress("🛍️ Iniciando extracción de productos...", 20)
        
        page = self.session_data.get('page')
        total_products = 0
        
        # Configuración
        limit_per_category = self.config.get('products_per_category', 100)
        delay_ms = self.config.get('scraping_speed_ms', 1000) / 1000
        
        for i, category_name in enumerate(self.selected_categories):
            # Buscar categoría en DB
            result = await self.db.execute(
                select(Category).where(Category.name == category_name)
            )
            category = result.scalar_one_or_none()
            
            if not category:
                continue
            
            progress = 20 + int((i / len(self.selected_categories)) * 70)
            await self.update_progress(f"📦 Procesando: {category_name}", progress)
            
            # Navegar a la categoría
            await page.goto(category.url)
            
            # Extraer URLs de productos
            product_links = await page.locator('.product-link').all()
            product_urls = []
            for link in product_links[:limit_per_category]:
                url = await link.get_attribute('href')
                product_urls.append(url)
            
            # Extraer cada producto
            for j, product_url in enumerate(product_urls):
                await page.goto(product_url)
                
                # AQUÍ: Extraer datos del producto
                name = await page.locator('.product-name').text_content()
                price_text = await page.locator('.product-price').text_content()
                price = float(price_text.replace('$', '').replace('.', '').replace(',', '.'))
                sku = await page.locator('.product-sku').text_content()
                
                # Guardar en DB
                product = Product(
                    importer_id=category.importer_id,
                    category_id=category.id,
                    sku=sku,
                    name=name,
                    price=price,
                    currency='CLP'
                )
                self.db.add(product)
                total_products += 1
                
                # Commit cada 50 productos
                if total_products % 50 == 0:
                    await self.db.commit()
                    await self.update_progress(
                        f"💾 {total_products} productos guardados...",
                        progress + 5
                    )
                
                # Delay para no saturar
                await asyncio.sleep(delay_ms)
        
        await self.db.commit()
        await self.update_progress(f"✅ {total_products} productos importados", 100)
        
        return {
            'success': True,
            'products_count': total_products,
            'categories_processed': len(self.selected_categories)
        }
```

### **Paso 1.4: Actualizar Orquestador** (10 min)

Edita: `backend/app/importers/alsacia/__init__.py`

```python
from .auth import AlsaciaAuthComponent
from .categories import AlsaciaCategoriesComponent
from .products import AlsaciaProductsComponent

__all__ = ['AlsaciaAuthComponent', 'AlsaciaCategoriesComponent', 'AlsaciaProductsComponent']
```

Luego actualiza `backend/app/importers/orchestrator.py` para usar las clases específicas de Alsacia cuando `importer_name == 'alsacia'`.

---

## 🎨 Fase 2: Frontend Básico (Después de Alsacia)

### **Paso 2.1: Página de Importadores** (2-3 horas)

```bash
frontend/app/importadores/page.tsx
```

Con tabs y botones "Importar Categorías" / "Importar Productos".

### **Paso 2.2: Modal de Progreso** (1-2 horas)

```bash
frontend/components/import-progress-modal.tsx
```

Con SSE conectado a `/api/v1/jobs/{job_id}/stream`.

### **Paso 2.3: Página de Catálogo** (2-3 horas)

Tabla con productos importados.

---

## 📞 ¿Dónde estás ahora?

**YA COMPLETADO:**
- ✅ Toda la infraestructura
- ✅ Backend base al 80%
- ✅ Frontend base al 30%
- ✅ Docker y CI/CD al 100%

**LO QUE TE FALTA (en orden):**
1. ⏳ **Implementar los componentes de scraping de Alsacia** (Auth, Categories, Products)
   - **Esto es lo que deberías hacer AHORA**
   - Usa Playwright en modo visible para inspeccionar el sitio
   - Ve paso por paso, empezando por Auth
2. ⏳ Crear endpoints API adicionales (jobs status, categories list, products list)
3. ⏳ Crear UI del frontend (páginas e Importadores, Catálogo)
4. ⏳ Replicar el patrón de Alsacia para los otros proveedores

---

## 💡 Consejos

1. **No intentes hacer todo de una vez**: Empieza por Auth de Alsacia y pruébalo.
2. **Usa Playwright en modo visible** (`headless=False`) mientras desarrollas.
3. **Prueba cada componente aisladamente** antes de integrar.
4. **Usa `make dev-backend`, `make dev-celery`** en terminales separadas.
5. **Revisa los logs** constantemente: son muy descriptivos.

---

## 🆘 Si necesitas ayuda

Dime en qué paso específico estás y te guiaré. Ejemplo:
- "Estoy en Paso 1.1, no sé cómo encontrar los selectores del formulario de login"
- "Ya tengo Auth funcionando, paso a Categories pero no sé cómo extraer la lista"

**¡Estás listo para comenzar! 🚀**
