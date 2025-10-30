"""
Schemas de usuarios, roles y permisos
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

# ===== PERMISSION SCHEMAS =====


class PermissionBase(BaseModel):
    page_name: str = Field(
        ..., description="Nombre de la página (catalogo, importers, configuracion)"
    )
    can_access: bool = Field(default=True, description="Permiso de acceso")


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    can_access: Optional[bool] = None


class PermissionResponse(PermissionBase):
    id: int
    role_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===== ROLE SCHEMAS =====


class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Nombre del rol")
    description: Optional[str] = Field(
        None, max_length=255, description="Descripción del rol"
    )
    is_active: bool = Field(default=True, description="Rol activo")


class RoleCreate(RoleBase):
    permissions: Optional[List[PermissionCreate]] = Field(
        default=[], description="Permisos del rol"
    )


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


# ===== USER SCHEMAS =====


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    username: str = Field(
        ..., min_length=3, max_length=100, description="Nombre de usuario"
    )
    full_name: Optional[str] = Field(
        None, max_length=255, description="Nombre completo"
    )
    is_active: bool = Field(default=True, description="Usuario activo")
    is_superuser: bool = Field(default=False, description="Es superusuario")
    role_id: Optional[int] = Field(None, description="ID del rol asignado")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    role: Optional[RoleResponse] = None

    class Config:
        from_attributes = True


# ===== AUTH SCHEMAS =====


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    username: str = Field(..., description="Usuario o email")
    password: str = Field(..., description="Contraseña")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
