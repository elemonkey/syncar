"""
Componente de extracción de productos para Noriega
"""

from typing import Any, Dict, List, Optional

from app.importers.base import ProductsComponent
from playwright.async_api import Browser, Page
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func


class NoriegaProductsComponent(ProductsComponent):
    """
    Componente para extraer productos de Noriega

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
        # Llamar al constructor de la clase base con session_data
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
        self.products_per_category = self.config.get(
            "products_per_category", None
        )  # None = sin límite
        self.scraping_speed_ms = self.config.get("scraping_speed_ms", 1000)

        self.logger.info("⚙️ Configuración cargada:")
        if self.products_per_category:
            self.logger.info(f"   - Límite por categoría: {self.products_per_category}")
        else:
            self.logger.info(f"   - Límite por categoría: SIN LÍMITE (scrapeará todos)")
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

        Flujo:
        1. Ya estamos autenticados y en el home
        2. Por cada categoría seleccionada:
           - Construir URL según tipo (medida o fabricante)
           - Navegar a la lista de productos
           - Extraer productos (próximo paso)
        3. Respetar límites y velocidad de configuración

        Returns:
            Dict con los productos encontrados
        """
        try:
            await self.update_progress("Iniciando extracción de productos...", 10)

            self.logger.info("=" * 80)
            self.logger.info("📦 INICIANDO SCRAPING DE PRODUCTOS")
            self.logger.info("=" * 80)
            self.logger.info(
                f"📋 Categorías seleccionadas: {len(self.selected_categories)}"
            )
            if self.products_per_category:
                self.logger.info(
                    f"⚙️  Límite por categoría: {self.products_per_category}"
                )
            else:
                self.logger.info(
                    f"⚙️  Límite por categoría: SIN LÍMITE (scrapeará todos)"
                )
            self.logger.info(
                f"⏱️  Velocidad: {self.scraping_speed_ms}ms entre productos"
            )
            self.logger.info("")

            # Obtener las categorías desde la base de datos para saber su tipo
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
            all_categories = {
                cat.name: cat for cat in categories_result.scalars().all()
            }

            self.logger.info(f"✅ Categorías en BD: {len(all_categories)}")
            self.logger.info("")

            total_products = 0
            processed_categories = 0

            # 🔄 PROCESAR UNA CATEGORÍA A LA VEZ
            for index, category_id in enumerate(self.selected_categories, 1):
                # ✋ Verificar si el job fue cancelado
                if await self.is_job_cancelled():
                    self.logger.warning("❌ Importación cancelada por el usuario")
                    return {
                        "success": False,
                        "error": "Importación cancelada por el usuario",
                        "products": [],
                        "total": 0,
                        "categories_processed": processed_categories,
                    }

                self.logger.info("=" * 80)
                self.logger.info(
                    f"📂 CATEGORÍA {index}/{len(self.selected_categories)}: ID={category_id}"
                )
                self.logger.info("=" * 80)

                # Buscar la categoría en la BD por ID
                # selected_categories contiene IDs como strings, necesitamos buscar por ID
                try:
                    category_id_int = int(category_id)
                except ValueError:
                    self.logger.warning(f"⚠️  ID de categoría inválido: '{category_id}'")
                    continue

                # Buscar por ID en lugar de nombre
                category = None
                for cat in all_categories.values():
                    if cat.id == category_id_int:
                        category = cat
                        break

                if not category:
                    self.logger.warning(
                        f"⚠️  Categoría con ID '{category_id}' no encontrada en BD"
                    )
                    continue

                category_name = category.name
                self.logger.info(f"✅ Categoría encontrada: {category_name}")

                # 🔗 CONSTRUIR URL SEGÚN TIPO DE CATEGORÍA
                category_url = self._build_category_url(category_name, category)

                self.logger.info(f"🔗 URL construida: {category_url}")
                self.logger.info(f"📍 Navegando a la lista de productos...")

                # 🌐 NAVEGAR A LA CATEGORÍA
                try:
                    # ✋ Verificar cancelación antes de navegar
                    if await self.is_job_cancelled():
                        self.logger.warning("❌ Importación cancelada por el usuario")
                        return {
                            "success": False,
                            "error": "Importación cancelada por el usuario",
                            "products": [],
                            "total": 0,
                            "categories_processed": processed_categories,
                        }

                    await self.page.goto(
                        category_url, wait_until="networkidle", timeout=60000
                    )
                    self.logger.info("✅ Página de productos cargada")

                    # 📸 Screenshot de la lista de productos
                    screenshot_path = (
                        f"/tmp/noriega_category_{index}_{category_name[:20]}.png"
                    )
                    await self.page.screenshot(path=screenshot_path)
                    self.logger.info(f"📸 Screenshot: {screenshot_path}")

                    # 📊 EXTRAER NÚMERO DE RESULTADOS
                    product_count = await self._extract_product_count()
                    if product_count is not None:
                        self.logger.info(
                            f"📊 Productos disponibles en la categoría: {product_count}"
                        )
                        # Actualizar el contador en la categoría
                        category.product_count = product_count
                        await self.db.commit()

                    # 📦 EXTRAER PRODUCTOS DE LA PÁGINA
                    category_products = await self._extract_products_from_page(
                        category, category_name
                    )

                    self.logger.info("")
                    self.logger.info(
                        f"✅ Productos extraídos: {len(category_products)}"
                    )
                    self.logger.info("")

                    # � GUARDAR PRODUCTOS EN LA BASE DE DATOS
                    saved_count = await self._save_products(category_products, category)
                    total_products += saved_count

                    self.logger.info(f"✅ Productos guardados: {saved_count}")
                    self.logger.info("")

                    processed_categories += 1

                    # Actualizar progreso
                    progress = 10 + int(
                        (processed_categories / len(self.selected_categories)) * 80
                    )
                    await self.update_progress(
                        f"Procesadas {processed_categories}/{len(self.selected_categories)} categorías",
                        progress,
                    )

                except Exception as e:
                    self.logger.error(
                        f"❌ Error navegando a categoría '{category_name}': {e}"
                    )
                    continue

            await self.update_progress(
                f"Extracción completada: {processed_categories} categorías procesadas",
                100,
            )

            return {
                "success": True,
                "products": [],
                "total": total_products,
                "categories_processed": processed_categories,
                "message": f"Se procesaron {processed_categories} categorías. Navegador listo para inspección.",
            }

        except Exception as e:
            self.logger.error(f"❌ Error extrayendo productos: {e}")
            await self.update_progress(f"Error: {str(e)}", 0, "ERROR")
            return {"success": False, "error": str(e), "products": []}

    def _build_category_url(self, category_name: str, category: Any) -> str:
        """
        Construye la URL de una categoría según su tipo

        Tipos de URL:
        - X MEDIDA: resultado_medida.jsp?medida=NOMBRE
        - X Nº DE FABRICANTE: resultado_fabrica.jsp?fabrica=NOMBRE

        Args:
            category_name: Nombre de la categoría
            category: Objeto Category de la BD (tiene metadata sobre el tipo)

        Returns:
            URL completa para navegar a la lista de productos
        """
        import urllib.parse

        base_url = "https://ecommerce.noriegavanzulli.cl/b2b/"

        # Determinar tipo de categoría basándose en la URL original
        # (guardada durante la importación de categorías)
        if category.url and "resultado_medida.jsp" in category.url:
            # Categoría tipo MEDIDA
            # URL: resultado_medida.jsp?medida=NOMBRE
            encoded_name = urllib.parse.quote(category_name)
            url = f"{base_url}resultado_medida.jsp?medida={encoded_name}"
            self.logger.info(f"   Tipo: X MEDIDA")
        elif category.url and "resultado_fabrica.jsp" in category.url:
            # Categoría tipo FABRICANTE
            # URL: resultado_fabrica.jsp?fabrica=NOMBRE
            encoded_name = urllib.parse.quote(category_name)
            url = f"{base_url}resultado_fabrica.jsp?fabrica={encoded_name}"
            self.logger.info(f"   Tipo: X Nº DE FABRICANTE")
        else:
            # Fallback: intentar detectar por el nombre o usar la URL guardada
            self.logger.warning(
                f"   ⚠️  Tipo de categoría no identificado, usando URL guardada"
            )
            url = category.url

        return url

    async def _extract_product_count(self) -> Optional[int]:
        """
        Extrae el número total de productos de la categoría desde el HTML

        Busca el elemento con clase "titulo_x_medida" que contiene el texto:
        "236 resultados"

        Returns:
            Número de productos o None si no se encuentra
        """
        try:
            # Selector del elemento que contiene el número de resultados
            count_selector = "div.titulo_x_medida"

            # Buscar todos los elementos con esa clase (hay 2: nombre y conteo)
            count_elements = await self.page.query_selector_all(count_selector)

            if len(count_elements) >= 2:
                # El segundo elemento contiene el número de resultados
                count_text = await count_elements[1].text_content()
                count_text = count_text.strip()

                # Extraer el número del texto "236 resultados"
                import re

                match = re.search(r"(\d+)\s*resultados?", count_text, re.IGNORECASE)

                if match:
                    product_count = int(match.group(1))
                    self.logger.info(
                        f"   📊 Conteo extraído: {product_count} productos"
                    )
                    return product_count

            self.logger.warning("⚠️  No se pudo extraer el número de resultados")
            return None

        except Exception as e:
            self.logger.warning(f"⚠️  Error extrayendo conteo de productos: {e}")
            return None

    async def _extract_products_from_page(
        self, category: Any, category_name: str
    ) -> List[Dict[str, Any]]:
        """
        Extrae productos de la página actual

        Estrategia:
        1. Obtener lista de SKUs de la tabla principal
        2. Por cada SKU, navegar a la página de detalle
        3. Extraer datos completos (nombre, descripción, marca, origen, precio, stock, imágenes, OEM, aplicaciones)
        4. Respetar límites y velocidad

        Args:
            category: Objeto Category de la BD
            category_name: Nombre de la categoría

        Returns:
            Lista de productos extraídos
        """
        import asyncio

        products = []

        try:
            self.logger.info("🔍 Extrayendo lista de productos de la categoría...")

            # ✅ SELECTORES PARA LA LISTA DE PRODUCTOS
            SELECTORS = {
                "product_row": "table tbody tr",  # Cada fila es un producto
                "sku_link": "td.n_noriega a",  # Link con el SKU
            }

            # Esperar a que cargue la tabla
            await self.page.wait_for_selector(
                SELECTORS["product_row"], state="visible", timeout=10000
            )

            # Obtener todos los SKUs de la página
            product_rows = await self.page.query_selector_all(SELECTORS["product_row"])

            skus = []
            for row in product_rows:
                sku_elem = await row.query_selector(SELECTORS["sku_link"])
                if sku_elem:
                    sku = (await sku_elem.text_content()).strip()
                    if sku:
                        skus.append(sku)

            self.logger.info(f"📋 SKUs encontrados en la categoría: {len(skus)}")

            # Determinar cuántos productos procesar
            if self.products_per_category is None:
                # Sin límite: scrapear todos
                max_products = len(skus)
                self.logger.info(
                    f"⚙️  SIN LÍMITE: Procesando TODOS los {max_products} productos"
                )
            else:
                # Con límite: respetar configuración
                max_products = min(len(skus), self.products_per_category)
                self.logger.info(
                    f"⚙️  LÍMITE ACTIVO: Procesando máximo {max_products} de {len(skus)} productos"
                )
            self.logger.info("")

            # 🔄 PROCESAR CADA PRODUCTO INDIVIDUALMENTE
            for index, sku in enumerate(skus[:max_products], 1):
                try:
                    # ✋ Verificar cancelación antes de procesar cada producto
                    if await self.is_job_cancelled():
                        self.logger.warning("❌ Importación cancelada por el usuario")
                        return products  # Retornar productos extraídos hasta ahora

                    self.logger.info(f"📦 Producto {index}/{max_products}: SKU {sku}")

                    # Actualizar progreso en tiempo real
                    # Progreso: 20% al inicio, 90% al final de extracción
                    current_progress = 20 + int((index / max_products) * 70)

                    # Actualizar job result con información detallada
                    await self._update_job_result(
                        {
                            "total_items": max_products,
                            "processed_items": len(products),
                            "current_item": index,
                            "current_sku": sku,
                            "category": category_name,
                        }
                    )

                    # Actualizar progreso
                    await self.update_progress(
                        f"Extrayendo producto {index}/{max_products} (SKU: {sku})",
                        current_progress,
                    )

                    # Construir URL de detalle
                    detail_url = f"https://ecommerce.noriegavanzulli.cl/b2b/producto.jsp?codigo={sku}&ref=resultado_medida"

                    # Navegar a la página de detalle
                    self.logger.info(f"   🔗 Navegando a: {detail_url}")
                    await self.page.goto(
                        detail_url, wait_until="networkidle", timeout=30000
                    )

                    # Extraer datos completos del producto
                    product_data = await self._extract_product_detail(sku)

                    if product_data:
                        products.append(product_data)
                        self.logger.info(
                            f"   ✅ Extraído: {product_data.get('name', 'Sin nombre')[:50]}"
                        )
                    else:
                        self.logger.warning(
                            f"   ⚠️  No se pudieron extraer datos del producto"
                        )

                    # ⏹️ DETENER SI ALCANZAMOS EL LÍMITE
                    if (
                        self.products_per_category
                        and len(products) >= self.products_per_category
                    ):
                        self.logger.info("")
                        self.logger.info(
                            f"🛑 LÍMITE ALCANZADO: {len(products)}/{self.products_per_category} productos"
                        )
                        self.logger.info("⏹️  Deteniendo scraping de esta categoría")
                        break

                    # Respetar velocidad de scraping
                    if index < max_products:
                        delay = self.scraping_speed_ms / 1000
                        self.logger.info(
                            f"   ⏳ Esperando {delay}s antes del siguiente producto..."
                        )
                        await asyncio.sleep(delay)

                    self.logger.info("")

                except Exception as e:
                    self.logger.error(f"   ❌ Error procesando SKU {sku}: {e}")
                    continue

            self.logger.info(
                f"✅ Extracción completada: {len(products)} productos procesados"
            )

        except Exception as e:
            self.logger.error(f"❌ Error extrayendo productos de la página: {e}")

        return products

    async def _extract_product_detail(self, sku: str) -> Optional[Dict[str, Any]]:
        """
        Extrae los datos completos de un producto desde su página de detalle

        URL: https://ecommerce.noriegavanzulli.cl/b2b/producto.jsp?codigo={SKU}

        Selectores reales de Noriega:
        - Nombre: id="titulo"
        - Descripción: id="producto_descripcion"
        - Marca: id="marca"
        - Origen: id="origen"
        - Precio: id="precio_lista" > .valor
        - Stock: id="precio_descuento" > .texto (Agotado=0, Disponible=999)
        - Imágenes: id="fotos" > img
        - OEM: id="numero_original" + id="numero_fabrica"
        - Aplicaciones: table.tablaAA > tbody > tr.contenidoAA

        Args:
            sku: SKU del producto

        Returns:
            Diccionario con todos los datos del producto
        """
        try:
            product_data = {"sku": sku, "extra_data": {}}

            # === NOMBRE DEL PRODUCTO ===
            try:
                name_elem = await self.page.query_selector("#titulo")
                if name_elem:
                    product_data["name"] = (await name_elem.text_content()).strip()
                    self.logger.info(f"      ✓ Nombre: {product_data['name'][:40]}...")
            except Exception as e:
                self.logger.warning(f"      ⚠️  No se pudo extraer nombre: {e}")

            # === DESCRIPCIÓN ===
            try:
                desc_elem = await self.page.query_selector("#producto_descripcion")
                if desc_elem:
                    desc_text = (await desc_elem.text_content()).strip()
                    product_data["description"] = desc_text.replace("\xa0", " ")
                    self.logger.info(
                        f"      ✓ Descripción: {len(desc_text)} caracteres"
                    )
            except Exception as e:
                self.logger.warning(f"      ⚠️  No se pudo extraer descripción: {e}")

            # === MARCA ===
            try:
                brand_elem = await self.page.query_selector("#marca")
                if brand_elem:
                    product_data["brand"] = (await brand_elem.text_content()).strip()
                    self.logger.info(f"      ✓ Marca: {product_data['brand']}")
            except Exception as e:
                self.logger.warning(f"      ⚠️  No se pudo extraer marca: {e}")

            # === ORIGEN ===
            try:
                origin_elem = await self.page.query_selector("#origen")
                if origin_elem:
                    product_data["extra_data"]["origin"] = (
                        await origin_elem.text_content()
                    ).strip()
                    self.logger.info(
                        f"      ✓ Origen: {product_data['extra_data']['origin']}"
                    )
            except Exception as e:
                self.logger.warning(f"      ⚠️  No se pudo extraer origen: {e}")

            # === PRECIO ===
            try:
                price_container = await self.page.query_selector("#precio_lista")
                if price_container:
                    price_elem = await price_container.query_selector(".valor")
                    if price_elem:
                        price_text = (await price_elem.text_content()).strip()
                        product_data["price"] = self._parse_price(price_text)
                        self.logger.info(
                            f"      ✓ Precio: {product_data.get('price', 'N/A')}"
                        )
            except Exception as e:
                self.logger.warning(f"      ⚠️  No se pudo extraer precio: {e}")

            # === STOCK ===
            try:
                stock_container = await self.page.query_selector("#precio_descuento")
                if stock_container:
                    stock_elem = await stock_container.query_selector(".texto")
                    if stock_elem:
                        stock_text = (await stock_elem.text_content()).strip()
                        # "Disponible" = 999, "Agotado" = 0
                        if "disponible" in stock_text.lower():
                            product_data["stock"] = 999
                            self.logger.info(f"      ✓ Stock: Disponible (999)")
                        elif "agotado" in stock_text.lower():
                            product_data["stock"] = 0
                            self.logger.info(f"      ✓ Stock: Agotado (0)")
                        else:
                            product_data["stock"] = 0
                            self.logger.info(f"      ✓ Stock: {stock_text} → 0")
            except Exception as e:
                self.logger.warning(f"      ⚠️  No se pudo extraer stock: {e}")

            # === IMÁGENES ===
            images = []
            try:
                fotos_container = await self.page.query_selector("#fotos")
                if fotos_container:
                    img_elements = await fotos_container.query_selector_all("img")
                    for img in img_elements:
                        src = await img.get_attribute("src")
                        if src:
                            # Convertir a URL absoluta si es necesario
                            if src.startswith("/"):
                                src = f"https://ecommerce.noriegavanzulli.cl{src}"
                            elif not src.startswith("http"):
                                src = f"https://ecommerce.noriegavanzulli.cl/b2b/{src}"
                            if src not in images:
                                images.append(src)

                if images:
                    product_data["image_url"] = images[
                        0
                    ]  # Primera imagen como principal
                    product_data["images"] = images  # Todas las imágenes en array
                    self.logger.info(f"      ✓ Imágenes: {len(images)} encontradas")
            except Exception as e:
                self.logger.warning(f"      ⚠️  No se pudieron extraer imágenes: {e}")

            # === OEM (CÓDIGOS EQUIVALENTES) ===
            oem_codes = []
            try:
                # Extraer de numero_original
                num_original = await self.page.query_selector("#numero_original")
                if num_original:
                    original_text = (await num_original.text_content()).strip()
                    if original_text:
                        oem_codes.append(original_text)

                # Extraer de numero_fabrica
                num_fabrica = await self.page.query_selector("#numero_fabrica")
                if num_fabrica:
                    fabrica_text = (await num_fabrica.text_content()).strip()
                    if fabrica_text and fabrica_text not in oem_codes:
                        oem_codes.append(fabrica_text)

                if oem_codes:
                    product_data["extra_data"]["oem"] = oem_codes
                    self.logger.info(
                        f"      ✓ OEM: {len(oem_codes)} códigos - {oem_codes}"
                    )
            except Exception as e:
                self.logger.warning(f"      ⚠️  No se pudieron extraer códigos OEM: {e}")

            # === APLICACIONES (COMPATIBILIDAD DE VEHÍCULOS) ===
            try:
                import asyncio

                # CLAVE: Las aplicaciones están en un TabbedPanel que se carga con JavaScript
                # Necesitamos hacer click en el tab "VER APLICACIÓN" primero
                try:
                    # Buscar el tab de aplicaciones por su texto
                    app_tab = await self.page.query_selector(
                        'li.TabbedPanelsTab:has-text("VER APLICACIÓN")'
                    )
                    if app_tab:
                        await app_tab.click()
                        self.logger.info(f"      🔍 Click en tab 'VER APLICACIÓN'")
                        # Esperar a que se cargue el contenido del tab
                        await asyncio.sleep(1.2)
                    else:
                        self.logger.info(
                            f"      ℹ️  No se encontró el tab de aplicaciones"
                        )
                except Exception as e:
                    self.logger.warning(f"      ⚠️  Error haciendo click en tab: {e}")

                # CLAVE: Hay DOS tablas separadas:
                # 1. <div id="cabeza_tabla"> con headers
                # 2. <div class="contenido_tabla"> con las filas de datos
                # Debemos buscar las filas directamente en toda la página

                self.logger.info(f"      🔍 Buscando filas de aplicaciones...")

                # Buscar TODAS las filas con clase contenidoAA en la página
                app_rows = await self.page.query_selector_all("tr.contenidoAA")
                self.logger.info(
                    f"      🔍 Filas encontradas con 'tr.contenidoAA': {len(app_rows)}"
                )

                if not app_rows:
                    self.logger.info(
                        f"      ℹ️  No se encontraron aplicaciones para este producto"
                    )
                else:
                    applications = []

                    for row in app_rows:
                        cells = await row.query_selector_all("td")
                        if len(cells) >= 5:
                            # Estructura de la tabla:
                            # td.col-1: Marca del auto
                            # td.col-5: Modelo del auto
                            # td.col-2: Nombre secundario (información adicional)
                            # td.col-1 (4º): Año inicio
                            # td.col-1 (5º): Año final/término
                            car_brand = (await cells[0].text_content()).strip()
                            car_model = (await cells[1].text_content()).strip()
                            secondary_name = (await cells[2].text_content()).strip()
                            year_start_text = (await cells[3].text_content()).strip()
                            year_end_text = (await cells[4].text_content()).strip()

                            try:
                                year_start = (
                                    int(year_start_text) if year_start_text else None
                                )
                                # Manejar "--" como None para año final
                                year_end = (
                                    int(year_end_text)
                                    if year_end_text and year_end_text != "--"
                                    else None
                                )

                                app_data = {
                                    "car_brand": car_brand,
                                    "car_model": car_model,
                                    "year_start": year_start,
                                    "year_end": year_end,
                                }

                                # Agregar nombre secundario solo si no está vacío
                                if secondary_name:
                                    app_data["secondary_name"] = secondary_name

                                applications.append(app_data)
                            except ValueError:
                                self.logger.warning(
                                    f"      ⚠️  Error parseando años: {year_start_text}, {year_end_text}"
                                )

                    if applications:
                        product_data["extra_data"]["applications"] = applications
                        self.logger.info(
                            f"      ✓ Aplicaciones: {len(applications)} vehículos"
                        )
                    else:
                        self.logger.info(
                            f"      ℹ️  No se encontraron aplicaciones válidas"
                        )

            except Exception as e:
                self.logger.warning(
                    f"      ⚠️  No se pudieron extraer aplicaciones: {e}"
                )

            # === SCREENSHOT DE LA PÁGINA DE DETALLE ===
            try:
                screenshot_path = f"/tmp/noriega_product_{sku}.png"
                await self.page.screenshot(path=screenshot_path)
                self.logger.info(f"      📸 Screenshot guardado: {screenshot_path}")
            except Exception as e:
                self.logger.warning(f"      ⚠️  No se pudo tomar screenshot: {e}")

            # Validar que al menos tengamos nombre
            if "name" not in product_data:
                self.logger.warning(f"      ⚠️  Producto sin nombre, usando SKU")
                product_data["name"] = f"Producto {sku}"

            return product_data

        except Exception as e:
            self.logger.error(f"      ❌ Error extrayendo detalle del producto: {e}")
            return None

    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Convierte texto de precio a float

        Noriega usa punto como separador de miles, sin símbolo $
        Ejemplos:
        - "17.920" -> 17920.0
        - "1.234.567" -> 1234567.0
        - "12990" -> 12990.0
        """
        try:
            if not price_text:
                return None

            # Remover espacios
            cleaned = price_text.strip()

            # Si tiene puntos, removerlos (son separadores de miles)
            if "." in cleaned:
                cleaned = cleaned.replace(".", "")

            # Remover cualquier símbolo de moneda si existe
            cleaned = cleaned.replace("$", "").replace("CLP", "").strip()

            # Convertir a float
            return float(cleaned) if cleaned else None

        except (ValueError, AttributeError):
            return None

    def _parse_stock(self, stock_text: str) -> Optional[int]:
        """
        Convierte texto de stock a entero

        Noriega muestra:
        - "X" = Tiene stock (cantidad desconocida)
        - "Oct-2025" = Disponible en fecha futura
        - "" (vacío) = Sin stock

        Ejemplos:
        - "X" -> 1 (disponible)
        - "Oct-2025" -> 0 (no disponible ahora, llega después)
        - "" -> 0 (sin stock)
        """
        try:
            if not stock_text:
                return 0

            stock_text = stock_text.strip().upper()

            # Si es "X" significa que hay stock
            if stock_text == "X":
                return 1  # Disponible, cantidad desconocida

            # Si contiene un guión o es una fecha, no está disponible ahora
            if "-" in stock_text or any(
                month in stock_text.upper()
                for month in [
                    "JAN",
                    "FEB",
                    "MAR",
                    "APR",
                    "MAY",
                    "JUN",
                    "JUL",
                    "AUG",
                    "SEP",
                    "OCT",
                    "NOV",
                    "DEC",
                    "ENE",
                    "FEB",
                    "MAR",
                    "ABR",
                    "MAY",
                    "JUN",
                    "JUL",
                    "AGO",
                    "SEP",
                    "OCT",
                    "NOV",
                    "DIC",
                ]
            ):
                return 0  # Llegará en el futuro

            # Intentar extraer número si lo hay
            import re

            numbers = re.findall(r"\d+", stock_text)
            if numbers:
                return int(numbers[0])

            return 0

        except (ValueError, AttributeError):
            return 0

    async def _save_products(
        self, products: List[Dict[str, Any]], category: Any
    ) -> int:
        """
        Guarda productos en la base de datos

        Args:
            products: Lista de diccionarios con datos de productos
            category: Categoría a la que pertenecen

        Returns:
            Número de productos guardados
        """
        from app.models import Product
        from sqlalchemy import select

        saved_count = 0

        try:
            # ✋ Verificar cancelación antes de guardar
            if await self.is_job_cancelled():
                self.logger.warning("❌ Importación cancelada por el usuario")
                await self.db.rollback()
                return 0

            self.logger.info(f"💾 Guardando {len(products)} productos en BD...")

            for product_data in products:
                try:
                    # Verificar si el producto ya existe (por SKU)
                    result = await self.db.execute(
                        select(Product).where(
                            Product.importer_id == category.importer_id,
                            Product.sku == product_data["sku"],
                        )
                    )
                    existing_product = result.scalar_one_or_none()

                    if existing_product:
                        # Actualizar producto existente
                        for key, value in product_data.items():
                            if hasattr(existing_product, key):
                                setattr(existing_product, key, value)
                        existing_product.last_scraped_at = func.now()
                        self.logger.info(
                            f"   ✓ Actualizado: {product_data.get('name', '')[:40]}"
                        )
                    else:
                        # Crear nuevo producto
                        new_product = Product(
                            importer_id=category.importer_id,
                            category_id=category.id,
                            sku=product_data.get("sku"),
                            name=product_data.get("name"),
                            description=product_data.get("description"),
                            price=product_data.get("price"),
                            stock=product_data.get("stock"),
                            brand=product_data.get("brand"),
                            image_url=product_data.get("image_url"),
                            images=product_data.get("images"),  # Array de imágenes
                            extra_data=product_data.get("extra_data"),
                            available=True,
                            last_scraped_at=func.now(),
                        )
                        self.db.add(new_product)
                        self.logger.info(
                            f"   ✓ Nuevo: {product_data.get('name', '')[:40]}"
                        )

                    saved_count += 1

                except Exception as e:
                    self.logger.warning(f"   ⚠️  Error guardando producto: {e}")
                    continue

            # Commit de todos los productos
            await self.db.commit()

            # Actualizar contador de productos en la categoría
            category.product_count = saved_count
            await self.db.commit()

            self.logger.info(f"✅ {saved_count} productos guardados exitosamente")

        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"❌ Error guardando productos: {e}")

        return saved_count
