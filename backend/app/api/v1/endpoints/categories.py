"""
Endpoints para categorías de importadores
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from app.core.database import get_db
from app.crud import crud_category
from app.schemas.category import Category, CategoryScrapeResult, CategoryImportResult, CategoryStats

router = APIRouter()


@router.get("/categories/{importer_name}", response_model=List[Category])
def get_categories_by_importer(
    importer_name: str,
    category_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener todas las categorías de un importador
    
    - **importer_name**: noriega, alsacia, refax, emasa
    - **category_type**: medida, fabricante (opcional, si no se especifica devuelve ambos)
    """
    categories = crud_category.get_categories_by_importer(db, importer_name, category_type)
    return categories


@router.post("/categories/{importer_name}/scrape", response_model=CategoryScrapeResult, deprecated=True)
async def scrape_categories(
    importer_name: str,
    db: Session = Depends(get_db)
):
    """
    ⚠️ DEPRECATED: Ejecutar importación de categorías para un importador específico
    
    Este endpoint está marcado como obsoleto. Use /import en su lugar.
    Actualmente solo soporta 'noriega'
    """
    if importer_name.lower() != "noriega":
        raise HTTPException(
            status_code=400, 
            detail=f"Importación de categorías no implementado para {importer_name}"
        )
    
    try:
        import time
        start_time = time.time()
        
        print(f"⚠️ [API] DEPRECATED: Endpoint /scrape usado. Migrar a /import")
        print(f"🚀 [API] Iniciando importación de categorías para {importer_name}")
        
        # Importar la función de importación
        from app.importadores.noriega.categories import import_and_save_noriega_categories
        
        result = await import_and_save_noriega_categories()
        
        execution_time = f"{time.time() - start_time:.2f}s"
        print(f"⏱️ [API] Importación completada en {execution_time}")
        
        if result["success"]:
            stats = result.get("stats", {})
            categories_data = result.get("categories_data", {})
            
            medida_count = len(categories_data.get("medida", []))
            fabricante_count = len(categories_data.get("fabricante", []))
            total_scraped = medida_count + fabricante_count
            
            print(f"📊 [API] Estadísticas finales:")
            print(f"   • Importadas: {total_scraped} categorías")
            print(f"   • Guardadas en BD: {stats.get('created', 0)} categorías")
            print(f"   • Eliminadas anteriores: {stats.get('deleted', 0)} categorías")
            
            return CategoryScrapeResult(
                importer_name=importer_name,
                medida_count=medida_count,
                fabricante_count=fabricante_count,
                total_scraped=total_scraped,
                total_saved_db=stats.get("created", 0),
                deleted_old=stats.get("deleted", 0),
                success=True,
                message=result["message"],
                execution_time=execution_time
            )
        else:
            return CategoryScrapeResult(
                importer_name=importer_name,
                medida_count=0,
                fabricante_count=0,
                total_scraped=0,
                total_saved_db=0,
                deleted_old=0,
                success=False,
                message=result["message"],
                execution_time=execution_time
            )
            
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail="Módulo de categorías no disponible. Instalar dependencias de importación"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante importación: {str(e)}"
        )


@router.get("/categories", response_model=List[Category])
def get_all_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtener todas las categorías de todos los importadores con paginación
    """
    categories = crud_category.get_all_categories(db, skip=skip, limit=limit)
    return categories


@router.get("/categories/{importer_name}/stats", response_model=CategoryStats)
def get_categories_stats(
    importer_name: str,
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de monitoreo de categorías para un importador
    """
    from app.models.category import Category
    from sqlalchemy import func
    
    # Contar categorías por tipo
    medida_count = db.query(Category).filter(
        Category.importer_name == importer_name,
        Category.category_type == "medida"
    ).count()
    
    fabricante_count = db.query(Category).filter(
        Category.importer_name == importer_name,
        Category.category_type == "fabricante" 
    ).count()
    
    total_count = medida_count + fabricante_count
    
    # Obtener fecha de última actualización
    last_updated = db.query(func.max(Category.updated_at)).filter(
        Category.importer_name == importer_name
    ).scalar()
    
    if total_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron categorías para {importer_name}"
        )
    
    return CategoryStats(
        importer_name=importer_name,
        medida_count=medida_count,
        fabricante_count=fabricante_count,
        total_count=total_count,
        last_updated=last_updated
    )


@router.post("/categories/{importer_name}/import", response_model=CategoryImportResult)
async def import_categories(
    importer_name: str,
    db: Session = Depends(get_db)
):
    """
    Ejecutar importación de categorías para un importador específico con monitoreo detallado
    
    Endpoint nuevo que reemplaza /scrape. Actualmente solo soporta 'noriega'
    """
    if importer_name.lower() != "noriega":
        raise HTTPException(
            status_code=400, 
            detail=f"Importación de categorías no implementado para {importer_name}"
        )
    
    try:
        start_time = time.time()
        
        print(f"🚀 [API] Iniciando importación de categorías para {importer_name}")
        
        # Importar la función de importación
        from app.importadores.noriega.categories import import_and_save_noriega_categories
        
        result = await import_and_save_noriega_categories()
        execution_time = f"{time.time() - start_time:.2f}s"
        
        print(f"⏱️ [API] Importación completada en {execution_time}")
        
        if result.get("success"):
            # Obtener estadísticas actualizadas
            medida_count = crud_category.count_categories_by_type(db, importer_name, "medida")
            fabricante_count = crud_category.count_categories_by_type(db, importer_name, "fabricante")
            total_imported = medida_count + fabricante_count
            
            print(f"   • Importadas: {total_imported} categorías")
            print(f"   • Medida: {medida_count}, Fabricante: {fabricante_count}")
            
            return CategoryImportResult(
                importer_name=importer_name,
                medida_count=medida_count,
                fabricante_count=fabricante_count,
                total_imported=total_imported,
                total_saved_db=result.get("total_saved_db", 0),
                deleted_old=result.get("deleted_old", 0),
                success=True,
                message="Categorías importadas y guardadas exitosamente",
                execution_time=execution_time
            )
        else:
            return CategoryImportResult(
                importer_name=importer_name,
                medida_count=0,
                fabricante_count=0,
                total_imported=0,
                total_saved_db=0,
                deleted_old=0,
                success=False,
                message=result.get("message", "Error durante importación"),
                execution_time=execution_time
            )
            
    except ImportError:
        raise HTTPException(
            status_code=500, 
            detail="Módulo de categorías no disponible. Instalar dependencias de importación"
        )
    except Exception as e:
        print(f"❌ [API] Error durante importación: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error durante importación: {str(e)}"
        )