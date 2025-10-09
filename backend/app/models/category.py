"""
Modelo para categorías de importadores
"""

from sqlalchemy import Column, Integer, String, DateTime, func, Index
from .base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    importer_name = Column(String, nullable=False, index=True)  # noriega, alsacia, etc.
    category_type = Column(String, nullable=False)  # "medida" o "fabricante"
    name = Column(String, nullable=False)  # "ABRAZADERAS", "ALTERNADORES", etc.
    url_param = Column(String, nullable=False)  # "ABRAZADERAS", "ALTERNADORES" (URL encoded)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Índices compuestos para optimizar consultas
    __table_args__ = (
        Index('idx_importer_type', 'importer_name', 'category_type'),
        Index('idx_importer_name_unique', 'importer_name', 'category_type', 'name', unique=True),
    )
    
    def __repr__(self):
        return f"<Category(importer='{self.importer_name}', type='{self.category_type}', name='{self.name}')>"