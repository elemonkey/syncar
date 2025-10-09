"""
Schemas para categorías de importadores
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    importer_name: str
    category_type: str  # "medida" o "fabricante"
    name: str
    url_param: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    importer_name: Optional[str] = None
    category_type: Optional[str] = None
    name: Optional[str] = None
    url_param: Optional[str] = None


class CategoryInDB(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Category(CategoryInDB):
    pass


class CategoryScrapeResult(BaseModel):
    """Resultado de la importación de categorías con monitoreo detallado (DEPRECATED - usar CategoryImportResult)"""
    importer_name: str
    medida_count: int
    fabricante_count: int
    total_scraped: int
    total_saved_db: int
    deleted_old: int
    success: bool
    message: str
    execution_time: Optional[str] = None


class CategoryImportResult(BaseModel):
    """Resultado de la importación de categorías con monitoreo detallado"""
    importer_name: str
    medida_count: int
    fabricante_count: int
    total_imported: int
    total_saved_db: int
    deleted_old: int
    success: bool
    message: str
    execution_time: Optional[str] = None
    
    
class CategoryStats(BaseModel):
    """Estadísticas de categorías por importador"""
    importer_name: str
    medida_count: int
    fabricante_count: int
    total_count: int
    last_updated: Optional[datetime] = None