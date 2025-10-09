
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import uuid
import os
from sqlalchemy.orm import Session
from typing import List

from app.tasks.import_tasks import run_import_flow
from app.core.database import get_db
from app.schemas.import_job import ImportJobCreate
from app.crud import crud_import_job

router = APIRouter()

# Mock data para las categorías
FAKE_CATEGORIES = {
    "alsacia": ["Frenos", "Filtros", "Motor", "Suspensión"],
    "refax": ["Accesorios", "Iluminación", "Carrocería"],
    "noriega": ["Neumáticos", "Llantas", "Aceites"],
    "emasa": ["Herramientas", "Equipamiento Taller", "Químicos"]
}

class ImportRequest(BaseModel):
    importer_name: str
    categories: List[str]

@router.get("/{importer_name}/categories")
def get_importer_categories(importer_name: str):
    """Devuelve una lista de categorías de ejemplo para un importador."""
    return FAKE_CATEGORIES.get(importer_name.lower(), [])

@router.post("/products")
def import_products(request: ImportRequest, db: Session = Depends(get_db)):
    """Inicia trabajos de importación para una lista de categorías."""
    job_ids = []
    for category in request.categories:
        job_id = str(uuid.uuid4())
        
        # Crear el trabajo en la base de datos
        job_schema = ImportJobCreate(id=job_id, importer_name=request.importer_name)
        crud_import_job.create_import_job(db=db, job=job_schema)

        # Encolar la tarea de Celery con el ID del trabajo y la categoría
        run_import_flow.delay(job_id=job_id, category=category)
        job_ids.append(job_id)
    
    return {"job_ids": job_ids, "message": f"Iniciados {len(job_ids)} trabajos de importación para {request.importer_name}"}

@router.get("/version")
def get_version():
    return {"version": os.getenv("APP_VERSION", "local-dev")}
