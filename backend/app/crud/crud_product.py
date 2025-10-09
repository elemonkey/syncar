from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.models.product import Product
from app.schemas.product import ProductCreate

def get_products(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None):
    query = db.query(Product)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.sku.ilike(search_term)
            )
        )
    return query.offset(skip).limit(limit).all()

def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product