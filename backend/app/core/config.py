"""
Configuración central de la aplicación
"""

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

# Buscar el archivo .env en el directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Configuración de la aplicación desde variables de entorno"""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General
    APP_NAME: str = "ImportApp"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Scraping
    SCRAPING_MODE: str = "dev"  # "dev" o "prod"

    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "importapp_db"
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "password"
    DATABASE_URL: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = ""

    # JWT
    SECRET_KEY: str = "changeme-super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Celery
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    # Playwright
    PLAYWRIGHT_BROWSERS_PATH: str = "/ms-playwright"
    HEADLESS: bool = True  # True en producción (sin UI), False en desarrollo local

    # Logging
    LOG_LEVEL: str = "INFO"

    # Importadores credentials
    ALSACIA_USERNAME: str = ""
    ALSACIA_PASSWORD: str = ""
    ALSACIA_URL: str = ""

    REFAX_USERNAME: str = ""
    REFAX_PASSWORD: str = ""
    REFAX_URL: str = ""

    NORIEGA_USERNAME: str = ""
    NORIEGA_PASSWORD: str = ""
    NORIEGA_URL: str = ""

    EMASA_USERNAME: str = ""
    EMASA_PASSWORD: str = ""
    EMASA_URL: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Construir URLs si no están definidas
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        if not self.REDIS_URL:
            self.REDIS_URL = (
                f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            )

        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.REDIS_URL

        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


# Instancia global de settings
settings = Settings()
