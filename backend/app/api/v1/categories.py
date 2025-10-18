"""
Endpoints para categorías
"""

from typing import List, Optional

from app.core.database import get_db
from app.models import Category, Importer, Product
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

router = APIRouter()


class DeleteCategoriesRequest(BaseModel):
    category_ids: List[int]
    importer_id: int


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
            "created_at": category.created_at.isoformat()
            if category.created_at
            else None,
            "updated_at": category.updated_at.isoformat()
            if category.updated_at
            else None,
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
        }
        if category.importer
        else None,
        "selected": category.selected,
        "created_at": category.created_at.isoformat() if category.created_at else None,
        "updated_at": category.updated_at.isoformat() if category.updated_at else None,
    }


@router.post("/delete-multiple")
async def delete_multiple_categories(
    request: DeleteCategoriesRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Elimina múltiples categorías por sus IDs para un importador específico.
    También elimina los productos asociados a esas categorías.
    """
    if not request.category_ids:
        raise HTTPException(
            status_code=400, detail="No se proporcionaron IDs de categorías"
        )

    try:
        # Verificar que todas las categorías pertenecen al importador especificado
        result = await db.execute(
            select(Category).where(
                Category.id.in_(request.category_ids),
                Category.importer_id == request.importer_id,
            )
        )
        categories_to_delete = result.scalars().all()

        if len(categories_to_delete) != len(request.category_ids):
            raise HTTPException(
                status_code=400,
                detail="Algunas categorías no pertenecen al importador especificado o no existen",
            )

        # Primero, eliminar todos los productos asociados a estas categorías
        delete_products_result = await db.execute(
            delete(Product).where(Product.category_id.in_(request.category_ids))
        )
        products_deleted = delete_products_result.rowcount

        # Luego, eliminar las categorías
        await db.execute(
            delete(Category).where(
                Category.id.in_(request.category_ids),
                Category.importer_id == request.importer_id,
            )
        )
        await db.commit()

        message = f"Se eliminaron {len(request.category_ids)} categorías correctamente"
        if products_deleted > 0:
            message += f" y {products_deleted} productos asociados"

        return {
            "success": True,
            "deleted_count": len(request.category_ids),
            "products_deleted": products_deleted,
            "message": message,
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al eliminar categorías: {str(e)}"
        )
