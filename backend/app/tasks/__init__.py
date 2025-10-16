"""
Módulo de tareas de Celery
"""
from .celery_app import celery_app
from .import_tasks import import_categories_task, import_products_task

__all__ = [
    'celery_app',
    'import_categories_task',
    'import_products_task',
]
