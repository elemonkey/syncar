"""
Router principal de la API v1
"""
from fastapi import APIRouter

# Importar routers individuales
# from .auth import router as auth_router
from .importers import router as importers_router
from .dev import router as dev_router
from .products import router as products_router
from .categories import router as categories_router
# from .jobs import router as jobs_router

api_router = APIRouter()

# Incluir routers
# api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(importers_router, prefix="/importers", tags=["importers"])
api_router.include_router(dev_router, prefix="/dev", tags=["dev"])  # 🔧 Modo desarrollo
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
# api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])

# Placeholder endpoint
@api_router.get("/")
async def api_root():
    return {"message": "API v1"}
