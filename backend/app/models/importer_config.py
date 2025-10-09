"""
Modelo para configuraciones de importadores
"""

from sqlalchemy import Column, String, Text, DateTime, func, Boolean
from .base import Base


class ImporterConfig(Base):
    __tablename__ = "importer_configs"

    importer_name = Column(String, primary_key=True, index=True)  # alsacia, noriega, refax, emasa
    display_name = Column(String, nullable=False)  # Nombre para mostrar en UI
    is_active = Column(Boolean, default=True)  # Si el importador está activo
    
    # Campos de configuración (JSON como texto)
    config_fields = Column(Text, nullable=True)  # JSON con campos específicos por importador
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ImporterConfig(importer_name='{self.importer_name}', display_name='{self.display_name}')>"