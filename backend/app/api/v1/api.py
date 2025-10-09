
from fastapi import APIRouter
from .endpoints.importer import router as importer_router
from .endpoints.products import router as products_router
from .endpoints.importer_config import router as importer_config_router
from .endpoints.categories import router as categories_router

api_router = APIRouter()
api_router.include_router(importer_router, prefix="/import", tags=["Importación"])
api_router.include_router(products_router, prefix="/products", tags=["Productos"])
api_router.include_router(importer_config_router, prefix="/importer-configs", tags=["Configuración de Importadores"])
api_router.include_router(categories_router, tags=["Categorías"])
