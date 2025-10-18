"""
Componente de extracción de categorías para Noriega
"""

from typing import Any, Dict

from app.importers.base import CategoriesComponent
from playwright.async_api import Browser, Page
from sqlalchemy.ext.asyncio import AsyncSession


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
            categories_url = (
                "https://ecommerce.noriegavanzulli.cl/b2b/seleccion_medida.jsp"
            )

            self.logger.info(f"🔗 Navegando a página de categorías: {categories_url}")
            await self.page.goto(
                categories_url, wait_until="networkidle", timeout=60000
            )
            self.logger.info("✅ Página de categorías cargada")

            # 📸 Screenshot de la página de categorías
            try:
                screenshot_path = "/tmp/noriega_categorias.png"
                await self.page.screenshot(path=screenshot_path)
                self.logger.info(f"📸 Screenshot guardado: {screenshot_path}")
            except Exception as e:
                self.logger.warning(f"⚠️ No se pudo tomar screenshot: {e}")

            await self.update_progress("Extrayendo categorías...", 50)

            # Extraer categorías de la primera tabla (X MEDIDA)
            self.logger.info("📋 Extrayendo categorías de 'X MEDIDA'...")

            # Selector: tabla dentro de #listado2 > #tabla_lista
            categories_selector = "#listado2 #tabla_lista table tbody tr td a"
            category_elements = await self.page.query_selector_all(categories_selector)

            categories = []
            for element in category_elements:
                # Verificar si el job fue cancelado
                if await self.is_job_cancelled():
                    self.logger.warning("❌ Importación cancelada por el usuario")
                    return {
                        "success": False,
                        "error": "Importación cancelada por el usuario",
                        "categories": [],
                        "total": 0,
                    }

                try:
                    # Extraer texto (nombre de categoría)
                    category_name = await element.text_content()
                    category_name = category_name.strip() if category_name else ""

                    # Extraer href (URL de la categoría)
                    href = await element.get_attribute("href")

                    if category_name and href:
                        # Construir URL completa
                        if not href.startswith("http"):
                            base_url = "https://ecommerce.noriegavanzulli.cl/b2b/"
                            category_url = base_url + href
                        else:
                            category_url = href

                        categories.append(
                            {
                                "name": category_name,
                                "external_id": category_name,  # Usar el nombre como ID
                                "url": category_url,
                                "type": "medida",  # Tipo de categoría
                            }
                        )

                        self.logger.info(f"  ✓ {category_name}")

                except Exception as e:
                    self.logger.warning(f"⚠️ Error extrayendo categoría: {e}")
                    continue

            # También extraer categorías de la segunda tabla (X Nº DE FABRICANTE)
            self.logger.info("📋 Extrayendo categorías de 'X Nº DE FABRICANTE'...")

            fabricante_selector = "#listado3 #tabla_lista table tbody tr td a"
            fabricante_elements = await self.page.query_selector_all(
                fabricante_selector
            )

            for element in fabricante_elements:
                # Verificar si el job fue cancelado
                if await self.is_job_cancelled():
                    self.logger.warning("❌ Importación cancelada por el usuario")
                    return {
                        "success": False,
                        "error": "Importación cancelada por el usuario",
                        "categories": [],
                        "total": 0,
                    }

                try:
                    category_name = await element.text_content()
                    category_name = category_name.strip() if category_name else ""

                    href = await element.get_attribute("href")

                    if category_name and href:
                        if not href.startswith("http"):
                            base_url = "https://ecommerce.noriegavanzulli.cl/b2b/"
                            category_url = base_url + href
                        else:
                            category_url = href

                        categories.append(
                            {
                                "name": category_name,
                                "external_id": category_name,
                                "url": category_url,
                                "type": "fabricante",  # Tipo de categoría
                            }
                        )

                        self.logger.info(f"  ✓ {category_name} (fabricante)")

                except Exception as e:
                    self.logger.warning(f"⚠️ Error extrayendo categoría fabricante: {e}")
                    continue

            await self.update_progress(f"Categorías extraídas: {len(categories)}", 70)

            self.logger.info(f"✅ Total de categorías extraídas: {len(categories)}")
            self.logger.info(
                f"   - Por medida: {sum(1 for c in categories if c.get('type') == 'medida')}"
            )
            self.logger.info(
                f"   - Por fabricante: {sum(1 for c in categories if c.get('type') == 'fabricante')}"
            )

            # 💾 Guardar categorías en la base de datos
            await self.update_progress(
                "Guardando categorías en la base de datos...", 80
            )
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
            existing_categories = (
                (
                    await self.db.execute(
                        select(Category).where(Category.importer_id == importer.id)
                    )
                )
                .scalars()
                .all()
            )

            for cat in existing_categories:
                await self.db.delete(cat)

            self.logger.info(
                f"🗑️  Eliminadas {len(existing_categories)} categorías antiguas"
            )

            # Crear nuevas categorías
            saved_count = 0
            for cat_data in categories:
                # Verificar si el job fue cancelado
                if await self.is_job_cancelled():
                    self.logger.warning("❌ Guardado cancelado por el usuario")
                    await self.db.rollback()
                    return {
                        "success": False,
                        "error": "Importación cancelada por el usuario",
                        "categories": [],
                        "total": 0,
                    }

                try:
                    # Crear slug del nombre
                    import re

                    slug = re.sub(r"[^a-z0-9]+", "-", cat_data["name"].lower()).strip(
                        "-"
                    )

                    category = Category(
                        importer_id=importer.id,
                        name=cat_data["name"],
                        slug=slug,
                        url=cat_data["url"],
                        external_id=cat_data["external_id"],
                        product_count=0,  # Se actualizará al importar productos
                    )

                    self.db.add(category)
                    saved_count += 1

                except Exception as e:
                    self.logger.warning(
                        f"⚠️ Error guardando categoría {cat_data['name']}: {e}"
                    )
                    continue

            # Commit de todas las categorías
            await self.db.commit()
            self.logger.info(
                f"✅ {saved_count} categorías guardadas en la base de datos"
            )

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
