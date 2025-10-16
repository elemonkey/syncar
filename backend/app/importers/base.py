"""
Componentes base para importación modular
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from playwright.async_api import Page, BrowserContext, async_playwright, Browser
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.logger import logger
from app.models import ImportJob, JobLog, JobStatus
from sqlalchemy import select, update


class ImporterComponentBase(ABC):
    """
    Clase base para todos los componentes de importación
    
    Cada componente representa una fase del proceso de importación:
    - AuthComponent: Autenticación
    - CategoriesComponent: Extracción de categorías
    - ConfigComponent: Carga de configuración
    - ProductsComponent: Extracción de productos
    """
    
    def __init__(
        self,
        importer_name: str,
        job_id: str,
        db: AsyncSession,
        browser: Optional[Browser] = None
    ):
        self.importer_name = importer_name
        self.job_id = job_id
        self.db = db
        self.browser = browser
        self.page: Optional[Page] = None
        self.context: Optional[BrowserContext] = None
        self.logger = logger.bind(
            importer=importer_name,
            job_id=job_id,
            component=self.__class__.__name__
        )
    
    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """
        Ejecuta la lógica del componente
        
        Returns:
            Dict con el resultado de la ejecución
        """
        pass
    
    async def update_progress(self, message: str, progress: int, level: str = "INFO"):
        """
        Actualiza el progreso del job en la base de datos
        
        Args:
            message: Mensaje descriptivo del progreso
            progress: Porcentaje de progreso (0-100)
            level: Nivel del log (INFO, WARNING, ERROR)
        """
        try:
            # Actualizar job
            stmt = (
                update(ImportJob)
                .where(ImportJob.job_id == self.job_id)
                .values(progress=progress)
            )
            await self.db.execute(stmt)
            
            # Crear log
            job_result = await self.db.execute(
                select(ImportJob).where(ImportJob.job_id == self.job_id)
            )
            job = job_result.scalar_one_or_none()
            
            if job:
                log_entry = JobLog(
                    job_id=job.id,
                    level=level,
                    message=message
                )
                self.db.add(log_entry)
            
            await self.db.commit()
            
            # Log a consola
            self.logger.info(f"[{progress}%] {message}")
            
        except Exception as e:
            self.logger.error(f"Error updating progress: {e}")
    
    async def mark_job_status(self, status: JobStatus, error_message: Optional[str] = None):
        """Marca el estado del job"""
        try:
            values = {"status": status}
            
            if status == JobStatus.RUNNING:
                values["started_at"] = datetime.utcnow()
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                values["completed_at"] = datetime.utcnow()
            
            if error_message:
                values["error_message"] = error_message
            
            stmt = (
                update(ImportJob)
                .where(ImportJob.job_id == self.job_id)
                .values(**values)
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
        except Exception as e:
            self.logger.error(f"Error marking job status: {e}")


class AuthComponent(ImporterComponentBase):
    """
    Componente de autenticación
    
    Responsabilidad:
    - Login en el sitio del proveedor
    - Guardar session/cookies
    - Dejar la página lista en inicio/dashboard
    """
    
    async def execute(self) -> Dict[str, Any]:
        """
        Ejecuta el proceso de autenticación
        
        Returns:
            {
                'success': bool,
                'session_data': dict,  # cookies, localStorage, etc
                'message': str
            }
        """
        await self.update_progress("🔐 Iniciando autenticación...", 5)
        
        # AQUÍ irá tu lógica específica de autenticación
        # Por ahora es un placeholder
        
        await self.update_progress("✅ Autenticación exitosa", 15)
        
        return {
            'success': True,
            'session_data': {},
            'message': 'Autenticación exitosa'
        }


class CategoriesComponent(ImporterComponentBase):
    """
    Componente de extracción de categorías
    
    Responsabilidad:
    - Navegar a URL de categorías
    - Extraer datos de categorías
    - Almacenar en base de datos
    """
    
    def __init__(
        self,
        importer_name: str,
        job_id: str,
        db: AsyncSession,
        session_data: dict,
        browser: Optional[Browser] = None
    ):
        super().__init__(importer_name, job_id, db, browser)
        self.session_data = session_data
    
    async def execute(self) -> Dict[str, Any]:
        """
        Ejecuta la extracción de categorías
        
        Returns:
            {
                'success': bool,
                'categories': List[dict],
                'count': int
            }
        """
        await self.update_progress("📂 Navegando a página de categorías...", 20)
        
        # AQUÍ irá tu lógica de scraping de categorías
        # Por ahora es un placeholder
        
        categories = []
        
        await self.update_progress("💾 Guardando categorías en base de datos...", 80)
        
        await self.update_progress(f"✅ {len(categories)} categorías importadas", 100)
        
        return {
            'success': True,
            'categories': categories,
            'count': len(categories)
        }


class ConfigComponent(ImporterComponentBase):
    """
    Componente de carga de configuración
    
    Responsabilidad:
    - Leer configuración del importador desde DB
    - Aplicar configuración (límites, velocidad, orden)
    """
    
    async def execute(self) -> Dict[str, Any]:
        """
        Lee la configuración del importador
        
        Returns:
            {
                'products_per_category': int,
                'category_order': List[str],
                'scraping_speed_ms': int
            }
        """
        await self.update_progress("⚙️ Cargando configuración del importador...", 10)
        
        # AQUÍ leerás de la DB la configuración
        # Por ahora valores por defecto
        
        config = {
            'products_per_category': 100,
            'category_order': [],
            'scraping_speed_ms': 1000
        }
        
        await self.update_progress("✅ Configuración cargada", 15)
        
        return config


class ProductsComponent(ImporterComponentBase):
    """
    Componente de extracción de productos
    
    Responsabilidad:
    - Para cada categoría seleccionada:
      * Construir URLs de productos
      * Navegar a cada URL individual
      * Extraer información del producto
      * Almacenar en base de datos
      * Respetar límites y velocidad de configuración
    """
    
    def __init__(
        self,
        importer_name: str,
        job_id: str,
        db: AsyncSession,
        session_data: dict,
        selected_categories: List[str],
        config: dict,
        browser: Optional[Browser] = None
    ):
        super().__init__(importer_name, job_id, db, browser)
        self.session_data = session_data
        self.selected_categories = selected_categories
        self.config = config
    
    async def execute(self) -> Dict[str, Any]:
        """
        Ejecuta la extracción de productos
        
        Returns:
            {
                'success': bool,
                'products_count': int,
                'categories_processed': int
            }
        """
        await self.update_progress("🛍️ Iniciando importación de productos...", 20)
        
        total_products = 0
        
        for i, category in enumerate(self.selected_categories):
            progress = 20 + int((i / len(self.selected_categories)) * 70)
            await self.update_progress(f"📦 Procesando categoría: {category}", progress)
            
            # AQUÍ irá tu lógica de scraping de productos
            # 1. Construir URLs de productos de esta categoría
            # 2. Iterar por cada URL
            # 3. Extraer datos
            # 4. Guardar en DB
            # 5. Aplicar delay según config['scraping_speed_ms']
            
        await self.update_progress(f"✅ {total_products} productos importados", 100)
        
        return {
            'success': True,
            'products_count': total_products,
            'categories_processed': len(self.selected_categories)
        }
