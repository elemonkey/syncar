from .auth import noriega_login_get_browser_async

async def get_noriega_categories_with_browser(page):
    try:
        print("Navegando a seleccion_medida.jsp...")
        await page.goto("https://ecommerce.noriegavanzulli.cl/b2b/seleccion_medida.jsp", timeout=30000)
        
        categories = {"medida": [], "fabricante": []}
        
        # Extraer categorias X MEDIDA
        print("Extrayendo categorias X MEDIDA...")
        medida_links = await page.query_selector_all('#listado2 table a[href*="resultado_medida.jsp"]')
        
        for link in medida_links:
            try:
                text = await link.inner_text()
                text = text.strip()
                href = await link.get_attribute('href')
                
                if 'medida=' in href:
                    param = href.split('medida=')[1]
                    categories["medida"].append({
                        "name": text,
                        "url_param": param
                    })
                    print(f"   X MEDIDA: {text}")
                    
            except Exception as e:
                print(f"   Error procesando medida: {e}")
                continue
        
        # Extraer categorias X FABRICANTE
        print("Extrayendo categorias X FABRICANTE...")
        fabricante_links = await page.query_selector_all('#listado3 table a[href*="resultado_fabrica.jsp"]')
        
        for link in fabricante_links:
            try:
                text = await link.inner_text()
                text = text.strip()
                href = await link.get_attribute('href')
                
                if 'fabrica=' in href:
                    param = href.split('fabrica=')[1]
                    categories["fabricante"].append({
                        "name": text,
                        "url_param": param
                    })
                    print(f"   X FABRICANTE: {text}")
                    
            except Exception as e:
                print(f"   Error procesando fabricante: {e}")
                continue
        
        print(f"📊 [NORIEGA CATEGORIES] Extraccion completada:")
        print(f"   📋 X MEDIDA: {len(categories['medida'])} categorias")
        print(f"   📋 X FABRICANTE: {len(categories['fabricante'])} categorias") 
        print(f"   📈 TOTAL IMPORTADO: {len(categories['medida']) + len(categories['fabricante'])} categorias")
        
        return categories
        
    except Exception as e:
        print(f"Error navegando: {str(e)}")
        return None


async def get_noriega_categories():
    try:
        print("Iniciando proceso...")
        
        browser, page = await noriega_login_get_browser_async()
        
        if not browser or not page:
            print("No se pudo hacer login")
            return None
        
        result = await get_noriega_categories_with_browser(page)
        
        await browser.close()
        return result
        
    except Exception as e:
        print(f"Error general: {str(e)}")
        return None


async def import_and_save_noriega_categories():
    """
    Función completa: importa categorías y las guarda en la base de datos
    """
    try:
        print("Iniciando importación y guardado de categorías de Noriega...")
        
        # 1. Importar categorías
        categories_data = await get_noriega_categories()
        
        if not categories_data:
            return {"success": False, "message": "Error al importar categorías"}
        
        # 2. Guardar en base de datos
        from app.core.database import SessionLocal
        from app.crud.crud_category import upsert_categories_for_importer
        
        print(f"💾 [NORIEGA CATEGORIES] Guardando en base de datos...")
        print(f"   📊 Datos a guardar:")
        print(f"      • X MEDIDA: {len(categories_data['medida'])} categorías")
        print(f"      • X FABRICANTE: {len(categories_data['fabricante'])} categorías")
        
        db = SessionLocal()
        try:
            stats = upsert_categories_for_importer(db, "noriega", categories_data)
            
            print(f"✅ [NORIEGA CATEGORIES] Guardado completado:")
            print(f"   🗑️ Eliminadas: {stats['deleted']} categorías anteriores")
            print(f"   ✨ Creadas: {stats['created']} nuevas categorías")
            print(f"   📈 Total activo: {stats['total']} categorías en BD")
            print(f"   📋 Desglose:")
            print(f"      • X MEDIDA guardadas: {len(categories_data['medida'])}")
            print(f"      • X FABRICANTE guardadas: {len(categories_data['fabricante'])}")
            print(f"   🎯 Monitoreo: Importación exitosa - {stats['total']} categorías disponibles")
            
            return {
                "success": True,
                "message": "Categorías importadas y guardadas exitosamente",
                "stats": stats,
                "categories_data": categories_data
            }
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"Error en import_and_save: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}