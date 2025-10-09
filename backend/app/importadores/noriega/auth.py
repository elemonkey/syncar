
import json
from app.core.database import SessionLocal
from app.models.importer_config import ImporterConfig
from playwright.sync_api import sync_playwright

def get_config_fields(cfg):
    if isinstance(cfg.config_fields, dict):
        return cfg.config_fields
    try:
        return json.loads(cfg.config_fields)
    except Exception:
        return {}

def get_noriega_credentials():
    session = SessionLocal()
    try:
        config = session.query(ImporterConfig).filter_by(importer_name='noriega').first()
        if not config:
            raise Exception("No se encontró configuración para Noriega.")
        
        fields = get_config_fields(config)
        rut = fields.get('rut')
        username = fields.get('username')
        password = fields.get('password')
        
        if not all([rut, username, password]):
            raise Exception("Faltan credenciales de Noriega en config_fields.")
        return rut, username, password
    finally:
        session.close()

def noriega_login():
    """Función para pruebas manuales con navegador visible"""
    rut, username, password = get_noriega_credentials()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        page.goto("https://ecommerce.noriegavanzulli.cl/b2b/")
        page.fill("input[name='trut']", rut)
        page.fill("input[name='tuser']", username)
        page.fill("input[name='tpass']", password)
        page.click("input[name='Ingresar']")
        print("Login realizado, revisa el navegador.")
        page.wait_for_timeout(3000)
        modal_detectado = False
        if page.query_selector(".modal, .popup"):
            modal_detectado = True
        if modal_detectado:
            print("Modal detectado. Haciendo click en el último pixel a la derecha...")
            box = page.viewport_size
            if box:
                x = box['width'] - 1
                y = box['height'] // 2
                page.mouse.click(x, y)
            else:
                page.mouse.click(1920, 10)
        else:
            print("No se detectó modal. Ya estás en la página de inicio.")
        input("Presiona Enter para cerrar el navegador...")

