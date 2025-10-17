"""
Script para inicializar datos básicos en la base de datos
Crea los importadores predefinidos
"""

import asyncio

from app.core.database import async_session
from app.core.logger import logger
from app.models import Importer, ImporterConfig
from sqlalchemy import select


async def seed_importers():
    """Crear importadores básicos si no existen"""
    async with async_session() as session:
        # Verificar si ya existen importadores
        result = await session.execute(select(Importer))
        existing = result.scalars().all()

        if existing:
            logger.info(f"✅ Ya existen {len(existing)} importadores")
            for imp in existing:
                logger.info(f"  - {imp.name} ({imp.code})")
            return

        # Crear importadores predefinidos
        importers_data = [
            {
                "code": "noriega",
                "name": "Noriega",
                "description": "Importador de productos desde Noriega",
                "is_active": True,
            },
            {
                "code": "alsacia",
                "name": "Alsacia",
                "description": "Importador de productos desde Alsacia",
                "is_active": False,
            },
            {
                "code": "emasa",
                "name": "Emasa",
                "description": "Importador de productos desde Emasa",
                "is_active": False,
            },
            {
                "code": "refax",
                "name": "Refax",
                "description": "Importador de productos desde Refax",
                "is_active": False,
            },
        ]

        logger.info("🌱 Creando importadores...")

        for data in importers_data:
            importer = Importer(**data)
            session.add(importer)
            logger.info(f"  ✓ Creado: {data['name']}")

        await session.commit()
        logger.info("✅ Importadores creados exitosamente")


async def seed_importer_configs():
    """Crear configuraciones iniciales para los importadores"""
    async with async_session() as session:
        # Verificar si ya existen configuraciones
        result = await session.execute(select(ImporterConfig))
        existing = result.scalars().all()

        if existing:
            logger.info(f"✅ Ya existen {len(existing)} configuraciones")
            return

        # Obtener importador de Noriega
        result = await session.execute(
            select(Importer).where(Importer.code == "noriega")
        )
        noriega = result.scalar_one_or_none()

        if not noriega:
            logger.error("❌ No se encontró el importador de Noriega")
            return

        # Crear configuración por defecto para Noriega
        config = ImporterConfig(
            importer_id=noriega.id,
            credentials={},  # Se configurarán desde el frontend
            is_active=True,
        )

        session.add(config)
        await session.commit()

        logger.info("✅ Configuración de Noriega creada")


async def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("🌱 Inicializando datos de la base de datos")
    logger.info("=" * 60)

    try:
        await seed_importers()
        await seed_importer_configs()

        logger.info("=" * 60)
        logger.info("✅ Inicialización completada exitosamente")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Error durante la inicialización: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
