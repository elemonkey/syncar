"""
Esquemas Pydantic para configuraciones de importadores
"""

from pydantic import BaseModel, field_validator
from typing import Dict, Any, Optional
from datetime import datetime
import json


class ImporterConfigBase(BaseModel):
    importer_name: str
    display_name: str
    is_active: bool = True
    config_fields: Optional[Dict[str, Any]] = {}


class ImporterConfigCreate(ImporterConfigBase):
    pass


class ImporterConfigUpdate(BaseModel):
    display_name: Optional[str] = None
    is_active: Optional[bool] = None
    config_fields: Optional[Dict[str, Any]] = None


class ImporterConfig(ImporterConfigBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('config_fields', mode='before')
    @classmethod
    def parse_config_fields(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v or {}

    class Config:
        from_attributes = True
# Esquemas específicos para cada importador
class NoriegaConfig(BaseModel):
    rut: str
    username: str
    password: str


class AlsaciaConfig(BaseModel):
    username: str
    password: str


class RefaxConfig(BaseModel):
    username: str
    password: str


class EmasaConfig(BaseModel):
    username: str
    password: str