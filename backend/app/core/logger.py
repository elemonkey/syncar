"""
Logger configurado con loguru
"""
import sys
from loguru import logger
from .config import settings


# Configuración del logger
logger.remove()  # Remover handler por defecto

# Formato del log
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Handler para consola
logger.add(
    sys.stdout,
    format=log_format,
    level=settings.LOG_LEVEL,
    colorize=True,
)

# Handler para archivo (opcional)
if settings.is_production:
    logger.add(
        "logs/app.log",
        format=log_format,
        level=settings.LOG_LEVEL,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
    )


def get_logger(name: str):
    """Obtiene un logger con un nombre específico"""
    return logger.bind(name=name)


# Exportar logger configurado
__all__ = ["logger", "get_logger"]
