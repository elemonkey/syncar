"""
Importador Noriega
Scraper para https://noriegaysalazar.cl
"""

from typing import Any, Dict, List, Optional

from app.core.logger import logger
from app.importers.base import AuthComponent, CategoriesComponent, ProductsComponent
from playwright.async_api import Browser, Page
from sqlalchemy.ext.asyncio import AsyncSession


class NoriegaAuthComponent(AuthComponent):
    """
    Componente de autenticación para Noriega

    Realiza el login en la plataforma de Noriega
    """

    def __init__(
        self,
        importer_name: str,
        job_id: str,
        db: AsyncSession,
        browser: Browser,
        credentials: Dict[str, str],
        headless: bool = False,
    ):
        super().__init__(importer_name, job_id, db, browser)
        self.credentials = credentials
        self.headless = headless
        self.base_url = "https://ecommerce.noriegavanzulli.cl/b2b/loginvip.jsp"

    async def execute(self) -> Dict[str, Any]:
        """
        Autentica en Noriega y devuelve el contexto y página autenticados.
        Usa self.browser y self.db que fueron pasados en __init__
        """
        try:
            logger.info("🔐 Iniciando autenticación en Noriega...")

            # Crear nuevo contexto del navegador
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            )

            # Crear nueva página
            page = await context.new_page()
            logger.info("📄 Nueva página creada")

            # Navegar a la página de login
            await page.goto(self.base_url, wait_until="networkidle", timeout=60000)
            logger.info(f"✅ Página cargada: {self.base_url}")

            # 📸 Screenshot ANTES de completar formulario
            screenshot_antes = "/tmp/noriega_antes_login.png"
            await page.screenshot(path=screenshot_antes)
            logger.info(f"📸 Screenshot guardado: {screenshot_antes}")

            # 🔑 Completar formulario de login con credenciales de la BD
            logger.info("📝 Completando formulario de login...")

            # Campo RUT
            await page.fill('input[name="trut"]', str(self.credentials.get("rut", "")))
            logger.info(f"✅ RUT completado: {self.credentials.get('rut', '')}")

            # Campo Usuario
            await page.fill('input[name="tuser"]', self.credentials.get("username", ""))
            logger.info(
                f"✅ Usuario completado: {self.credentials.get('username', '')}"
            )

            # Campo Contraseña
            await page.fill('input[name="tpass"]', self.credentials.get("password", ""))
            logger.info("✅ Contraseña completada: ****")

            # 📸 Screenshot DESPUÉS de completar formulario
            screenshot_despues = "/tmp/noriega_despues_completar.png"
            await page.screenshot(path=screenshot_despues)
            logger.info(f"📸 Screenshot guardado: {screenshot_despues}")

            # 🚀 Hacer clic en el botón de login
            logger.info("🚀 Haciendo clic en botón Ingresar...")

            # Hacer clic y esperar navegación simultáneamente
            try:
                async with page.expect_navigation(timeout=30000):
                    await page.click('input[name="Ingresar"]')
                logger.info("✅ Navegación completada después del clic")
            except Exception as e:
                logger.warning(f"⚠️ Error en navegación: {e}")
                # Intentar esperar un poco más
                import asyncio

                await asyncio.sleep(3)

            # Verificar URL actual para confirmar login exitoso
            current_url = page.url
            logger.info(f"📍 URL actual después del login: {current_url}")

            # � Detectar y cerrar modal/popup si existe
            logger.info("🔍 Buscando modal o popup...")
            import asyncio
            await asyncio.sleep(2)  # Esperar a que aparezca el modal

            try:
                # Buscar si hay un modal visible (pueden tener diferentes clases/ids)
                # Intentar detectar elementos comunes de modals
                modal_selectors = [
                    'div[role="dialog"]',
                    '.modal',
                    '#modal',
                    '.popup',
                    '.alert',
                    'div.swal2-container',  # SweetAlert
                ]

                modal_found = False
                for selector in modal_selectors:
                    try:
                        modal = await page.query_selector(selector)
                        if modal and await modal.is_visible():
                            logger.info(f"✅ Modal detectado con selector: {selector}")
                            modal_found = True
                            break
                    except:
                        continue

                if modal_found:
                    # Hacer clic en la esquina superior derecha del navegador
                    # Obtener dimensiones del viewport
                    viewport = page.viewport_size
                    logger.info(f"📐 Viewport: {viewport}")

                    # Hacer clic en el último pixel superior derecho (con margen de seguridad)
                    x = viewport['width'] - 10  # 10px desde el borde derecho
                    y = 10  # 10px desde el borde superior

                    logger.info(f"🖱️  Haciendo clic en esquina superior derecha: ({x}, {y})")
                    await page.mouse.click(x, y)
                    await asyncio.sleep(1)
                    logger.info("✅ Modal cerrado")
                else:
                    logger.info("ℹ️  No se detectó modal - continuando")

            except Exception as e:
                logger.warning(f"⚠️ Error buscando/cerrando modal: {e}")

            # �📸 Screenshot DESPUÉS del login (con manejo de errores)
            try:
                screenshot_final = "/tmp/noriega_despues_login.png"
                await page.screenshot(path=screenshot_final)
                logger.info(f"📸 Screenshot guardado: {screenshot_final}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo tomar screenshot final: {e}")

            logger.info("✅ Autenticación completada - listo para extraer categorías")

            return {
                "success": True,
                "context": context,
                "page": page,
                "url": current_url,
                "message": "Login completado. Revisa el navegador y los screenshots en /tmp/",
            }

        except Exception as e:
            logger.error(f"❌ Error en autenticación Noriega: {str(e)}")
            raise


