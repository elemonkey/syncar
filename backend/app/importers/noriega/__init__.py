"""
Importador Noriega
Scraper para https://ecommerce.noriegavanzulli.cl

Este módulo contiene todos los componentes necesarios para importar
categorías y productos desde el sitio de Noriega.

Componentes disponibles:
- NoriegaAuthComponent: Autenticación en el sitio
- NoriegaCategoriesComponent: Extracción de categorías
- NoriegaProductsComponent: Extracción de productos
"""

from app.importers.noriega.auth import NoriegaAuthComponent
from app.importers.noriega.categories import NoriegaCategoriesComponent
from app.importers.noriega.products import NoriegaProductsComponent

__all__ = [
    "NoriegaAuthComponent",
    "NoriegaCategoriesComponent",
    "NoriegaProductsComponent",
]
