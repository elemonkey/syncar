"""
Configuración de Uvicorn para desarrollo
"""

# Configuración de servidor
bind = "0.0.0.0:8000"
workers = 1  # En desarrollo, solo 1 worker
worker_class = "uvicorn.workers.UvicornWorker"

# Reload
reload = True
reload_delay = 0.5
reload_excludes = [
    "app/tasks/*",
    "app/importers/*",
    "*.pyc",
    "__pycache__/*",
    "*.log",
    "*.tmp",
]

# Timeouts
timeout = 30
graceful_timeout = 3  # Timeout para shutdown graceful

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Keep alive
keepalive = 5
