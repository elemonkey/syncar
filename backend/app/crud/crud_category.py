"""
CRUD operations para categorías de importadores
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Obtener categoría por ID"""
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories_by_importer(db: Session, importer_name: str, category_type: Optional[str] = None) -> List[Category]:
    """Obtener todas las categorías de un importador, opcionalmente filtradas por tipo"""
    query = db.query(Category).filter(Category.importer_name == importer_name)
    
    if category_type:
        query = query.filter(Category.category_type == category_type)
    
    return query.order_by(Category.name).all()


def get_all_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """Obtener todas las categorías con paginación"""
    return db.query(Category).offset(skip).limit(limit).all()


def create_category(db: Session, category: CategoryCreate) -> Category:
    """Crear nueva categoría"""
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def create_categories_bulk(db: Session, categories: List[CategoryCreate]) -> List[Category]:
    """Crear múltiples categorías de forma eficiente"""
    db_categories = []
    
    for category_data in categories:
        db_category = Category(**category_data.dict())
        db_categories.append(db_category)
    
    db.add_all(db_categories)
    db.commit()
    
    # Refresh all objects
    for db_category in db_categories:
        db.refresh(db_category)
    
    return db_categories


def update_category(db: Session, category_id: int, category_update: CategoryUpdate) -> Optional[Category]:
    """Actualizar categoría existente"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    
    if not db_category:
        return None
    
    # Actualizar solo los campos proporcionados
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """Eliminar categoría por ID"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True


def delete_categories_by_importer(db: Session, importer_name: str, category_type: Optional[str] = None) -> int:
    """Eliminar todas las categorías de un importador (útil para reemplazar durante importación)"""
    query = db.query(Category).filter(Category.importer_name == importer_name)
    
    if category_type:
        query = query.filter(Category.category_type == category_type)
    
    count = query.count()
    query.delete()
    db.commit()
    
    return count


def count_categories_by_type(db: Session, importer_name: str, category_type: Optional[str] = None) -> int:
    """Contar categorías de un importador por tipo"""
    query = db.query(Category).filter(Category.importer_name == importer_name)
    
    if category_type:
        query = query.filter(Category.category_type == category_type)
    
    return query.count()


def category_exists(db: Session, importer_name: str, category_type: str, name: str) -> bool:
    """Verificar si ya existe una categoría específica"""
    return db.query(Category).filter(
        Category.importer_name == importer_name,
        Category.category_type == category_type,
        Category.name == name
    ).first() is not None


def upsert_categories_for_importer(db: Session, importer_name: str, categories_data: dict) -> dict:
    """
    Actualizar o insertar categorías para un importador (reemplaza todas las existentes)
    
    Args:
        importer_name: Nombre del importador
        categories_data: Dict con keys "medida" y "fabricante", cada uno con lista de categorías
        
    Returns:
        Dict con estadísticas de la operación
    """
    stats = {"deleted": 0, "created": 0, "total": 0}
    
    # Eliminar categorías existentes del importador
    deleted_count = delete_categories_by_importer(db, importer_name)
    stats["deleted"] = deleted_count
    
    # Crear nuevas categorías
    new_categories = []
    
    # Procesar categorías "medida"
    for cat_data in categories_data.get("medida", []):
        new_categories.append(CategoryCreate(
            importer_name=importer_name,
            category_type="medida",
            name=cat_data["name"],
            url_param=cat_data["url_param"]
        ))
    
    # Procesar categorías "fabricante"
    for cat_data in categories_data.get("fabricante", []):
        new_categories.append(CategoryCreate(
            importer_name=importer_name,
            category_type="fabricante",
            name=cat_data["name"],
            url_param=cat_data["url_param"]
        ))
    
    if new_categories:
        created_categories = create_categories_bulk(db, new_categories)
        stats["created"] = len(created_categories)
    
    stats["total"] = stats["created"]
    
    return stats