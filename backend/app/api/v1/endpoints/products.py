from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.product import Product
from app.crud import crud_product

router = APIRouter()

@router.get("", response_model=List[Product])
def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    """Devuelve una lista de productos con paginación y búsqueda."""
    products = crud_product.get_products(db, skip=skip, limit=limit, search=search)
    return products