"""
Endpoints de gestión de usuarios
"""

from typing import List

from app.api.v1.auth import get_current_active_user
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models import Role, User
from app.schemas import UserCreate, UserResponse, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Lista todos los usuarios

    Requiere autenticación
    """
    result = await db.execute(
        select(User)
        .options(joinedload(User.role).joinedload(Role.permissions))
        .offset(skip)
        .limit(limit)
    )
    users = result.unique().scalars().all()
    return [UserResponse.from_orm(user) for user in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Crea un nuevo usuario

    Requiere autenticación. Solo superusuarios pueden crear otros superusuarios.
    """
    # Verificar que el usuario no exista
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )

    # Solo superusuarios pueden crear otros superusuarios
    if user_data.is_superuser and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can create superusers",
        )

    # Verificar que el rol exista si se especifica
    if user_data.role_id:
        role_result = await db.execute(select(Role).where(Role.id == user_data.role_id))
        role = role_result.scalar_one_or_none()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with id {user_data.role_id} not found",
            )

    # Crear usuario
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        is_active=user_data.is_active,
        is_superuser=user_data.is_superuser,
        role_id=user_data.role_id,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.from_orm(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Obtiene un usuario por ID
    """
    result = await db.execute(
        select(User)
        .options(joinedload(User.role).joinedload(Role.permissions))
        .where(User.id == user_id)
    )
    user = result.unique().scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Actualiza un usuario

    Los usuarios solo pueden actualizarse a sí mismos, excepto los superusuarios
    """
    # Buscar usuario
    result = await db.execute(
        select(User)
        .options(joinedload(User.role).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    user = result.unique().scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Verificar permisos
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Verificar unicidad de email/username si se actualizan
    if user_data.email and user_data.email != user.email:
        email_check = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if email_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    if user_data.username and user_data.username != user.username:
        username_check = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if username_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    # Actualizar campos
    update_data = user_data.model_dump(exclude_unset=True)

    # Hash de password si se actualiza
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return UserResponse.from_orm(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Elimina un usuario

    Solo superusuarios pueden eliminar usuarios
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can delete users",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # No permitir eliminar al propio usuario
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )

    await db.delete(user)
    await db.commit()

    return None
