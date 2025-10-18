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

    async def _update_job_result(self, result_data: Dict[str, Any]):
        """
        Actualiza el campo result del job con información detallada

        Args:
            result_data: Diccionario con datos actualizados
        """
        from app.models import ImportJob
        from sqlalchemy import select, update

        try:
            # Obtener job actual
            stmt = select(ImportJob).where(ImportJob.job_id == self.job_id)
            result = await self.db.execute(stmt)
            job = result.scalar_one_or_none()

            if job:
                # Merge con el result existente
                current_result = job.result or {}
                updated_result = {**current_result, **result_data}

                # Actualizar
                update_stmt = (
                    update(ImportJob)
                    .where(ImportJob.job_id == self.job_id)
                    .values(result=updated_result)
                )
                await self.db.execute(update_stmt)
                await self.db.commit()
        except Exception as e:
            self.logger.error(f"Error actualizando job result: {e}")

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
                    # ✋ Verificar si el job fue cancelado
                    if await self.is_job_cancelled():
                        self.logger.warning("❌ Importación cancelada por el usuario")
                        return {
                            "success": False,
                            "error": "Importación cancelada por el usuario",
                            "products": [],
                            "total": 0,
                            "categories_processed": categories_processed,
                        }

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
        Extrae productos de una categoría navegando por todas las páginas

        Args:
            category: Objeto Category de SQLAlchemy
            limit: Límite máximo de productos a extraer (None = todos)

        Returns:
            Lista de productos extraídos
        """
        products = []

        try:
            import asyncio
            import re

            # Esperar a que cargue la tabla de productos
            await asyncio.sleep(2)

            # 1. EXTRAER TOTAL DE PRODUCTOS
            # Buscar el texto "Mostrando registros del X al Y de un total de Z registros"
            info_selector = "#tblProd_info"
            info_element = await self.page.query_selector(info_selector)

            total_products = 0
            if info_element:
                info_text = await info_element.text_content()
                # Extraer el número total con regex
                match = re.search(r"de un total de (\d+) registros", info_text)
                if match:
                    total_products = int(match.group(1))
                    self.logger.info(
                        f"📦 Total de productos en categoría: {total_products}"
                    )

            if total_products == 0:
                self.logger.warning(f"⚠️ No se encontraron productos en {category.name}")
                return products

            # Aplicar límite si existe
            products_to_extract = (
                min(total_products, limit) if limit else total_products
            )
            self.logger.info(f"🎯 Se extraerán {products_to_extract} productos")

            # 2. NAVEGAR POR TODAS LAS PÁGINAS
            current_page = 1
            products_extracted = 0

            while products_extracted < products_to_extract:
                # ✋ Verificar cancelación antes de cada página
                if await self.is_job_cancelled():
                    self.logger.warning("❌ Importación cancelada por el usuario")
                    return products

                self.logger.info(f"\n📄 Procesando página {current_page}...")

                # 3. EXTRAER PRODUCTOS DE LA PÁGINA ACTUAL
                # Selector de filas de la tabla
                row_selector = "#tblProd tbody tr"
                rows = await self.page.query_selector_all(row_selector)

                self.logger.info(f"   Productos en página: {len(rows)}")

                for idx, row in enumerate(rows, 1):
                    # ✋ Verificar cancelación
                    if await self.is_job_cancelled():
                        self.logger.warning("❌ Importación cancelada")
                        return products

                    # Verificar límite
                    if products_extracted >= products_to_extract:
                        break

                    try:
                        # Actualizar job result
                        await self._update_job_result(
                            {
                                "total_items": products_to_extract,
                                "processed_items": products_extracted,
                                "current_item": products_extracted + 1,
                                "category": category.name,
                                "current_page": current_page,
                            }
                        )

                        # Extraer datos del producto (fila)
                        product_data = await self._extract_product_from_row(
                            row, category
                        )

                        if product_data:
                            products.append(product_data)
                            products_extracted += 1

                            self.logger.info(
                                f"  ✓ [{products_extracted}/{products_to_extract}] "
                                f"{product_data.get('sku', 'N/A')} - {product_data.get('name', 'Sin nombre')[:50]}"
                            )

                        # Delay entre productos
                        await asyncio.sleep(self.scraping_speed_ms / 1000.0)

                    except Exception as e:
                        self.logger.warning(f"⚠️ Error extrayendo producto {idx}: {e}")
                        continue

                # 4. NAVEGAR A LA SIGUIENTE PÁGINA SI HAY MÁS PRODUCTOS
                if products_extracted < products_to_extract:
                    # Buscar botón "Siguiente"
                    next_button = await self.page.query_selector(
                        "#tblProd_next:not(.disabled)"
                    )

                    if next_button:
                        self.logger.info(f"➡️  Navegando a página {current_page + 1}...")
                        await next_button.click()
                        await asyncio.sleep(2)  # Esperar a que cargue la nueva página
                        current_page += 1
                    else:
                        self.logger.info("✅ No hay más páginas disponibles")
                        break
                else:
                    break

            self.logger.info(
                f"\n✅ Extracción completada: {len(products)} productos de {category.name}"
            )

        except Exception as e:
            self.logger.error(f"❌ Error en _extract_products_from_category: {e}")
            import traceback

            self.logger.error(traceback.format_exc())

        return products

    async def _extract_product_from_row(
        self, row: Any, category: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Extrae datos de una fila de la tabla de productos y navega al detalle

        Args:
            row: Elemento <tr> de la tabla de productos
            category: Categoría del producto

        Returns:
            Dict con datos del producto o None si falla
        """
        try:
            import asyncio

            # 1. EXTRAER DATOS BÁSICOS DE LA FILA
            cells = await row.query_selector_all("td")

            if len(cells) < 3:  # Verificar que tenga al menos 3 columnas
                self.logger.warning("⚠️ Fila sin suficientes columnas")
                return None

            # El enlace está en la TERCERA celda (índice 2)
            item_cell = cells[2]

            # Buscar enlace con data-src o href
            item_link = await item_cell.query_selector("[data-src]")
            if not item_link:
                item_link = await item_cell.query_selector("a")

            if not item_link:
                self.logger.warning(
                    "⚠️ No se encontró enlace en la tercera celda (ITEM)"
                )
                return None

            # Extraer SKU del texto del enlace
            sku_text = await item_link.text_content()
            sku = sku_text.strip()

            # Extraer URL del detalle (puede estar en data-src o href)
            detail_url = await item_link.get_attribute("data-src")
            if not detail_url:
                detail_url = await item_link.get_attribute("href")

            if not detail_url:
                self.logger.warning(f"⚠️ No se pudo extraer URL para SKU {sku}")
                return None

            # Construir URL completa si es relativa
            if not detail_url.startswith("http"):
                detail_url = f"https://ecommerce.emasa.cl/b2b/{detail_url.lstrip('/')}"

            self.logger.info(f"   🔗 Navegando a detalle: {detail_url}")

            # 2. NAVEGAR AL DETALLE DEL PRODUCTO EN NUEVA PESTAÑA
            # Guardar la página actual
            current_page = self.page

            # Abrir el detalle en nueva pestaña
            context = current_page.context
            detail_page = await context.new_page()

            try:
                await detail_page.goto(
                    detail_url, wait_until="domcontentloaded", timeout=30000
                )
                await asyncio.sleep(1.5)

                # 3. EXTRAER DATOS DEL DETALLE
                product_data = await self._extract_product_detail(
                    detail_page, sku, category, detail_url
                )

                return product_data

            finally:
                # Cerrar la pestaña del detalle
                await detail_page.close()

        except Exception as e:
            self.logger.warning(f"⚠️ Error extrayendo producto de fila: {e}")
            import traceback

            self.logger.debug(traceback.format_exc())
            return None

    async def _extract_product_detail(
        self, page: Any, sku: str, category: Any, url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extrae todos los datos del detalle del producto desde EMASA

        Args:
            page: Página de Playwright con el detalle del producto
            sku: SKU del producto
            category: Categoría del producto
            url: URL del detalle

        Returns:
            Dict con datos completos del producto o None si falla
        """
        try:
            import re

            # EXTRAER NOMBRE (h3 dentro de box-body)
            name_element = await page.query_selector(".box-body h3")
            name = "Sin nombre"
            if name_element:
                name = await name_element.text_content()
                name = name.strip()

            # EXTRAER MARCA (span después del nombre)
            brand_element = await page.query_selector(".box-body .col-sm-8 span")
            brand = ""
            if brand_element:
                brand = await brand_element.text_content()
                brand = brand.strip()

            # EXTRAER PRECIO CON IVA (tercer h3 en div.pficha)
            price = 0.0
            price_elements = await page.query_selector_all("div.pficha h3")
            if len(price_elements) >= 2:  # El segundo precio es "PRECIO CON IVA"
                price_text = await price_elements[1].text_content()
                # Limpiar precio: $37.604 -> 37604
                price_clean = re.sub(r"[^\d]", "", price_text)
                try:
                    price = float(price_clean) if price_clean else 0.0
                except:
                    price = 0.0

            # EXTRAER DESCRIPCIÓN/CARACTERÍSTICAS (dentro del jumbotron)
            characteristics = []
            char_elements = await page.query_selector_all(".jumbotron ul li")
            for elem in char_elements:
                char_text = await elem.text_content()
                if char_text:
                    characteristics.append(char_text.strip())

            # Mantener descripción como texto para compatibilidad
            description = "\n".join(characteristics) if characteristics else ""

            # EXTRAER TODAS LAS IMÁGENES (del slider)
            images = []
            img_elements = await page.query_selector_all("#slider-thumbs img")
            for img_elem in img_elements:
                img_src = await img_elem.get_attribute(
                    "data-zoom"
                )  # Usar data-zoom para obtener imagen grande
                if not img_src:
                    img_src = await img_elem.get_attribute("src")

                if img_src and "no_image" not in img_src:
                    # Convertir a URL completa
                    if not img_src.startswith("http"):
                        img_src = (
                            f"https://ecommerce.emasa.cl/b2b/{img_src.lstrip('/')}"
                        )
                    images.append(img_src)

            # Primera imagen como principal
            image_url = images[0] if images else ""

            # EXTRAER COMPATIBILIDAD (tabla de aplicaciones)
            compatibility = []
            app_rows = await page.query_selector_all("#tb1 tbody tr")
            for row in app_rows:
                cells = await row.query_selector_all("td")
                if len(cells) >= 3:
                    brand_auto = await cells[0].text_content()
                    model = await cells[1].text_content()
                    years = await cells[2].text_content()

                    # Separar año inicio y término
                    year_match = re.search(r"(\d{4})\s*-\s*(\d{4}|--)", years.strip())
                    year_start = None
                    year_end = None
                    if year_match:
                        try:
                            year_start = int(year_match.group(1))
                            if year_match.group(2) != "--":
                                year_end = int(year_match.group(2))
                        except ValueError:
                            pass

                    # Extraer nombre secundario del modelo (después del "/")
                    model_text = model.strip()
                    secondary_name = ""
                    if "/" in model_text:
                        parts = model_text.split("/", 1)
                        model_text = parts[0].strip()
                        secondary_name = parts[1].strip() if len(parts) > 1 else ""

                    compatibility.append(
                        {
                            "car_brand": brand_auto.strip(),
                            "car_model": model_text,
                            "secondary_name": secondary_name
                            if secondary_name
                            else None,
                            "year_start": year_start,
                            "year_end": year_end,
                        }
                    )

            # EXTRAER STOCK (del input max)
            stock = 0
            stock_input = await page.query_selector("#txtAgrega")
            if stock_input:
                max_stock = await stock_input.get_attribute("max")
                if max_stock:
                    try:
                        stock = int(max_stock)
                    except:
                        stock = 0

            # VERIFICAR SI ESTÁ EN OFERTA
            is_offer = False
            offer_badge = await page.query_selector(".label-dcto")
            if offer_badge:
                is_offer = True

            # LOG de debug para ver qué se extrajo
            self.logger.info(f"   📊 Datos extraídos:")
            self.logger.info(f"      - Nombre: {name[:50]}...")
            self.logger.info(f"      - Marca: {brand}")
            self.logger.info(f"      - Precio: ${price}")
            self.logger.info(f"      - Imágenes: {len(images)}")
            self.logger.info(f"      - Compatibilidades: {len(compatibility)}")
            self.logger.info(f"      - Stock: {stock}")
            self.logger.info(f"      - Es oferta: {is_offer}")

            return {
                "name": name,
                "sku": sku,
                "price": price,
                "url": url,
                "image_url": image_url,
                "images": images,  # Todas las imágenes
                "category_id": category.id,
                "category_name": category.name,
                "stock": stock,
                "description": description,
                "brand": brand,
                "characteristics": characteristics,  # Array de características para tabla
                "applications": compatibility,  # Lista de aplicaciones/compatibilidades
                "is_offer": is_offer,
            }

        except Exception as e:
            self.logger.warning(f"⚠️ Error extrayendo detalle del producto {sku}: {e}")
            import traceback

            self.logger.debug(traceback.format_exc())
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
            # ✋ Verificar cancelación antes de guardar
            if await self.is_job_cancelled():
                self.logger.warning("❌ Importación cancelada por el usuario")
                await self.db.rollback()
                return 0

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
                    # LOG: Ver qué estamos intentando guardar
                    apps_count = len(product_data.get("applications", []))
                    self.logger.info(
                        f"💾 Guardando {product_data['sku']}: {apps_count} aplicaciones"
                    )

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
                        existing_product.brand = product_data.get("brand", "")
                        existing_product.images = product_data.get("images", [])

                        # Guardar aplicaciones/compatibilidades en extra_data
                        # IMPORTANTE: Crear un nuevo dict para forzar la actualización en SQLAlchemy
                        extra_data = dict(existing_product.extra_data or {})
                        extra_data["applications"] = product_data.get(
                            "applications", []
                        )
                        extra_data["characteristics"] = product_data.get(
                            "characteristics", []
                        )
                        extra_data["is_offer"] = product_data.get("is_offer", False)
                        existing_product.extra_data = extra_data

                        # Marcar explícitamente que extra_data fue modificado
                        from sqlalchemy.orm.attributes import flag_modified

                        flag_modified(existing_product, "extra_data")

                        self.logger.info(
                            f"   ✏️ Actualizado (existía): {apps_count} apps en extra_data"
                        )
                    else:
                        # Crear nuevo producto
                        # Preparar extra_data con aplicaciones/compatibilidades
                        extra_data = {
                            "applications": product_data.get("applications", []),
                            "characteristics": product_data.get("characteristics", []),
                            "is_offer": product_data.get("is_offer", False),
                        }

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
                            brand=product_data.get("brand", ""),
                            images=product_data.get("images", []),
                            extra_data=extra_data,
                        )
                        self.db.add(product)
                        self.logger.info(
                            f"   ➕ Creado (nuevo): {apps_count} apps en extra_data"
                        )

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
