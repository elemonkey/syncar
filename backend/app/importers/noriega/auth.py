"""
Componente de autenticación para Noriega
"""

from typing import Any, Dict

from app.core.logger import logger
from app.importers.base import AuthComponent
from playwright.async_api import Browser
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

            # Detectar y cerrar modal/popup si existe
            logger.info("🔍 Buscando modal o popup...")
            import asyncio

            await asyncio.sleep(2)  # Esperar a que aparezca el modal

            try:
                # Buscar si hay un modal visible (pueden tener diferentes clases/ids)
                # Intentar detectar elementos comunes de modals
                modal_selectors = [
                    'div[role="dialog"]',
                    ".modal",
                    "#modal",
                    ".popup",
                    ".alert",
                    "div.swal2-container",  # SweetAlert
                ]

                modal_found = False
                for selector in modal_selectors:
                    try:
                        modal = await page.query_selector(selector)
                        if modal and await modal.is_visible():
                            logger.info(f"✅ Modal detectado con selector: {selector}")
                            modal_found = True
                            break
                    except Exception:
                        continue

                if modal_found:
                    # Hacer clic en la esquina superior derecha del navegador
                    # Obtener dimensiones del viewport
                    viewport = page.viewport_size
                    logger.info(f"📐 Viewport: {viewport}")

                    # Hacer clic en el último pixel superior derecho (con margen de seguridad)
                    x = viewport["width"] - 10  # 10px desde el borde derecho
                    y = 10  # 10px desde el borde superior

                    logger.info(
                        f"🖱️  Haciendo clic en esquina superior derecha: ({x}, {y})"
                    )
                    await page.mouse.click(x, y)
                    await asyncio.sleep(1)
                    logger.info("✅ Modal cerrado")
                else:
                    logger.info("ℹ️  No se detectó modal - continuando")

            except Exception as e:
                logger.warning(f"⚠️ Error buscando/cerrando modal: {e}")

            # 📸 Screenshot DESPUÉS del login (con manejo de errores)
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
