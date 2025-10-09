"""
Endpoints para gestión de configuraciones de importadores
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.importer_config import ImporterConfig, ImporterConfigCreate, ImporterConfigUpdate
from app.crud import crud_importer_config

router = APIRouter()


@router.get("", response_model=List[ImporterConfig])
def get_all_importer_configs(db: Session = Depends(get_db)):
    """Obtiene todas las configuraciones de importadores"""
    configs = crud_importer_config.get_all_importer_configs(db)
    
    # Si no hay configuraciones, crear las por defecto
    if not configs:
        crud_importer_config.create_default_configs(db)
        configs = crud_importer_config.get_all_importer_configs(db)
    
    return configs


@router.get("/{importer_name}", response_model=ImporterConfig)
def get_importer_config(importer_name: str, db: Session = Depends(get_db)):
    """Obtiene la configuración de un importador específico"""
    config = crud_importer_config.get_importer_config(db, importer_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"Configuración para {importer_name} no encontrada")
    return config


@router.post("", response_model=ImporterConfig)
def create_importer_config(config: ImporterConfigCreate, db: Session = Depends(get_db)):
    """Crea una nueva configuración de importador"""
    
    # Verificar si ya existe
    existing = crud_importer_config.get_importer_config(db, config.importer_name)
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Configuración para {config.importer_name} ya existe"
        )
    
    return crud_importer_config.create_importer_config(db, config)


@router.put("/{importer_name}", response_model=ImporterConfig)
def update_importer_config(
    importer_name: str, 
    config_update: ImporterConfigUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza la configuración de un importador"""
    
    updated_config = crud_importer_config.update_importer_config(db, importer_name, config_update)
    if not updated_config:
        raise HTTPException(status_code=404, detail=f"Configuración para {importer_name} no encontrada")
    
    return updated_config


@router.delete("/{importer_name}")
def delete_importer_config(importer_name: str, db: Session = Depends(get_db)):
    """Elimina la configuración de un importador"""
    
    success = crud_importer_config.delete_importer_config(db, importer_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Configuración para {importer_name} no encontrada")
    
    return {"message": f"Configuración para {importer_name} eliminada exitosamente"}


@router.post("/initialize")
def initialize_default_configs(db: Session = Depends(get_db)):
    """Inicializa las configuraciones por defecto para todos los importadores"""
    crud_importer_config.create_default_configs(db)
    return {"message": "Configuraciones por defecto inicializadas exitosamente"}


@router.post("/{importer_name}/test-connection")
def test_importer_connection(
    importer_name: str,
    test_data: dict,
    db: Session = Depends(get_db)
):
    """Prueba la conexión con un importador usando Selenium"""
    
    try:
        # SIMPLIFICADO: Solo usar credenciales de la base de datos
        print("🔄 [API] Usando ÚNICAMENTE credenciales de la base de datos")
        
        # Solo soportamos Noriega por ahora
        if importer_name.lower() != 'noriega':
            raise HTTPException(status_code=400, detail=f"Prueba de conexión no implementada para {importer_name}")
        
        # Importar y usar el módulo de autenticación Playwright
        from app.importadores.noriega.auth import noriega_test_login
        
        # Para Noriega - SOLO usar credenciales de la base de datos
        if importer_name.lower() == 'noriega':
            # Verificar que existe configuración en BD
            existing_config = crud_importer_config.get_importer_config(db, 'noriega')
            if not existing_config:
                raise HTTPException(status_code=404, detail="Configuración de Noriega no encontrada en base de datos")
            
            print("🔄 [API] Usando credenciales de la base de datos")
            
            # Ejecutar prueba de login directamente (la función get_noriega_credentials lee de BD)
            try:
                success, message = noriega_test_login()
                print(f"DEBUG: noriega_test_login returned - success: {success}, message: {message}")
            except Exception as e:
                print(f"DEBUG: Exception in noriega_test_login: {e}")
                import traceback
                print(f"DEBUG: Traceback: {traceback.format_exc()}")
                success = False
                message = f"Error en login de Noriega: {str(e)}"
        
        return {
            "success": success,
            "message": message,
            "importer": importer_name
        }
        
    except ImportError as e:
        raise HTTPException(
            status_code=500, 
            detail="Módulo Playwright no disponible. Instalar playwright"
        )
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error general en test_connection: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))