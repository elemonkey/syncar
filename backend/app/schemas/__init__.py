"""
Schemas de autenticación y usuarios
"""

from .auth import (
    LoginRequest,
    LoginResponse,
    PermissionBase,
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
    RoleBase,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    Token,
    TokenData,
    UserBase,
    UserCreate,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # Permission schemas
    "PermissionBase",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionResponse",
    # Role schemas
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Auth schemas
    "Token",
    "TokenData",
    "LoginRequest",
    "LoginResponse",
]
