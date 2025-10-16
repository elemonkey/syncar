#!/usr/bin/env python
"""
🔧 Script de desarrollo para Noriega Scraper

Este script abre Safari (WebKit) en modo visible para desarrollar el scraper
de forma interactiva. Las credenciales se cargan desde la base de datos.

Uso:
    python scripts/dev_noriega_scraper.py

O desde la raíz del proyecto:
    ./backend/venv/bin/python backend/scripts/dev_noriega_scraper.py
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from playwright.async_api import async_playwright
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import AsyncSessionLocal
from app.core.logger import logger
from app.models import Importer


async def main():
    """Función principal del scraper de desarrollo"""

    logger.info("=" * 80)
    logger.info("🔧 MODO DESARROLLO - Noriega Scraper")
    logger.info("=" * 80)

    # 1. Obtener credenciales de la base de datos
    logger.info("\n📋 Cargando credenciales desde la base de datos...")
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Importer)
            .options(joinedload(Importer.config))
            .where(Importer.name == "NORIEGA")
        )
        importer = result.unique().scalar_one_or_none()

        if not importer:
            logger.error("❌ Importador NORIEGA no encontrado en la base de datos")
            logger.info("💡 Asegúrate de haber configurado las credenciales en /configuracion")
            return

        if not importer.config or not importer.config.credentials:
            logger.error("❌ No hay credenciales configuradas para NORIEGA")
            logger.info("💡 Ve a http://localhost:3001/configuracion y configura:")
            logger.info("   - RUT")
            logger.info("   - Usuario")
            logger.info("   - Contraseña")
            return

        credentials = importer.config.credentials
        logger.info(f"✅ Credenciales cargadas:")
        logger.info(f"   📌 RUT: {credentials.get('rut')}")
        logger.info(f"   👤 Usuario: {credentials.get('username')}")
        logger.info(f"   🔑 Contraseña: {'*' * len(credentials.get('password', ''))}")

    # 2. Abrir navegador Safari (WebKit)
    logger.info("\n🌐 Abriendo Safari (WebKit)...")
    async with async_playwright() as p:
        # 🍎 Usar WebKit (Safari) en lugar de Chromium
        browser = await p.webkit.launch(
            headless=False,  # ✅ Modo visible
            slow_mo=1000     # Ralentizar 1 segundo entre acciones para ver qué hace
        )

        logger.info("✅ Safari abierto")

        # Crear contexto
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
        )

        # Crear página
        page = await context.new_page()
        logger.info("📄 Nueva página creada")

        try:
            # 3. Navegar a Noriega
            base_url = "https://ecommerce.noriegavanzulli.cl/b2b/loginvip.jsp"
            logger.info(f"\n🌍 Navegando a {base_url}")

            await page.goto(base_url, timeout=30000)
            logger.info(f"✅ Página cargada: {page.url}")

            # Tomar screenshot
            screenshot_path = "/tmp/noriega_inicio.png"
            await page.screenshot(path=screenshot_path)
            logger.info(f"📸 Screenshot guardado: {screenshot_path}")

            # 4. Esperar y mostrar directrices
            logger.info("\n" + "=" * 80)
            logger.info("⏸️  ESPERANDO TUS DIRECTRICES")
            logger.info("=" * 80)
            logger.info("\n👀 Revisa el navegador Safari que se acaba de abrir")
            logger.info("🔍 Identifica los siguientes elementos:")
            logger.info("")
            logger.info("1️⃣  ¿Hay un botón de LOGIN o INGRESAR?")
            logger.info("    → Si hay, dime el texto exacto del botón")
            logger.info("")
            logger.info("2️⃣  ¿Hay campos de RUT, Usuario y/o Contraseña visibles?")
            logger.info("    → Si hay, inspecciona y dime los selectores (id, name, class)")
            logger.info("")
            logger.info("3️⃣  ¿Se necesita hacer algún click primero para ver el formulario?")
            logger.info("    → Si es así, dime qué elemento clickear")
            logger.info("")
            logger.info("💡 TIPS:")
            logger.info("   • Click derecho → Inspeccionar en cualquier elemento")
            logger.info("   • Busca: <input>, <button>, <form>")
            logger.info("   • Anota los atributos: id='...', name='...', class='...'")
            logger.info("")
            logger.info("=" * 80)

            # Mantener el navegador abierto para inspección
            logger.info("\n⏱️  El navegador permanecerá abierto por 10 minutos")
            logger.info("    Presiona Ctrl+C para cerrar antes")

            # Esperar 10 minutos (600 segundos)
            await asyncio.sleep(600)

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  Interrupción detectada (Ctrl+C)")
            logger.info("🔒 Cerrando navegador...")
        except Exception as e:
            logger.error(f"\n❌ Error: {e}")
            import traceback
            logger.error(traceback.format_exc())

            # En caso de error, mantener abierto 60 segundos
            logger.info("\n⏱️  Navegador abierto 60 segundos para inspección del error...")
            await asyncio.sleep(60)
        finally:
            logger.info("👋 Cerrando navegador...")
            await browser.close()
            logger.info("✅ Navegador cerrado")


if __name__ == "__main__":
    logger.info("🚀 Iniciando script de desarrollo...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Script terminado por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("\n✅ Script finalizado")
