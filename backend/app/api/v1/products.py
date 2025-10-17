"""
Endpoints para productos
"""
from typing import List, Optional

from app.core.database import get_db
from app.models import Product, Category, Importer
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.get("")
async def get_products(
    importer: Optional[str] = Query(None, description="Filtrar por importador"),
    category: Optional[str] = Query(None, description="Filtrar por categoría (ID o slug)"),
    search: Optional[str] = Query(None, description="Buscar por nombre o SKU"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene lista de productos con filtros opcionales
    """
    # Construir query base
    query = select(Product).options(
        joinedload(Product.category),
        joinedload(Product.importer)
    )

    # Filtrar por importador
    if importer:
        importer_result = await db.execute(
            select(Importer).where(Importer.name == importer.upper())
        )
        importer_obj = importer_result.scalar_one_or_none()
        if importer_obj:
            query = query.where(Product.importer_id == importer_obj.id)

    # Filtrar por categoría
    if category:
        # Intentar como ID primero
        try:
            category_id = int(category)
            query = query.where(Product.category_id == category_id)
        except ValueError:
            # Si no es un ID, buscar por slug/nombre
            category_result = await db.execute(
                select(Category).where(
                    (Category.slug == category) | (Category.name == category)
                )
            )
            category_obj = category_result.scalar_one_or_none()
            if category_obj:
                query = query.where(Product.category_id == category_obj.id)

    # Buscar por nombre o SKU
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (Product.name.ilike(search_pattern)) | (Product.sku.ilike(search_pattern))
        )

    # Ordenar por fecha de actualización (más recientes primero)
    query = query.order_by(Product.updated_at.desc())

    # Paginación
    query = query.offset(skip).limit(limit)

    # Ejecutar query
    result = await db.execute(query)
    products = result.unique().scalars().all()

    # Formatear respuesta
    products_data = []
    for product in products:
        product_dict = {
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "brand": product.brand,
            "image_url": product.image_url,
            "images": product.images,
            "available": product.available,
            "category": product.category.name if product.category else None,
            "category_id": product.category_id,
            "importer": product.importer.name.lower() if product.importer else None,
            "importer_id": product.importer_id,
            "extra_data": product.extra_data,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        }
        products_data.append(product_dict)

    return {
        "products": products_data,
        "total": len(products_data),
        "skip": skip,
        "limit": limit,
    }


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene un producto específico por ID
    """
    result = await db.execute(
        select(Product)
        .options(
            joinedload(Product.category),
            joinedload(Product.importer)
        )
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        return {"error": "Producto no encontrado"}, 404

    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "brand": product.brand,
        "image_url": product.image_url,
        "images": product.images,
        "available": product.available,
        "category": {
            "id": product.category.id,
            "name": product.category.name,
            "slug": product.category.slug,
        } if product.category else None,
        "importer": {
            "id": product.importer.id,
            "name": product.importer.name.lower(),
        } if product.importer else None,
        "extra_data": product.extra_data,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }
