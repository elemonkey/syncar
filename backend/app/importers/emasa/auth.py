"""
Componente de autenticación para EMASA
"""

from typing import Any, Dict

from app.core.logger import logger
from app.importers.base import AuthComponent
from playwright.async_api import Browser
from sqlalchemy.ext.asyncio import AsyncSession


class EmasaAuthComponent(AuthComponent):
    """
    Componente de autenticación para EMASA

    Realiza el login en la plataforma de EMASA
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
        self.base_url = "https://ecommerce.emasa.cl/b2b/loginvip.jsp"

    async def execute(self) -> Dict[str, Any]:
        """
        Autentica en EMASA y devuelve el contexto y página autenticados.
        """
        try:
            logger.info("🔐 Iniciando autenticación en EMASA...")

            # Crear nuevo contexto del navegador
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                ignore_https_errors=True,  # Ignorar errores de certificado SSL
            )

            # Crear nueva página
            page = await context.new_page()
            logger.info("📄 Nueva página creada")

            # Extraer credenciales (claves de la BDD: rut, username, password)
            rut_empresa = self.credentials.get("rut", "")
            usuario = self.credentials.get("username", "")
            password = self.credentials.get("password", "")

            logger.info(
                f"🔑 Credenciales extraídas: RUT={rut_empresa}, Usuario={usuario}"
            )

            # URL de login de EMASA
            login_url = "https://ecommerce.emasa.cl/b2b/loginvip.jsp"

            logger.info("=== INICIANDO AUTENTICACIÓN EMASA ===")
            logger.info(f"Navegando a: {login_url}")  # Navegar a la página de login
            await page.goto(login_url, wait_until="networkidle")

            # 📸 Screenshot página de login
            screenshot_login = "/tmp/emasa_01_login_page.png"
            await page.screenshot(path=screenshot_login)
            logger.info(f"📸 Screenshot guardado: {screenshot_login}")

            # Esperar a que los campos estén disponibles (usando id)
            logger.info("Esperando campos de login...")
            await page.wait_for_selector("input#txtrut", timeout=10000)

            # Llenar el campo de RUT (sin puntos, sin guión, sin DV)
            logger.info(f"Llenando RUT: {rut_empresa}")
            await page.fill("input#txtrut", rut_empresa)

            # Llenar el campo de Usuario
            logger.info(f"Llenando Usuario: {usuario}")
            await page.fill("input#txtuser", usuario)

            # Llenar el campo de Contraseña
            logger.info("Llenando Contraseña")
            await page.fill("input#txtpass", password)

            # 📸 Screenshot DESPUÉS de completar formulario
            screenshot_despues = "/tmp/emasa_despues_completar.png"
            await page.screenshot(path=screenshot_despues)
            logger.info(f"📸 Screenshot guardado: {screenshot_despues}")

            # 🚀 Hacer clic en el botón de login (btnlogin)
            logger.info("🚀 Haciendo clic en botón Entrar...")

            # Hacer clic y esperar navegación simultáneamente
            try:
                async with page.expect_navigation(timeout=30000):
                    await page.click("input#btnlogin")
                logger.info("✅ Navegación completada después del clic")
            except Exception as e:
                logger.warning(f"⚠️ Error en navegación: {e}")
                import asyncio

                await asyncio.sleep(3)

            # Verificar URL actual para confirmar login exitoso
            current_url = page.url
            logger.info(f"📍 URL actual después del login: {current_url}")

            # Detectar y cerrar modal/popup si existe
            logger.info("🔍 Buscando modal o popup...")
            import asyncio

            await asyncio.sleep(2)

            try:
                modal_selectors = [
                    'div[role="dialog"]',
                    ".modal",
                    "#modal",
                    ".popup",
                    ".alert",
                    "div.swal2-container",
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
                    viewport = page.viewport_size
                    logger.info(f"📐 Viewport: {viewport}")

                    x = viewport["width"] - 10
                    y = 10

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

            # 📸 Screenshot DESPUÉS del login
            try:
                screenshot_final = "/tmp/emasa_despues_login.png"
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
            logger.error(f"❌ Error en autenticación de EMASA: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "message": f"Error en login: {str(e)}",
            }
