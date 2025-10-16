"""
Orquestador de componentes de importación
"""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from playwright.async_api import Browser

from .base import (
    AuthComponent,
    CategoriesComponent,
    ConfigComponent,
    ProductsComponent
)
from app.core.logger import logger


class ImportOrchestrator:
    """
    Orquesta la ejecución de componentes en orden correcto
    
    Flujos:
    1. Importación de categorías: Auth -> Categories
    2. Importación de productos: Auth -> Config -> Products
    """
    
    def __init__(
        self,
        importer_name: str,
        job_id: str,
        db: AsyncSession,
        browser: Browser
    ):
        self.importer_name = importer_name
        self.job_id = job_id
        self.db = db
        self.browser = browser
        self.logger = logger.bind(importer=importer_name, job_id=job_id)
    
    async def import_categories(self) -> Dict[str, Any]:
        """
        Flujo completo de importación de categorías
        
        Pasos:
        1. Autenticación
        2. Extracción de categorías
        
        Returns:
            Resultado de la importación
        """
        try:
            self.logger.info(f"🚀 Iniciando importación de categorías para {self.importer_name}")
            
            # Paso 1: Autenticación
            self.logger.info("Paso 1/2: Autenticación")
            auth_component = AuthComponent(
                self.importer_name,
                self.job_id,
                self.db,
                self.browser
            )
            auth_result = await auth_component.execute()
            
            if not auth_result['success']:
                self.logger.error("❌ Autenticación fallida")
                return {
                    'success': False,
                    'error': 'Authentication failed',
                    'details': auth_result
                }
            
            # Paso 2: Extracción de categorías
            self.logger.info("Paso 2/2: Extracción de categorías")
            categories_component = CategoriesComponent(
                self.importer_name,
                self.job_id,
                self.db,
                auth_result['session_data'],
                self.browser
            )
            categories_result = await categories_component.execute()
            
            self.logger.info(f"✅ Importación de categorías completada: {categories_result['count']} categorías")
            
            return categories_result
            
        except Exception as e:
            self.logger.error(f"❌ Error en importación de categorías: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def import_products(self, selected_categories: List[str]) -> Dict[str, Any]:
        """
        Flujo completo de importación de productos
        
        Pasos:
        1. Autenticación
        2. Carga de configuración
        3. Extracción de productos
        
        Args:
            selected_categories: Lista de nombres de categorías a importar
        
        Returns:
            Resultado de la importación
        """
        try:
            self.logger.info(f"🚀 Iniciando importación de productos para {self.importer_name}")
            self.logger.info(f"Categorías seleccionadas: {selected_categories}")
            
            # Paso 1: Autenticación
            self.logger.info("Paso 1/3: Autenticación")
            auth_component = AuthComponent(
                self.importer_name,
                self.job_id,
                self.db,
                self.browser
            )
            auth_result = await auth_component.execute()
            
            if not auth_result['success']:
                self.logger.error("❌ Autenticación fallida")
                return {
                    'success': False,
                    'error': 'Authentication failed',
                    'details': auth_result
                }
            
            # Paso 2: Carga de configuración
            self.logger.info("Paso 2/3: Carga de configuración")
            config_component = ConfigComponent(
                self.importer_name,
                self.job_id,
                self.db,
                self.browser
            )
            config = await config_component.execute()
            
            # Paso 3: Extracción de productos
            self.logger.info("Paso 3/3: Extracción de productos")
            products_component = ProductsComponent(
                self.importer_name,
                self.job_id,
                self.db,
                auth_result['session_data'],
                selected_categories,
                config,
                self.browser
            )
            products_result = await products_component.execute()
            
            self.logger.info(f"✅ Importación de productos completada: {products_result['products_count']} productos")
            
            return products_result
            
        except Exception as e:
            self.logger.error(f"❌ Error en importación de productos: {e}")
            return {
                'success': False,
                'error': str(e)
            }
