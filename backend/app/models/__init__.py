"""
Modelos de base de datos
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


# ===== ENUMS =====

class ImporterType(str, enum.Enum):
    """Tipos de importadores"""
    ALSACIA = "ALSACIA"
    REFAX = "REFAX"
    NORIEGA = "NORIEGA"
    EMASA = "EMASA"


class JobStatus(str, enum.Enum):
    """Estados de los trabajos de importación"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    """Tipos de trabajos de importación"""
    CATEGORIES = "categories"
    PRODUCTS = "products"


# ===== MODELOS =====

class User(Base):
    """Modelo de usuarios"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Importer(Base):
    """Modelo de importadores/proveedores"""
    __tablename__ = "importers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(SQLEnum(ImporterType), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    categories: Mapped[List["Category"]] = relationship("Category", back_populates="importer", cascade="all, delete-orphan")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="importer", cascade="all, delete-orphan")
    jobs: Mapped[List["ImportJob"]] = relationship("ImportJob", back_populates="importer", cascade="all, delete-orphan")
    config: Mapped[Optional["ImporterConfig"]] = relationship("ImporterConfig", back_populates="importer", uselist=False, cascade="all, delete-orphan")


class Category(Base):
    """Modelo de categorías de productos"""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    importer_id: Mapped[int] = mapped_column(Integer, ForeignKey("importers.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    url: Mapped[Optional[str]] = mapped_column(String(500))
    external_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    product_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    importer: Mapped["Importer"] = relationship("Importer", back_populates="categories")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    """Modelo de productos"""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    importer_id: Mapped[int] = mapped_column(Integer, ForeignKey("importers.id"), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"))

    # Información básica
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Precios
    price: Mapped[Optional[float]] = mapped_column(Float)
    original_price: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="CLP")

    # Stock
    stock: Mapped[Optional[int]] = mapped_column(Integer)
    available: Mapped[bool] = mapped_column(Boolean, default=True)

    # Identificación externa
    external_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    url: Mapped[Optional[str]] = mapped_column(String(500))

    # Imágenes
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    images: Mapped[Optional[dict]] = mapped_column(JSON)

    # Metadata adicional
    brand: Mapped[Optional[str]] = mapped_column(String(100))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    year_start: Mapped[Optional[int]] = mapped_column(Integer)
    year_end: Mapped[Optional[int]] = mapped_column(Integer)

    # Datos adicionales flexibles
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relaciones
    importer: Mapped["Importer"] = relationship("Importer", back_populates="products")
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")


class ImportJob(Base):
    """Modelo de trabajos de importación"""
    __tablename__ = "import_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    importer_id: Mapped[int] = mapped_column(Integer, ForeignKey("importers.id"), nullable=False)

    # Tipo y estado
    job_type: Mapped[str] = mapped_column(SQLEnum(JobType), nullable=False)
    status: Mapped[str] = mapped_column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)

    # Parámetros del job
    params: Mapped[Optional[dict]] = mapped_column(JSON)

    # Progreso
    progress: Mapped[int] = mapped_column(Integer, default=0)
    total_items: Mapped[Optional[int]] = mapped_column(Integer)
    processed_items: Mapped[int] = mapped_column(Integer, default=0)

    # Resultados
    result: Mapped[Optional[dict]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relaciones
    importer: Mapped["Importer"] = relationship("Importer", back_populates="jobs")
    logs: Mapped[List["JobLog"]] = relationship("JobLog", back_populates="job", cascade="all, delete-orphan")


class JobLog(Base):
    """Logs de los trabajos de importación"""
    __tablename__ = "job_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("import_jobs.id"), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    job: Mapped["ImportJob"] = relationship("ImportJob", back_populates="logs")


class ImporterConfig(Base):
    """Configuración de cada importador"""
    __tablename__ = "importer_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    importer_id: Mapped[int] = mapped_column(Integer, ForeignKey("importers.id"), unique=True, nullable=False)

    # Credenciales de acceso (encriptadas en producción)
    credentials: Mapped[Optional[dict]] = mapped_column(JSON)  # {rut, username, password}
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Configuración de scraping
    products_per_category: Mapped[int] = mapped_column(Integer, default=100)
    scraping_speed_ms: Mapped[int] = mapped_column(Integer, default=1000)
    category_order: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Configuración adicional
    extra_config: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    importer: Mapped["Importer"] = relationship("Importer", back_populates="config")
