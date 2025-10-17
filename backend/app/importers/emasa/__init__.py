"""
Importador EMASA
Scraper para https://ecommerce.emasa.cl/b2b/

Este módulo contiene todos los componentes necesarios para importar
categorías y productos desde el sitio de EMASA.
Sistema B2B idéntico a Noriega.

Componentes disponibles:
- EmasaAuthComponent: Autenticación en el sitio
- EmasaCategoriesComponent: Extracción de categorías
- EmasaProductsComponent: Extracción de productos
"""

from app.importers.emasa.auth import EmasaAuthComponent
from app.importers.emasa.categories import EmasaCategoriesComponent
from app.importers.emasa.products import EmasaProductsComponent

__all__ = [
    "EmasaAuthComponent",
    "EmasaCategoriesComponent",
    "EmasaProductsComponent",
]
