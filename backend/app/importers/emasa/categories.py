"""
Componente de extracción de categorías para EMASA
"""

from typing import Any, Dict

from app.importers.base import CategoriesComponent
from playwright.async_api import Browser, Page
from sqlalchemy.ext.asyncio import AsyncSession


class EmasaCategoriesComponent(CategoriesComponent):
    """
    Componente para extraer categorías de EMASA
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
        Extrae las categorías de EMASA desde el menú principal o página de categorías

        Returns:
            Dict con las categorías encontradas
        """
        try:
            await self.update_progress("Iniciando extracción de categorías...", 30)

            # URL de la página base después del login (buscador googleo)
            # No necesitamos navegar, ya estamos en esta página después del auth
            current_url = self.page.url
            self.logger.info(f"📍 Página actual: {current_url}")
            
            # Si no estamos en buscador_googleo, navegar ahí
            if "buscador_googleo.jsp" not in current_url:
                categories_url = "https://ecommerce.emasa.cl/b2b/buscador_googleo.jsp"
                self.logger.info(f"🔗 Navegando a página de buscador: {categories_url}")
                try:
                    await self.page.goto(
                        categories_url, wait_until="networkidle", timeout=60000
                    )
                    self.logger.info("✅ Página de buscador cargada")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error navegando a {categories_url}: {e}")
            else:
                self.logger.info("✅ Ya estamos en la página de buscador")

            # 📸 Screenshot de la página de categorías
            try:
                screenshot_path = "/tmp/emasa_categorias.png"
                await self.page.screenshot(path=screenshot_path)
                self.logger.info(f"📸 Screenshot guardado: {screenshot_path}")
            except Exception as e:
                self.logger.warning(f"⚠️ No se pudo tomar screenshot: {e}")

            await self.update_progress("Extrayendo categorías...", 50)

            # EMASA: categorías desde el dropdown "Nuestras Líneas" en el menú lateral
            self.logger.info("📋 Extrayendo categorías desde 'Nuestras Líneas'...")

            # El dropdown está en el menú lateral izquierdo, bajo el título "Nuestras Líneas"
            # Selector: <li role="presentation"><a href="resultado_busqueda.jsp?cod_familia=...&nombreMarca=...">
            categories_selector = 'ul.dropdown-menu li[role="presentation"] a[href*="cod_familia"]'
            category_elements = await self.page.query_selector_all(categories_selector)

            self.logger.info(f"🔍 Encontrados {len(category_elements)} elementos de categoría")

            categories = []
            for element in category_elements:
                try:
                    # Extraer texto (nombre de categoría)
                    category_name = await element.text_content()
                    category_name = category_name.strip() if category_name else ""

                    # Extraer href (URL de la categoría)
                    href = await element.get_attribute("href")

                    if category_name and href:
                        # Construir URL completa
                        if not href.startswith("http"):
                            base_url = "https://ecommerce.emasa.cl/b2b/"
                            category_url = base_url + href
                        else:
                            category_url = href

                        # Extraer cod_familia del href para usarlo como external_id
                        import re
                        cod_familia_match = re.search(r'cod_familia=([^&]+)', href)
                        external_id = cod_familia_match.group(1) if cod_familia_match else category_name

                        categories.append(
                            {
                                "name": category_name,
                                "external_id": external_id,  # Usar cod_familia como ID
                                "url": category_url,
                                "type": "linea",  # Tipo de categoría
                            }
                        )
                        self.logger.info(f"  ✓ {category_name} ({external_id})")

                except Exception as e:
                    self.logger.warning(f"⚠️ Error extrayendo categoría: {e}")
                    continue

            await self.update_progress("Guardando categorías en base de datos...", 70)

            # Guardar categorías en la base de datos
            from app.models import Category, Importer
            from sqlalchemy import select

            # Obtener el importador
            result = await self.db.execute(
                select(Importer).where(Importer.name == self.importer_name.upper())
            )
            importer = result.scalar_one_or_none()

            if not importer:
                raise Exception(f"Importador {self.importer_name} no encontrado")

            saved_count = 0
            for cat_data in categories:
                # Verificar si la categoría ya existe
                result = await self.db.execute(
                    select(Category).where(
                        Category.external_id == cat_data["external_id"],
                        Category.importer_id == importer.id,
                    )
                )
                existing_category = result.scalar_one_or_none()

                if existing_category:
                    # Actualizar categoría existente
                    existing_category.name = cat_data["name"]
                    existing_category.url = cat_data["url"]
                    existing_category.type = cat_data["type"]
                else:
                    # Crear nueva categoría
                    category = Category(
                        name=cat_data["name"],
                        external_id=cat_data["external_id"],
                        url=cat_data["url"],
                        type=cat_data["type"],
                        importer_id=importer.id,
                        selected=False,  # Por defecto no seleccionada
                    )
                    self.db.add(category)

                saved_count += 1

            await self.db.commit()

            await self.update_progress(f"✅ {saved_count} categorías guardadas", 100)

            self.logger.info(f"✅ Total de categorías extraídas: {len(categories)}")
            self.logger.info(f"✅ Categorías guardadas en BD: {saved_count}")

            return {
                "success": True,
                "categories": categories,
                "total": len(categories),
                "message": f"Se extrajeron {len(categories)} categorías de EMASA",
            }

        except Exception as e:
            self.logger.error(f"❌ Error extrayendo categorías: {e}")
            import traceback

            self.logger.error(traceback.format_exc())

            await self.update_progress(f"❌ Error: {str(e)}", 100)

            return {
                "success": False,
                "error": str(e),
                "message": f"Error extrayendo categorías: {str(e)}",
            }
