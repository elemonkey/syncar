"""
Endpoints de gestión de roles y permisos
"""

from typing import List

from app.api.v1.auth import get_current_active_user
from app.core.database import get_db
from app.models import Permission, Role, User
from app.schemas import (
    PermissionCreate,
    PermissionResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=List[RoleResponse])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Lista todos los roles
    """
    result = await db.execute(
        select(Role).options(joinedload(Role.permissions)).offset(skip).limit(limit)
    )
    roles = result.unique().scalars().all()
    return [RoleResponse.from_orm(role) for role in roles]


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Crea un nuevo rol con sus permisos

    Solo superusuarios pueden crear roles
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can create roles",
        )

    # Verificar que el rol no exista
    result = await db.execute(select(Role).where(Role.name == role_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role_data.name}' already exists",
        )

    # Crear rol
    role = Role(
        name=role_data.name,
        description=role_data.description,
        is_active=role_data.is_active,
    )

    db.add(role)
    await db.flush()  # Para obtener el ID del rol

    # Crear permisos
    if role_data.permissions:
        for perm_data in role_data.permissions:
            permission = Permission(
                role_id=role.id,
                page_name=perm_data.page_name,
                can_access=perm_data.can_access,
            )
            db.add(permission)

    await db.commit()
    await db.refresh(role)

    return RoleResponse.from_orm(role)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Obtiene un rol por ID
    """
    result = await db.execute(
        select(Role).options(joinedload(Role.permissions)).where(Role.id == role_id)
    )
    role = result.unique().scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return RoleResponse.from_orm(role)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Actualiza un rol

    Solo superusuarios pueden actualizar roles
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can update roles",
        )

    result = await db.execute(
        select(Role).options(joinedload(Role.permissions)).where(Role.id == role_id)
    )
    role = result.unique().scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Verificar unicidad del nombre si se actualiza
    if role_data.name and role_data.name != role.name:
        name_check = await db.execute(select(Role).where(Role.name == role_data.name))
        if name_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role_data.name}' already exists",
            )

    # Actualizar campos
    update_data = role_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)

    await db.commit()
    await db.refresh(role)

    return RoleResponse.from_orm(role)


@router.put("/{role_id}/permissions", response_model=RoleResponse)
async def update_role_permissions(
    role_id: int,
    permissions_data: List[PermissionCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Actualiza los permisos de un rol

    Reemplaza todos los permisos existentes
    Solo superusuarios pueden actualizar permisos
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can update permissions",
        )

    result = await db.execute(
        select(Role).options(joinedload(Role.permissions)).where(Role.id == role_id)
    )
    role = result.unique().scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Eliminar permisos existentes
    await db.execute(select(Permission).where(Permission.role_id == role_id))
    for perm in role.permissions:
        await db.delete(perm)

    # Crear nuevos permisos
    for perm_data in permissions_data:
        permission = Permission(
            role_id=role.id,
            page_name=perm_data.page_name,
            can_access=perm_data.can_access,
        )
        db.add(permission)

    await db.commit()
    await db.refresh(role)

    return RoleResponse.from_orm(role)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Elimina un rol

    Solo superusuarios pueden eliminar roles
    No se puede eliminar un rol que tenga usuarios asignados
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can delete roles",
        )

    result = await db.execute(
        select(Role).options(joinedload(Role.users)).where(Role.id == role_id)
    )
    role = result.unique().scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Verificar que no tenga usuarios asignados
    if role.users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role with {len(role.users)} assigned users",
        )

    await db.delete(role)
    await db.commit()

    return None


# ============================================================================
# Endpoints para gestión individual de permisos
# ============================================================================


@router.post(
    "/{role_id}/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    role_id: int,
    permission_data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Crea un nuevo permiso para un rol específico

    Solo superusuarios pueden crear permisos
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can create permissions",
        )

    # Verificar que el rol existe
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    # Verificar si ya existe el permiso
    existing_perm = await db.execute(
        select(Permission).where(
            Permission.role_id == role_id,
            Permission.page_name == permission_data.page_name,
        )
    )
    if existing_perm.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Permission for page '{permission_data.page_name}' already exists",
        )

    # Crear el permiso
    permission = Permission(
        role_id=role_id,
        page_name=permission_data.page_name,
        can_access=permission_data.can_access,
    )
    db.add(permission)
    await db.commit()
    await db.refresh(permission)

    return PermissionResponse.from_orm(permission)


@router.put("/{role_id}/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    role_id: int,
    permission_id: int,
    permission_data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Actualiza un permiso específico

    Solo superusuarios pueden actualizar permisos
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can update permissions",
        )

    # Buscar el permiso
    result = await db.execute(
        select(Permission).where(
            Permission.id == permission_id, Permission.role_id == role_id
        )
    )
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    # Actualizar solo can_access (page_name no cambia)
    permission.can_access = permission_data.can_access

    await db.commit()
    await db.refresh(permission)

    return PermissionResponse.from_orm(permission)


@router.delete(
    "/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_permission(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Elimina un permiso específico

    Solo superusuarios pueden eliminar permisos
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can delete permissions",
        )

    # Buscar el permiso
    result = await db.execute(
        select(Permission).where(
            Permission.id == permission_id, Permission.role_id == role_id
        )
    )
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found",
        )

    await db.delete(permission)
    await db.commit()

    return None
