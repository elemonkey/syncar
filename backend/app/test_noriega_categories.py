#!/usr/bin/env python3
"""
Script de prueba independiente para categories.py de Noriega
Similar a test_noriega_playwright.py pero para categorías
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append('/Users/maxberrios/Desktop/REPUESTOS/SYNCAR.CL/backend')

# Configurar variables de entorno para simular Docker
os.environ['DATABASE_URL'] = 'postgresql://syncar:syncar123@localhost:5432/syncar'

def test_noriega_categories():
    """Probar extracción de categorías fuera del entorno Docker"""
    try:
        print("🧪 [TEST] Iniciando prueba de categories.py...")
        
        # Crear función de prueba que usa credenciales hardcodeadas
        from app.importadores.noriega.categories import get_noriega_categories_with_browser
        from playwright.sync_api import sync_playwright
        
        # Credenciales para prueba (fuera de Docker)
        rut = "77920477"
        username = "compras" 
        password = "2020"
        
        print("🔑 [TEST] Usando credenciales de prueba...")
        
        with sync_playwright() as p:
            print("🌐 [TEST] Lanzando navegador...")
            browser = p.chromium.launch(headless=False)  # Visible para debugging
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
            
            # Login manual para prueba
            print("🌍 [TEST] Navegando a página de login...")
            page.goto("https://ecommerce.noriegavanzulli.cl/b2b/", timeout=30000)
            print("✅ [TEST] Página cargada correctamente")
            
            # Llenar campos
            print("📝 [TEST] Llenando campos de login...")
            page.fill("input[name='trut']", rut)
            page.fill("input[name='tuser']", username)
            page.fill("input[name='tpass']", password)
            
            # Login
            print("🔐 [TEST] Haciendo click en botón 'Ingresar'...")
            page.click("input[name='Ingresar']")
            page.wait_for_timeout(5000)
            
            # Verificar
            current_url = page.url
            print(f"🌐 [TEST] URL después del login: {current_url}")
            
            if "b2b" in current_url and "login" not in current_url.lower():
                print("✅ [TEST] ¡Login exitoso!")
                
                # Ahora usar la función de categorías
                result = get_noriega_categories_with_browser(page)
                
                if result:
                    print("\n" + "="*60)
                    print("CATEGORÍAS EXTRAÍDAS:")
                    print("="*60)
                    
                    print(f"\n📋 X MEDIDA ({len(result['medida'])} categorías):")
                    for cat in result['medida'][:10]:  # Mostrar solo las primeras 10
                        print(f"   • {cat['name']} ({cat['url_param']})")
                    if len(result['medida']) > 10:
                        print(f"   ... y {len(result['medida']) - 10} más")
                    
                    print(f"\n📋 X FABRICANTE ({len(result['fabricante'])} categorías):")
                    for cat in result['fabricante'][:10]:  # Mostrar solo las primeras 10
                        print(f"   • {cat['name']} ({cat['url_param']})")
                    if len(result['fabricante']) > 10:
                        print(f"   ... y {len(result['fabricante']) - 10} más")
                    
                    print("\n" + "="*60)
                
                browser.close()
                return result
            else:
                print("❌ [TEST] Login falló")
                browser.close()
                return False
                
    except ImportError as e:
        print(f"❌ [TEST] Error de importación: {e}")
        return False
    except Exception as e:
        print(f"💥 [TEST] Error general: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 PRUEBA DE CATEGORÍAS NORIEGA - FUERA DE DOCKER")
    print("=" * 60)
    
    # Verificar si Playwright está instalado
    try:
        from playwright.sync_api import sync_playwright
        print("✅ [TEST] Playwright disponible")
    except ImportError:
        print("❌ [TEST] Playwright no instalado. Ejecuta: pip install playwright")
        print("       Luego: playwright install chromium")
        sys.exit(1)
    
    # Ejecutar prueba
    success = test_noriega_categories()
    
    if success:
        print("\n🎉 [TEST] ¡Prueba completada!")
    else:
        print("\n💥 [TEST] Prueba falló")
        sys.exit(1)