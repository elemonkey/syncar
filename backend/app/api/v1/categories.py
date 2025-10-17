"""
Endpoints para categorías
"""
from typing import Optional

from app.core.database import get_db
from app.models import Category, Importer
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.get("")
async def get_categories(
    importer: Optional[str] = Query(None, description="Filtrar por importador"),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene lista de categorías con filtros opcionales
    """
    # Construir query base
    query = select(Category).options(joinedload(Category.importer))

    # Filtrar por importador
    if importer:
        importer_result = await db.execute(
            select(Importer).where(Importer.name == importer.upper())
        )
        importer_obj = importer_result.scalar_one_or_none()
        if importer_obj:
            query = query.where(Category.importer_id == importer_obj.id)

    # Ordenar por nombre
    query = query.order_by(Category.name)

    # Ejecutar query
    result = await db.execute(query)
    categories = result.unique().scalars().all()

    # Formatear respuesta
    categories_data = []
    for category in categories:
        category_dict = {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "url": category.url,
            "product_count": category.product_count,
            "importer": category.importer.name.lower() if category.importer else None,
            "importer_id": category.importer_id,
            "selected": category.selected,
            "created_at": category.created_at.isoformat() if category.created_at else None,
            "updated_at": category.updated_at.isoformat() if category.updated_at else None,
        }
        categories_data.append(category_dict)

    return {
        "categories": categories_data,
        "total": len(categories_data),
    }


@router.get("/{category_id}")
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene una categoría específica por ID
    """
    result = await db.execute(
        select(Category)
        .options(joinedload(Category.importer))
        .where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()

    if not category:
        return {"error": "Categoría no encontrada"}, 404

    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "url": category.url,
        "product_count": category.product_count,
        "importer": {
            "id": category.importer.id,
            "name": category.importer.name.lower(),
        } if category.importer else None,
        "selected": category.selected,
        "created_at": category.created_at.isoformat() if category.created_at else None,
        "updated_at": category.updated_at.isoformat() if category.updated_at else None,
    }
