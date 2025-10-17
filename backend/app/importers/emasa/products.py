"""
Componente de extracción de productos para EMASA
"""

from typing import Any, Dict, List, Optional

from app.importers.base import ProductsComponent
from playwright.async_api import Browser, Page
from sqlalchemy.ext.asyncio import AsyncSession


class EmasaProductsComponent(ProductsComponent):
    """
    Componente para extraer productos de EMASA

    Respeta la configuración del importador:
    - products_per_category: Límite máximo de productos por categoría
    - scraping_speed_ms: Delay entre cada producto (en milisegundos)
    """

    def __init__(
        self,
        importer_name: str,
        job_id: str,
        db: AsyncSession,
        browser: Browser,
        page: Page,
        context: Any,
        selected_categories: List[str],
        config: Optional[Dict[str, Any]] = None,
    ):
        # Llamar al constructor de la clase base
        session_data = {
            "page": page,
            "context": context,
        }
        super().__init__(
            importer_name=importer_name,
            job_id=job_id,
            db=db,
            session_data=session_data,
            selected_categories=selected_categories,
            config=config or {},
            browser=browser,
        )
        self.page = page
        self.context = context

        # Configuración con valores por defecto
        self.products_per_category = self.config.get("products_per_category", None)
        self.scraping_speed_ms = self.config.get("scraping_speed_ms", 1000)

        self.logger.info("⚙️ Configuración cargada:")
        if self.products_per_category:
            self.logger.info(f"   - Límite por categoría: {self.products_per_category}")
        else:
            self.logger.info("   - Límite por categoría: SIN LÍMITE (scrapeará todos)")
        self.logger.info(f"   - Velocidad: {self.scraping_speed_ms}ms entre productos")

    async def execute(self) -> Dict[str, Any]:
        """
        Extrae productos de las categorías seleccionadas

        Returns:
            Dict con los productos encontrados
        """
        try:
            await self.update_progress("Iniciando extracción de productos...", 10)

            self.logger.info("=" * 80)
            self.logger.info("📦 INICIANDO SCRAPING DE PRODUCTOS - EMASA")
            self.logger.info("=" * 80)
            self.logger.info(
                f"📋 Categorías seleccionadas: {len(self.selected_categories)}"
            )

            if self.products_per_category:
                self.logger.info(
                    f"⚙️  Límite por categoría: {self.products_per_category}"
                )
            else:
                self.logger.info("⚙️  Límite por categoría: SIN LÍMITE")

            self.logger.info(
                f"⏱️  Velocidad: {self.scraping_speed_ms}ms entre productos"
            )
            self.logger.info("")

            # Obtener las categorías desde la base de datos
            from app.models import Category, Importer
            from sqlalchemy import select

            result = await self.db.execute(
                select(Importer).where(Importer.name == self.importer_name.upper())
            )
            importer = result.scalar_one_or_none()

            if not importer:
                raise Exception(f"Importador {self.importer_name} no encontrado")

            # Obtener todas las categorías del importador
            categories_result = await self.db.execute(
                select(Category).where(Category.importer_id == importer.id)
            )
            all_categories = {cat.id: cat for cat in categories_result.scalars().all()}

            self.logger.info(f"✅ Categorías en BD: {len(all_categories)}")
            self.logger.info("")

            all_products = []
            categories_processed = 0

            # Iterar por cada categoría seleccionada
            for idx, cat_id_str in enumerate(self.selected_categories, 1):
                try:
                    cat_id = int(cat_id_str)
                    category = all_categories.get(cat_id)

                    if not category:
                        self.logger.warning(
                            f"⚠️ Categoría ID {cat_id} no encontrada en BD"
                        )
                        continue

                    self.logger.info("=" * 80)
                    self.logger.info(
                        f"📂 CATEGORÍA {idx}/{len(self.selected_categories)}: {category.name}"
                    )
                    self.logger.info(f"   ID: {category.id}")
                    self.logger.info("=" * 80)

                    # Navegar a la categoría
                    self.logger.info(f"🔗 URL: {category.url}")
                    self.logger.info("📍 Navegando a la lista de productos...")

                    await self.page.goto(
                        category.url, wait_until="networkidle", timeout=60000
                    )

                    # Screenshot de la categoría
                    try:
                        screenshot_path = f"/tmp/emasa_category_{cat_id}.png"
                        await self.page.screenshot(path=screenshot_path)
                        self.logger.info(f"📸 Screenshot: {screenshot_path}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error en screenshot: {e}")

                    # Extraer productos de esta categoría
                    products = await self._extract_products_from_category(
                        category=category, limit=self.products_per_category
                    )

                    all_products.extend(products)
                    categories_processed += 1

                    self.logger.info(
                        f"✅ Productos extraídos de {category.name}: {len(products)}"
                    )
                    self.logger.info("")

                except Exception as e:
                    self.logger.error(
                        f"❌ Error procesando categoría {cat_id_str}: {e}"
                    )
                    import traceback

                    self.logger.error(traceback.format_exc())
                    continue

            # Guardar productos en la base de datos
            if all_products:
                await self.update_progress(
                    f"Guardando {len(all_products)} productos...", 90
                )
                saved_count = await self._save_products(all_products)
                self.logger.info(f"✅ {saved_count} productos guardados exitosamente")

            await self.update_progress("✅ Importación completada", 100)

            self.logger.info("=" * 80)
            self.logger.info("✅ SCRAPING COMPLETADO")
            self.logger.info(f"   Total de productos extraídos: {len(all_products)}")
            self.logger.info(f"   Categorías procesadas: {categories_processed}")
            self.logger.info("=" * 80)

            return {
                "success": True,
                "products": [],  # No devolver productos completos (muy pesado)
                "total": len(all_products),
                "categories_processed": categories_processed,
                "message": f"Se procesaron {categories_processed} categorías. Navegador listo para inspección.",
            }

        except Exception as e:
            self.logger.error(f"❌ Error en extracción de productos: {e}")
            import traceback

            self.logger.error(traceback.format_exc())

            await self.update_progress(f"❌ Error: {str(e)}", 100)

            return {
                "success": False,
                "error": str(e),
                "message": f"Error extrayendo productos: {str(e)}",
            }

    async def _extract_products_from_category(
        self, category: Any, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Extrae productos de una categoría

        Args:
            category: Objeto Category de SQLAlchemy
            limit: Límite máximo de productos a extraer (None = todos)

        Returns:
            Lista de productos extraídos
        """
        products = []

        try:
            # NOTA: Ajustar selectores según la estructura HTML de EMASA

            # Esperar a que carguen los productos
            import asyncio

            await asyncio.sleep(2)

            # Selector genérico de productos (ajustar según EMASA)
            product_selector = ".product-item, .product-card, .product"
            product_elements = await self.page.query_selector_all(product_selector)

            self.logger.info(
                f"📦 Productos encontrados en página: {len(product_elements)}"
            )

            # Aplicar límite si existe
            products_to_process = (
                product_elements[:limit] if limit else product_elements
            )

            for idx, element in enumerate(products_to_process, 1):
                try:
                    # Actualizar progreso
                    progress = 20 + (idx / len(products_to_process)) * 60
                    await self.update_progress(
                        f"Extrayendo producto {idx}/{len(products_to_process)}...",
                        int(progress),
                    )

                    # Extraer datos del producto (ajustar selectores según EMASA)
                    product_data = await self._extract_product_data(element, category)

                    if product_data:
                        products.append(product_data)
                        self.logger.info(
                            f"  ✓ [{idx}/{len(products_to_process)}] {product_data.get('name', 'Sin nombre')[:50]}"
                        )

                    # Delay entre productos
                    await asyncio.sleep(self.scraping_speed_ms / 1000.0)

                except Exception as e:
                    self.logger.warning(f"⚠️ Error extrayendo producto {idx}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"❌ Error en _extract_products_from_category: {e}")
            import traceback

            self.logger.error(traceback.format_exc())

        return products

    async def _extract_product_data(
        self, element: Any, category: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Extrae datos de un elemento de producto

        NOTA: Los selectores son genéricos y deben ajustarse según la estructura HTML de EMASA

        Args:
            element: Elemento de producto de Playwright
            category: Categoría del producto

        Returns:
            Dict con datos del producto o None si falla
        """
        try:
            # Extraer nombre (ajustar selector)
            name_element = await element.query_selector(
                ".product-name, .product-title, h3, h4"
            )
            name = await name_element.text_content() if name_element else "Sin nombre"
            name = name.strip()

            # Extraer SKU/Código (ajustar selector)
            sku_element = await element.query_selector(
                ".product-sku, .product-code, .sku"
            )
            sku = await sku_element.text_content() if sku_element else ""
            sku = sku.strip()

            # Extraer precio (ajustar selector)
            price_element = await element.query_selector(
                ".product-price, .price, .product-cost"
            )
            price_text = await price_element.text_content() if price_element else "0"
            # Limpiar precio: eliminar símbolos y convertir a float
            import re

            price_clean = re.sub(
                r"[^\d.,]", "", price_text.replace(".", "").replace(",", ".")
            )
            try:
                price = float(price_clean) if price_clean else 0.0
            except:
                price = 0.0

            # Extraer URL del producto (ajustar selector)
            link_element = await element.query_selector("a")
            product_url = (
                await link_element.get_attribute("href") if link_element else ""
            )
            if product_url and not product_url.startswith("http"):
                product_url = f"https://ecommerce.emasa.cl/b2b/{product_url}"

            # Extraer imagen (ajustar selector)
            img_element = await element.query_selector("img")
            image_url = await img_element.get_attribute("src") if img_element else ""
            if image_url and not image_url.startswith("http"):
                image_url = f"https://ecommerce.emasa.cl/b2b/{image_url}"

            return {
                "name": name,
                "sku": sku
                or f"EMASA-{category.id}-{hash(name)}",  # SKU generado si no existe
                "price": price,
                "url": product_url,
                "image_url": image_url,
                "category_id": category.id,
                "category_name": category.name,
                "stock": 1,  # Stock por defecto (ajustar si EMASA muestra stock)
                "description": "",  # Extraer si está disponible
            }

        except Exception as e:
            self.logger.warning(f"⚠️ Error extrayendo datos de producto: {e}")
            return None

    async def _save_products(self, products: List[Dict[str, Any]]) -> int:
        """
        Guarda productos en la base de datos

        Args:
            products: Lista de productos a guardar

        Returns:
            Número de productos guardados
        """
        from app.models import Importer, Product
        from sqlalchemy import select

        try:
            # Obtener el importador
            result = await self.db.execute(
                select(Importer).where(Importer.name == self.importer_name.upper())
            )
            importer = result.scalar_one_or_none()

            if not importer:
                raise Exception(f"Importador {self.importer_name} no encontrado")

            saved_count = 0
            for product_data in products:
                try:
                    # Verificar si el producto ya existe
                    result = await self.db.execute(
                        select(Product).where(
                            Product.sku == product_data["sku"],
                            Product.importer_id == importer.id,
                        )
                    )
                    existing_product = result.scalar_one_or_none()

                    if existing_product:
                        # Actualizar producto existente
                        existing_product.name = product_data["name"]
                        existing_product.price = product_data["price"]
                        existing_product.stock = product_data["stock"]
                        existing_product.url = product_data.get("url", "")
                        existing_product.image_url = product_data.get("image_url", "")
                        existing_product.description = product_data.get(
                            "description", ""
                        )
                    else:
                        # Crear nuevo producto
                        product = Product(
                            name=product_data["name"],
                            sku=product_data["sku"],
                            price=product_data["price"],
                            stock=product_data["stock"],
                            category_id=product_data["category_id"],
                            importer_id=importer.id,
                            url=product_data.get("url", ""),
                            image_url=product_data.get("image_url", ""),
                            description=product_data.get("description", ""),
                        )
                        self.db.add(product)

                    saved_count += 1

                except Exception as e:
                    self.logger.error(
                        f"❌ Error guardando producto {product_data.get('sku')}: {e}"
                    )
                    continue

            await self.db.commit()
            return saved_count

        except Exception as e:
            self.logger.error(f"❌ Error en _save_products: {e}")
            import traceback

            self.logger.error(traceback.format_exc())
            return 0