def noriega_test_login():
    """Función para API - login en modo headless"""
    try:
        print("🔄 [NORIEGA AUTH] Iniciando proceso de autenticación...")
        
        rut, username, password = get_noriega_credentials()
        print(f"🔑 [NORIEGA AUTH] Credenciales obtenidas desde base de datos")
        
        with sync_playwright() as p:
            print("🌐 [NORIEGA AUTH] Lanzando navegador Chromium en modo headless...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            
            # Ir a la página de login
            print("🌍 [NORIEGA AUTH] Navegando a https://ecommerce.noriegavanzulli.cl/b2b/...")
            page.goto("https://ecommerce.noriegavanzulli.cl/b2b/", timeout=30000)
            print("✅ [NORIEGA AUTH] Página cargada correctamente")
            
            # Llenar campos de login
            print("📝 [NORIEGA AUTH] Llenando campos de login...")
            page.fill("input[name='trut']", rut)
            print(f"   ✓ RUT rellenado: {rut}")
            page.fill("input[name='tuser']", username)
            print(f"   ✓ Usuario rellenado: {username}")
            page.fill("input[name='tpass']", password)
            print("   ✓ Contraseña rellenada")
            
            # Hacer click en login
            print("🔐 [NORIEGA AUTH] Haciendo click en botón 'Ingresar'...")
            page.click("input[name='Ingresar']")
            
            # Esperar respuesta
            print("⏳ [NORIEGA AUTH] Esperando respuesta del servidor (5 segundos)...")
            page.wait_for_timeout(5000)
            
            # Verificar si el login fue exitoso
            print("🔍 [NORIEGA AUTH] Verificando resultado del login...")
            error_selectors = [
                "text=Usuario o contraseña incorrectos",
                "text=Error",
                ".error",
                ".alert-danger"
            ]
            
            for selector in error_selectors:
                if page.query_selector(selector):
                    print(f"❌ [NORIEGA AUTH] Error encontrado: {selector}")
                    browser.close()
                    return False, "Credenciales incorrectas"
            
            # Si llegamos aquí y no hay errores, el login probablemente fue exitoso
            current_url = page.url
            print(f"🌐 [NORIEGA AUTH] URL actual después del login: {current_url}")
            browser.close()
            
            if "b2b" in current_url and "login" not in current_url.lower():
                print("✅ [NORIEGA AUTH] ¡Login exitoso! URL indica acceso correcto")
                return True, "Login exitoso"
            else:
                print("❌ [NORIEGA AUTH] Login falló - URL no indica éxito")
                return False, "Login falló - no se redirigió correctamente"
                
    except Exception as e:
        print(f"💥 [NORIEGA AUTH] Excepción durante login: {str(e)}")
        return False, f"Error durante login: {str(e)}"


def noriega_login_get_browser_sync(headless=None):
    """
    Versión síncrona para uso fuera de FastAPI (pruebas)
    """
    try:
        print("🔄 [NORIEGA AUTH] Iniciando login para obtener browser activo...")
        
        rut, username, password = get_noriega_credentials()
        print(f"🔑 [NORIEGA AUTH] Credenciales obtenidas desde base de datos")
        
        # Auto-detectar si estamos en Docker (no hay DISPLAY)
        if headless is None:
            import os
            headless = not bool(os.environ.get('DISPLAY'))
            print(f"🔍 [NORIEGA AUTH] Modo auto-detectado: headless={headless}")
        
        # Crear playwright context que se mantenga activo
        p = sync_playwright().start()
        print(f"🌐 [NORIEGA AUTH] Lanzando navegador (headless={headless})...")
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        
        # Login
        print("🌍 [NORIEGA AUTH] Navegando a https://ecommerce.noriegavanzulli.cl/b2b/...")
        page.goto("https://ecommerce.noriegavanzulli.cl/b2b/", timeout=30000)
        print("✅ [NORIEGA AUTH] Página cargada correctamente")
        
        # Llenar campos
        print("📝 [NORIEGA AUTH] Llenando campos de login...")
        page.fill("input[name='trut']", rut)
        page.fill("input[name='tuser']", username)
        page.fill("input[name='tpass']", password)
        
        # Login
        print("🔐 [NORIEGA AUTH] Haciendo click en botón 'Ingresar'...")
        page.click("input[name='Ingresar']")
        page.wait_for_timeout(5000)
        
        # Verificar
        current_url = page.url
        print(f"🌐 [NORIEGA AUTH] URL después del login: {current_url}")
        
        if "b2b" in current_url and "login" not in current_url.lower():
            print("✅ [NORIEGA AUTH] ¡Login exitoso! Devolviendo browser activo")
            # Devolver browser, page y playwright instance para cerrar después
            return browser, page
        else:
            print("❌ [NORIEGA AUTH] Login falló")
            browser.close()
            p.stop()
            return None, None
                
    except Exception as e:
        print(f"💥 [NORIEGA AUTH] Error obteniendo browser: {str(e)}")
        try:
            if 'browser' in locals():
                browser.close()
            if 'p' in locals():
                p.stop()
        except:
            pass
        return None, None


async def noriega_login_get_browser_async(headless=None):
    """
    Versión asíncrona para uso en FastAPI
    """
    try:
        print("🔄 [NORIEGA AUTH] Iniciando login para obtener browser activo...")
        
        rut, username, password = get_noriega_credentials()
        print(f"🔑 [NORIEGA AUTH] Credenciales obtenidas desde base de datos")
        
        # Auto-detectar si estamos en Docker (no hay DISPLAY)
        if headless is None:
            import os
            headless = not bool(os.environ.get('DISPLAY'))
            print(f"🔍 [NORIEGA AUTH] Modo auto-detectado: headless={headless}")
        
        # Usar API async de Playwright
        from playwright.async_api import async_playwright
        
        p = await async_playwright().start()
        print(f"🌐 [NORIEGA AUTH] Lanzando navegador (headless={headless})...")
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        # Login
        print("🌍 [NORIEGA AUTH] Navegando a https://ecommerce.noriegavanzulli.cl/b2b/...")
        await page.goto("https://ecommerce.noriegavanzulli.cl/b2b/", timeout=30000)
        print("✅ [NORIEGA AUTH] Página cargada correctamente")
        
        # Llenar campos
        print("📝 [NORIEGA AUTH] Llenando campos de login...")
        await page.fill("input[name='trut']", rut)
        await page.fill("input[name='tuser']", username)
        await page.fill("input[name='tpass']", password)
        
        # Login
        print("🔐 [NORIEGA AUTH] Haciendo click en botón 'Ingresar'...")
        await page.click("input[name='Ingresar']")
        await page.wait_for_timeout(5000)
        
        # Verificar
        current_url = page.url
        print(f"🌐 [NORIEGA AUTH] URL después del login: {current_url}")
        
        if "b2b" in current_url and "login" not in current_url.lower():
            print("✅ [NORIEGA AUTH] ¡Login exitoso! Devolviendo browser activo")
            return browser, page
        else:
            print("❌ [NORIEGA AUTH] Login falló")
            await browser.close()
            await p.stop()
            return None, None
                
    except Exception as e:
        print(f"💥 [NORIEGA AUTH] Error obteniendo browser: {str(e)}")
        try:
            if 'browser' in locals():
                await browser.close()
            if 'p' in locals():
                await p.stop()
        except:
            pass
        return None, None

