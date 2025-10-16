"""
Configuración de Celery
"""
from celery import Celery
from app.core.config import settings

# Crear instancia de Celery
celery_app = Celery(
    "importapp",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks.import_tasks']
)

# Configuración de Celery optimizada para scraping
celery_app.conf.update(
    # Serialización
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Progress tracking
    task_track_started=True,
    task_send_sent_event=True,
    
    # Límites de tiempo
    task_time_limit=3600,  # 1 hora máximo por tarea
    task_soft_time_limit=3300,  # 55 minutos soft limit
    
    # Worker config (optimizado para tareas largas de scraping)
    worker_prefetch_multiplier=1,  # No prefetch (mejor para tareas largas)
    worker_max_tasks_per_child=50,  # Restart workers periódicamente (previene memory leaks)
    
    # Reliability
    task_acks_late=True,  # Acknowledge después de completar, no al empezar
    task_reject_on_worker_lost=True,
    
    # Retry
    task_autoretry_for=(Exception,),
    task_retry_kwargs={'max_retries': 3},
    task_retry_backoff=True,
    task_retry_backoff_max=600,
    task_retry_jitter=True,
    
    # Broker
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Result backend
    result_expires=86400,  # 24 horas
    result_extended=True,
)

# Configuración de rutas de tareas
celery_app.conf.task_routes = {
    'app.tasks.import_tasks.*': {'queue': 'imports'},
}

# Beat schedule (tareas programadas - opcional)
celery_app.conf.beat_schedule = {
    # Ejemplo: importar automáticamente cada día a las 3 AM
    # 'auto-import-alsacia': {
    #     'task': 'app.tasks.import_tasks.import_products',
    #     'schedule': crontab(hour=3, minute=0),
    #     'args': ('alsacia', ['Frenos'])
    # },
}
