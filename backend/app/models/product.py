
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from .base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True)
    price = Column(Float, nullable=False)
    importer_name = Column(String, index=True, nullable=False)
    category = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
