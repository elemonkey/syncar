
from celery import Celery
import os

celery = Celery(
    __name__,
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0")
)

celery.conf.update(
    task_track_started=True,
)

# Importar las tareas para que Celery las registre
from . import import_tasks
