"""
Script para inspeccionar la estructura HTML de la página de productos de Noriega
Ejecutar con el navegador ya autenticado para ver los selectores
"""

import asyncio
from playwright.async_api import async_playwright


async def inspect_page():
    """Inspecciona la estructura de la página de productos"""

    async with async_playwright() as p:
        print("🌐 Abriendo navegador...")
        browser = await p.webkit.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # URL de ejemplo - ajusta según necesites
        url = "https://ecommerce.noriegavanzulli.cl/b2b/resultado_medida.jsp?medida=AMORTIGUADORES"

        print(f"📍 Navegando a: {url}")
        print("⚠️  NECESITAS HACER LOGIN MANUALMENTE PRIMERO")
        print("")
        print("PASOS:")
        print("1. El navegador se abrirá en la página de productos")
        print("2. Si te pide login, hazlo manualmente")
        print("3. Navega a una categoría con productos")
        print("4. Luego vuelve a esta terminal y presiona ENTER")

        await page.goto(url)

        input("\n⏸️  Presiona ENTER cuando estés en la página de productos... ")

        print("\n" + "="*80)
        print("🔍 INSPECCIONANDO ESTRUCTURA HTML")
        print("="*80)

        # Intentar encontrar diferentes estructuras comunes
        selectors_to_try = [
            # Tablas
            "table tbody tr",
            "table.productos tr",
            "table tr[data-product]",

            # Divs
            "div.producto",
            "div.product-item",
            "div[data-product]",
            "div.item",

            # Listas
            "ul.productos li",
            "ul.product-list li",

            # Artículos
            "article.producto",
            "article.product",
        ]

        product_container = None
        product_selector = None

        for selector in selectors_to_try:
            try:
                elements = await page.query_selector_all(selector)
                if len(elements) > 0:
                    print(f"\n✅ Encontrado: {selector}")
                    print(f"   📊 Elementos: {len(elements)}")
                    product_selector = selector
                    product_container = elements[0]
                    break
            except:
                continue

        if product_container:
            print(f"\n📦 SELECTOR DE PRODUCTOS: {product_selector}")
            print("\n🔍 HTML del primer producto:")
            print("-" * 80)
            html = await product_container.inner_html()
            print(html[:1000])  # Primeros 1000 caracteres
            print("-" * 80)

            # Intentar identificar campos comunes
            print("\n🏷️  BUSCANDO CAMPOS ESPECÍFICOS:")

            fields_to_find = {
                "Nombre/Título": ["h1", "h2", "h3", "h4", ".nombre", ".title", ".producto-nombre", ".name"],
                "SKU/Código": [".sku", ".codigo", ".code", ".producto-sku", "span:has-text('SKU')"],
                "Precio": [".precio", ".price", ".producto-precio", "span:has-text('$')"],
                "Stock": [".stock", ".disponibilidad", ".availability", "span:has-text('Stock')"],
                "Imagen": ["img", ".imagen", ".image", ".producto-imagen"],
                "Descripción": [".descripcion", ".description", ".desc", "p"],
                "Marca": [".marca", ".brand", "span:has-text('Marca')"],
            }

            for field_name, selectors in fields_to_find.items():
                for sel in selectors:
                    try:
                        elem = await product_container.query_selector(sel)
                        if elem:
                            if sel == "img" or "imagen" in sel or "image" in sel:
                                value = await elem.get_attribute("src")
                            else:
                                value = await elem.text_content()
                            print(f"\n   {field_name}:")
                            print(f"      Selector: {sel}")
                            print(f"      Valor: {value[:100] if value else 'N/A'}")
                            break
                    except:
                        continue

        else:
            print("\n❌ No se pudo identificar automáticamente el selector de productos")
            print("\n💡 INSPECCIÓN MANUAL:")
            print("   1. Abre el Inspector de Safari (Cmd+Opt+I)")
            print("   2. Inspecciona un producto en la página")
            print("   3. Identifica el selector CSS del contenedor de productos")
            print("   4. Copia la estructura HTML y compártela")

        print("\n" + "="*80)
        print("📸 Tomando screenshot...")
        await page.screenshot(path="/tmp/noriega_products_inspection.png", full_page=True)
        print("✅ Screenshot guardado: /tmp/noriega_products_inspection.png")

        print("\n⏸️  El navegador permanecerá abierto para inspección manual")
        print("🛑 Presiona Ctrl+C para cerrar")

        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            print("\n🔒 Cerrando navegador...")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_page())
