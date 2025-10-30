"""
Router principal de la API v1
"""

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .auth import router as auth_router
from .categories import router as categories_router
from .dev import router as dev_router
from .importers import router as importers_router
from .products import router as products_router
from .roles import router as roles_router
from .users import router as users_router

api_router = APIRouter()

# Incluir routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, tags=["users"])
api_router.include_router(roles_router, tags=["roles"])
api_router.include_router(importers_router, prefix="/importers", tags=["importers"])
api_router.include_router(dev_router, prefix="/dev", tags=["dev"])  # 🔧 Modo desarrollo
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])


# Placeholder endpoint
@api_router.get("/")
async def api_root():
    return {"message": "API v1"}


# Endpoint de jobs para el auto-refresh del frontend
@api_router.get("/import-jobs")
async def get_import_jobs(limit: int = 10):
    """
    Obtiene los últimos import jobs.
    Usado por el sistema de auto-refresh del frontend.
    """
    from app.core.database import get_db
    from app.models import ImportJob

    async for db in get_db():
        result = await db.execute(
            select(ImportJob)
            .options(joinedload(ImportJob.importer))
            .order_by(ImportJob.created_at.desc())
            .limit(limit)
        )
        jobs = result.scalars().unique().all()

        return {
            "jobs": [
                {
                    "job_id": job.job_id,
                    "status": job.status.value,
                    "job_type": job.job_type.value,
                    "importer_name": job.importer.name.value if job.importer else None,
                    "progress": job.progress,
                    "total_items": job.total_items,
                    "processed_items": job.processed_items,
                    "created_at": job.created_at.isoformat()
                    if job.created_at
                    else None,
                    "started_at": job.started_at.isoformat()
                    if job.started_at
                    else None,
                    "completed_at": job.completed_at.isoformat()
                    if job.completed_at
                    else None,
                }
                for job in jobs
            ]
        }