class NoriegaCategoriesComponent(CategoriesComponent):
    """
    Componente para extraer categorías de Noriega
    """

    def __init__(
        self,
        importer_name: str,
        job_id: str,
        db: AsyncSession,
        browser: Browser,
        page: Page,
        context: Any,
    ):
        super().__init__(importer_name, job_id, db, browser)
        self.page = page
        self.context = context

    async def execute(self) -> Dict[str, Any]:
        """
        Extrae las categorías de Noriega desde la página de selección por medida

        Returns:
            Dict con las categorías encontradas
        """
        try:
            await self.update_progress("Iniciando extracción de categorías...", 30)

            # URL de la página de categorías (Lista por Medida)
            categories_url = "https://ecommerce.noriegavanzulli.cl/b2b/seleccion_medida.jsp"

            self.logger.info(f"🔗 Navegando a página de categorías: {categories_url}")
            await self.page.goto(categories_url, wait_until="networkidle", timeout=60000)
            self.logger.info("✅ Página de categorías cargada")

            # 📸 Screenshot de la página de categorías
            try:
                screenshot_path = "/tmp/noriega_categorias.png"
                await self.page.screenshot(path=screenshot_path)
                self.logger.info(f"� Screenshot guardado: {screenshot_path}")
            except Exception as e:
                self.logger.warning(f"⚠️ No se pudo tomar screenshot: {e}")

            await self.update_progress("Extrayendo categorías...", 50)

            # Extraer categorías de la primera tabla (X MEDIDA)
            self.logger.info("📋 Extrayendo categorías de 'X MEDIDA'...")

            # Selector: tabla dentro de #listado2 > #tabla_lista
            categories_selector = '#listado2 #tabla_lista table tbody tr td a'
            category_elements = await self.page.query_selector_all(categories_selector)

            categories = []
            for element in category_elements:
                try:
                    # Extraer texto (nombre de categoría)
                    category_name = await element.text_content()
                    category_name = category_name.strip() if category_name else ""

                    # Extraer href (URL de la categoría)
                    href = await element.get_attribute('href')

                    if category_name and href:
                        # Construir URL completa
                        if not href.startswith('http'):
                            base_url = "https://ecommerce.noriegavanzulli.cl/b2b/"
                            category_url = base_url + href
                        else:
                            category_url = href

                        categories.append({
                            "name": category_name,
                            "external_id": category_name,  # Usar el nombre como ID
                            "url": category_url,
                            "type": "medida"  # Tipo de categoría
                        })

                        self.logger.info(f"  ✓ {category_name}")

                except Exception as e:
                    self.logger.warning(f"⚠️ Error extrayendo categoría: {e}")
                    continue

            # También extraer categorías de la segunda tabla (X Nº DE FABRICANTE)
            self.logger.info("📋 Extrayendo categorías de 'X Nº DE FABRICANTE'...")

            fabricante_selector = '#listado3 #tabla_lista table tbody tr td a'
            fabricante_elements = await self.page.query_selector_all(fabricante_selector)

            for element in fabricante_elements:
                try:
                    category_name = await element.text_content()
                    category_name = category_name.strip() if category_name else ""

                    href = await element.get_attribute('href')

                    if category_name and href:
                        if not href.startswith('http'):
                            base_url = "https://ecommerce.noriegavanzulli.cl/b2b/"
                            category_url = base_url + href
                        else:
                            category_url = href

                        categories.append({
                            "name": category_name,
                            "external_id": category_name,
                            "url": category_url,
                            "type": "fabricante"  # Tipo de categoría
                        })

                        self.logger.info(f"  ✓ {category_name} (fabricante)")

                except Exception as e:
                    self.logger.warning(f"⚠️ Error extrayendo categoría fabricante: {e}")
                    continue

            await self.update_progress(f"Categorías extraídas: {len(categories)}", 70)

            self.logger.info(f"✅ Total de categorías extraídas: {len(categories)}")
            self.logger.info(f"   - Por medida: {sum(1 for c in categories if c.get('type') == 'medida')}")
            self.logger.info(f"   - Por fabricante: {sum(1 for c in categories if c.get('type') == 'fabricante')}")

            # 💾 Guardar categorías en la base de datos
            await self.update_progress("Guardando categorías en la base de datos...", 80)
            self.logger.info("💾 Guardando categorías en la base de datos...")

            from app.models import Category, Importer
            from sqlalchemy import select

            # Obtener el importer
            result = await self.db.execute(
                select(Importer).where(Importer.name == self.importer_name.upper())
            )
            importer = result.scalar_one_or_none()

            if not importer:
                raise Exception(f"Importador {self.importer_name} no encontrado")

            # Limpiar categorías existentes del importador
            await self.db.execute(
                select(Category).where(Category.importer_id == importer.id)
            )
            existing_categories = (await self.db.execute(
                select(Category).where(Category.importer_id == importer.id)
            )).scalars().all()

            for cat in existing_categories:
                await self.db.delete(cat)

            self.logger.info(f"🗑️  Eliminadas {len(existing_categories)} categorías antiguas")

            # Crear nuevas categorías
            saved_count = 0
            for cat_data in categories:
                try:
                    # Crear slug del nombre
                    import re
                    slug = re.sub(r'[^a-z0-9]+', '-', cat_data['name'].lower()).strip('-')

                    category = Category(
                        importer_id=importer.id,
                        name=cat_data['name'],
                        slug=slug,
                        url=cat_data['url'],
                        external_id=cat_data['external_id'],
                        product_count=0  # Se actualizará al importar productos
                    )

                    self.db.add(category)
                    saved_count += 1

                except Exception as e:
                    self.logger.warning(f"⚠️ Error guardando categoría {cat_data['name']}: {e}")
                    continue

            # Commit de todas las categorías
            await self.db.commit()
            self.logger.info(f"✅ {saved_count} categorías guardadas en la base de datos")

            # Actualizar last_sync_at del importador
            from datetime import datetime
            importer.last_sync_at = datetime.now()
            await self.db.commit()

            await self.update_progress(f"Categorías guardadas: {saved_count}", 100)

            return {
                "success": True,
                "categories": categories,
                "total": len(categories),
                "saved": saved_count,
                "message": f"Se extrajeron y guardaron {saved_count} categorías exitosamente",
            }

        except Exception as e:
            self.logger.error(f"❌ Error extrayendo categorías: {e}")
            await self.update_progress(f"Error: {str(e)}", 0, "ERROR")
            return {"success": False, "error": str(e), "categories": []}


class NoriegaProductsComponent(ProductsComponent):
    """
    Componente para extraer productos de Noriega
    """

    def __init__(
        self,
        importer_name: str,
        job_id: str,
        db: AsyncSession,
        browser: Browser,
        page: Page,
        context: Any,
        categories: List[str],
    ):
        super().__init__(importer_name, job_id, db, browser)
        self.page = page
        self.context = context
        self.categories = categories

    async def execute(self) -> Dict[str, Any]:
        """
        Extrae productos de las categorías seleccionadas

        Returns:
            Dict con los productos encontrados
        """
        try:
            await self.update_progress("Iniciando extracción de productos...", 50)

            self.logger.info(f"⏸️  ESPERANDO DIRECTRICES para extraer productos")
            self.logger.info(f"📋 Categorías a procesar: {self.categories}")

            await self.update_progress(
                "Esperando directrices para extraer productos", 55
            )

            return {
                "success": True,
                "products": [],
                "message": "Esperando directrices para extraer productos",
            }

        except Exception as e:
            self.logger.error(f"Error extrayendo productos: {e}")
            await self.update_progress(f"Error: {str(e)}", 0, "ERROR")
            return {"success": False, "error": str(e), "products": []}
