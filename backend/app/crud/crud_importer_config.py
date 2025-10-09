"""
CRUD operations para configuraciones de importadores
"""

from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.models.importer_config import ImporterConfig
from app.schemas.importer_config import ImporterConfigCreate, ImporterConfigUpdate


def get_importer_config(db: Session, importer_name: str) -> Optional[ImporterConfig]:
    """Obtiene la configuración de un importador específico"""
    return db.query(ImporterConfig).filter(ImporterConfig.importer_name == importer_name).first()


def get_all_importer_configs(db: Session) -> List[ImporterConfig]:
    """Obtiene todas las configuraciones de importadores"""
    return db.query(ImporterConfig).all()


def create_importer_config(db: Session, config: ImporterConfigCreate) -> ImporterConfig:
    """Crea una nueva configuración de importador"""
    
    # Convertir config_fields a JSON string si es necesario
    config_fields_json = json.dumps(config.config_fields) if config.config_fields else "{}"
    
    db_config = ImporterConfig(
        importer_name=config.importer_name,
        display_name=config.display_name,
        is_active=config.is_active,
        config_fields=config_fields_json
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


def update_importer_config(
    db: Session, 
    importer_name: str, 
    config_update: ImporterConfigUpdate
) -> Optional[ImporterConfig]:
    """Actualiza la configuración de un importador"""
    
    db_config = get_importer_config(db, importer_name)
    if not db_config:
        return None
    
    update_data = config_update.dict(exclude_unset=True)
    
    # Convertir config_fields a JSON string si está presente
    if "config_fields" in update_data:
        update_data["config_fields"] = json.dumps(update_data["config_fields"])
    
    for field, value in update_data.items():
        setattr(db_config, field, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config


def delete_importer_config(db: Session, importer_name: str) -> bool:
    """Elimina la configuración de un importador"""
    
    db_config = get_importer_config(db, importer_name)
    if not db_config:
        return False
    
    db.delete(db_config)
    db.commit()
    return True


def get_importer_credentials(db: Session, importer_name: str) -> Optional[dict]:
    """
    Obtiene las credenciales de un importador específico
    Retorna el config_fields parseado como dict
    """
    config = get_importer_config(db, importer_name)
    if not config or not config.config_fields:
        return None
    
    try:
        return json.loads(config.config_fields)
    except json.JSONDecodeError:
        return None


def create_default_configs(db: Session):
    """Crea las configuraciones por defecto para todos los importadores"""
    
    default_configs = [
        {
            "importer_name": "alsacia",
            "display_name": "Alsacia",
            "is_active": True,
            "config_fields": {
                "username": "",
                "password": ""
            }
        },
        {
            "importer_name": "noriega", 
            "display_name": "Noriega",
            "is_active": True,
            "config_fields": {
                "rut": "",
                "username": "",
                "password": ""
            }
        },
        {
            "importer_name": "refax",
            "display_name": "Refax", 
            "is_active": True,
            "config_fields": {
                "username": "",
                "password": ""
            }
        },
        {
            "importer_name": "emasa",
            "display_name": "Emasa",
            "is_active": True, 
            "config_fields": {
                "username": "",
                "password": ""
            }
        }
    ]
    
    for config_data in default_configs:
        # Solo crear si no existe
        existing = get_importer_config(db, config_data["importer_name"])
        if not existing:
            config_create = ImporterConfigCreate(**config_data)
            create_importer_config(db, config_create)
            print(f"✅ Configuración creada para {config_data['display_name']}")
        else:
            print(f"⚠️ Configuración ya existe para {config_data['display_name']}")