"""
Endpoints de importadores
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.core.logger import logger
from app.models import Importer, ImporterConfig, Category, Product
from app.tasks.import_tasks import import_categories_task, import_products_task

router = APIRouter()


class ImporterConfigSchema(BaseModel):
    id: str
    name: str
    rut: str
    username: str
    password: str
    color: str
    enabled: bool


class ConfigsRequest(BaseModel):
    configs: List[ImporterConfigSchema]


@router.get("/")
async def get_importers(db: AsyncSession = Depends(get_db)):
    """Obtiene la lista de todos los importadores"""
    result = await db.execute(select(Importer))
    importers = result.scalars().all()
    return importers


@router.post("/{importer_name}/import-categories")
async def start_category_import(
    importer_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia la importación de categorías para un importador

    Args:
        importer_name: Nombre del importador (alsacia, refax, etc.)

    Returns:
        Job ID para trackear el progreso
    """
    # Verificar que el importador existe (buscar en mayúsculas)
    from app.models import ImporterType
    try:
        importer_type = ImporterType[importer_name.upper()]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Importer '{importer_name}' not found")

    result = await db.execute(
        select(Importer).where(Importer.name == importer_type)
    )
    importer = result.scalar_one_or_none()

    if not importer:
        raise HTTPException(status_code=404, detail=f"Importer '{importer_name}' not configured in database")

    # Iniciar tarea de Celery
    logger.info(f"🚀 Iniciando importación de categorías para {importer_name}")
    task = import_categories_task.delay(importer_name)

    return {
        "message": "Category import started",
        "job_id": task.id,
        "importer": importer_name
    }


@router.post("/{importer_name}/import-products")
async def start_product_import(
    importer_name: str,
    selected_categories: List[str],
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia la importación de productos para un importador

    Args:
        importer_name: Nombre del importador
        selected_categories: Lista de categorías a importar

    Returns:
        Job ID para trackear el progreso
    """
    # Verificar que el importador existe
    result = await db.execute(
        select(Importer).where(Importer.name == importer_name)
    )
    importer = result.scalar_one_or_none()

    if not importer:
        raise HTTPException(status_code=404, detail="Importer not found")

    # Iniciar tarea de Celery
    task = import_products_task.delay(importer_name, selected_categories)

    return {
        "message": "Product import started",
        "job_id": task.id,
        "importer": importer_name,
        "categories": selected_categories
    }


@router.get("/configs")
async def get_configs(db: AsyncSession = Depends(get_db)):
    """Obtiene todas las configuraciones de importadores"""
    from sqlalchemy.orm import joinedload

    # Usar joinedload para cargar la relación importer de forma eager
    result = await db.execute(
        select(ImporterConfig).options(joinedload(ImporterConfig.importer))
    )
    configs = result.unique().scalars().all()

    # Convertir a formato esperado por el frontend
    configs_list = []
    for config in configs:
        configs_list.append({
            "id": config.importer.name.lower() if config.importer else str(config.importer_id),
            "name": config.importer.name if config.importer else "Unknown",
            "rut": config.credentials.get("rut", "") if config.credentials else "",
            "username": config.credentials.get("username", "") if config.credentials else "",
            "password": config.credentials.get("password", "") if config.credentials else "",
            "color": "blue",  # Default color
            "enabled": config.is_active
        })

    return {"configs": configs_list}


@router.post("/configs")
async def save_configs(
    request: ConfigsRequest,
    db: AsyncSession = Depends(get_db)
):
    """Guarda las configuraciones de importadores"""
    from app.models import ImporterType

    try:
        for config_data in request.configs:
            # Convertir el nombre al valor del enum
            try:
                importer_name_enum = ImporterType[config_data.name.upper()]
            except KeyError:
                raise HTTPException(status_code=400, detail=f"Invalid importer name: {config_data.name}")

            # Buscar o crear importador
            result = await db.execute(
                select(Importer).where(Importer.name == importer_name_enum)
            )
            importer = result.scalar_one_or_none()

            if not importer:
                # Crear importador si no existe
                importer = Importer(
                    name=importer_name_enum,
                    display_name=config_data.name,
                    base_url=f"https://{config_data.name.lower()}.cl",  # URL por defecto
                    is_active=config_data.enabled
                )
                db.add(importer)
                await db.flush()

            # Buscar o crear configuración
            result = await db.execute(
                select(ImporterConfig).where(ImporterConfig.importer_id == importer.id)
            )
            importer_config = result.scalar_one_or_none()

            credentials = {
                "rut": config_data.rut,
                "username": config_data.username,
                "password": config_data.password
            }

            if importer_config:
                # Actualizar configuración existente
                importer_config.credentials = credentials
                importer_config.is_active = config_data.enabled
            else:
                # Crear nueva configuración
                importer_config = ImporterConfig(
                    importer_id=importer.id,
                    credentials=credentials,
                    is_active=config_data.enabled
                )
                db.add(importer_config)

        await db.commit()

        return {"message": "Configurations saved successfully"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories(
    importer: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todas las categorías, opcionalmente filtradas por importador"""
    from sqlalchemy.orm import joinedload

    query = select(Category).options(joinedload(Category.importer))

    if importer:
        query = query.join(Importer).where(Importer.name == importer.upper())

    result = await db.execute(query)
    categories = result.scalars().unique().all()

    return {
        "categories": [
            {
                "id": str(cat.id),
                "name": cat.name,
                "slug": cat.slug,
                "external_id": cat.external_id,
                "url": cat.url,
                "product_count": cat.product_count,
                "importer": cat.importer.name if cat.importer else None,
                "created_at": cat.created_at.isoformat() if cat.created_at else None,
            }
            for cat in categories
        ],
        "total": len(categories)
    }


@router.get("/products")
async def get_products(
    importer: str = None,
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todos los productos, opcionalmente filtrados"""
    query = select(Product)

    if importer:
        query = query.join(Category).join(Importer).where(Importer.name == importer)

    if category:
        query = query.join(Category).where(Category.slug == category)

    result = await db.execute(query)
    products = result.scalars().all()

    return {"products": [
        {
            "id": prod.id,
            "sku": prod.sku,
            "name": prod.name,
            "price": float(prod.price) if prod.price else 0,
            "stock": prod.stock or 0,
            "category": prod.category.name if prod.category else None,
            "importer": prod.category.importer.name if prod.category and prod.category.importer else None,
            "description": prod.description,
            "image_url": prod.images[0] if prod.images else None,
            "updated_at": prod.updated_at.isoformat() if prod.updated_at else None
        }
        for prod in products
    ]}
