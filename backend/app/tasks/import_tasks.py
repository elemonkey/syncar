"""
Tareas de Celery para importación
"""
import uuid
import asyncio
from typing import List
from celery import Task
from playwright.async_api import async_playwright
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.logger import logger
from app.models import ImportJob, JobStatus, JobType, Importer, ImporterConfig
from app.importers.orchestrator import ImportOrchestrator
from app.importers.noriega import NoriegaAuthComponent, NoriegaCategoriesComponent


class DatabaseTask(Task):
    """Tarea base con conexión a base de datos"""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = AsyncSessionLocal()
        return self._db


async def _run_import_categories(importer_name: str, job_id: str) -> dict:
    """Función async interna para importar categorías"""
    async with AsyncSessionLocal() as db:
        try:
            # Obtener importador y sus credenciales
            from sqlalchemy.orm import joinedload
            result = await db.execute(
                select(Importer)
                .options(joinedload(Importer.config))
                .where(Importer.name == importer_name.upper())
            )
            importer = result.unique().scalar_one_or_none()

            if not importer:
                logger.error(f"❌ Importador no encontrado: {importer_name}")
                return {'success': False, 'error': 'Importer not found'}

            if not importer.config:
                logger.error(f"❌ Configuración no encontrada para: {importer_name}")
                return {'success': False, 'error': 'Configuration not found'}

            credentials = importer.config.credentials or {}

            job = ImportJob(
                job_id=job_id,
                importer_id=importer.id,
                job_type=JobType.CATEGORIES,
                status=JobStatus.RUNNING
            )
            db.add(job)
            await db.commit()

            # Ejecutar importación con Playwright (MODO VISIBLE para desarrollo)
            async with async_playwright() as p:
                # headless=False para ver el navegador en acción
                browser = await p.chromium.launch(
                    headless=False,
                    slow_mo=500  # Ralentizar acciones para que puedas ver
                )

                page = None
                context = None

                try:
                    if importer_name.upper() == "NORIEGA":
                        # Usar componentes específicos de Noriega
                        logger.info("🔧 Usando componentes de Noriega")

                        # Paso 1: Autenticación
                        auth_component = NoriegaAuthComponent(
                            importer_name=importer_name,
                            job_id=job_id,
                            db=db,
                            browser=browser,
                            credentials=credentials,
                            headless=False
                        )
                        auth_result = await auth_component.execute()

                        # Guardar referencias a page y context
                        page = auth_result.get('page')
                        context = auth_result.get('context')

                        # Crear resultado sin objetos no serializables
                        clean_auth_result = {
                            'success': auth_result['success'],
                            'message': auth_result.get('message', ''),
                            'error': auth_result.get('error')
                        }

                        if not auth_result['success']:
                            logger.error("❌ Autenticación fallida")
                            job.status = JobStatus.FAILED
                            job.result = clean_auth_result
                            await db.commit()

                            # Mantener navegador abierto 60 segundos
                            import asyncio
                            logger.info("🔍 Navegador abierto por 60 segundos para inspección...")
                            await asyncio.sleep(60)

                            return clean_auth_result

                        # Paso 2: Extracción de categorías
                        categories_component = NoriegaCategoriesComponent(
                            importer_name=importer_name,
                            job_id=job_id,
                            db=db,
                            browser=browser,
                            page=page,
                            context=context
                        )
                        result = await categories_component.execute()

                    else:
                        # Usar orchestrator genérico para otros importadores
                        orchestrator = ImportOrchestrator(
                            importer_name=importer_name,
                            job_id=job_id,
                            db=db,
                            browser=browser
                        )
                        result = await orchestrator.import_categories()

                    # Actualizar job con resultado
                    job.status = JobStatus.COMPLETED if result['success'] else JobStatus.FAILED
                    job.result = result
                    job.progress = 100
                    await db.commit()

                    logger.info(f"✅ Tarea completada: {job_id}")

                    # Mantener navegador abierto por 120 segundos para inspección
                    import asyncio
                    logger.info("🔍 Navegador permanecerá abierto por 120 segundos para inspección...")
                    await asyncio.sleep(120)

                    return result

                except Exception as e:
                    logger.error(f"Error en importación: {e}")
                    import traceback
                    logger.error(traceback.format_exc())

                    if 'job' in locals():
                        job.status = JobStatus.FAILED
                        job.error_message = str(e)
                        await db.commit()

                    # Mantener navegador abierto 60 segundos en caso de error
                    import asyncio
                    logger.info("🔍 Navegador abierto por 60 segundos para inspección de error...")
                    await asyncio.sleep(60)

                    raise

        except Exception as e:
            logger.error(f"❌ Error en tarea {job_id}: {e}")

            # Marcar job como fallido si fue creado
            try:
                if 'job' in locals():
                    job.status = JobStatus.FAILED
                    job.error_message = str(e)
                    await db.commit()
            except:
                pass

            return {'success': False, 'error': str(e)}


@celery_app.task(bind=True, name="import_categories")
def import_categories_task(self, importer_name: str) -> dict:
    """
    Tarea de Celery para importar categorías

    Args:
        importer_name: Nombre del importador (alsacia, refax, etc.)

    Returns:
        Dict con el resultado de la importación
    """
    job_id = str(uuid.uuid4())
    logger.info(f"🚀 Iniciando tarea de importación de categorías: {importer_name} | Job ID: {job_id}")

    # Crear un nuevo event loop para esta tarea
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run_import_categories(importer_name, job_id))
    finally:
        loop.close()
async def _run_import_products(importer_name: str, selected_categories: List[str], job_id: str) -> dict:
    """Función async interna para importar productos"""
    logger.info(f"🚀 Iniciando tarea de importación de productos: {importer_name} | Job ID: {job_id}")
    logger.info(f"Categorías: {selected_categories}")

    async with AsyncSessionLocal() as db:
        try:
            # Crear registro del job
            result = await db.execute(
                select(Importer).where(Importer.name == importer_name)
            )
            importer = result.scalar_one_or_none()

            if not importer:
                logger.error(f"❌ Importador no encontrado: {importer_name}")
                return {'success': False, 'error': 'Importer not found'}

            job = ImportJob(
                job_id=job_id,
                importer_id=importer.id,
                job_type=JobType.PRODUCTS,
                status=JobStatus.RUNNING,
                params={'selected_categories': selected_categories}
            )
            db.add(job)
            await db.commit()

            # Ejecutar importación con Playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)

                try:
                    orchestrator = ImportOrchestrator(
                        importer_name=importer_name,
                        job_id=job_id,
                        db=db,
                        browser=browser
                    )

                    result = await orchestrator.import_products(selected_categories)

                    # Actualizar job con resultado
                    job.status = JobStatus.COMPLETED if result['success'] else JobStatus.FAILED
                    job.result = result
                    job.progress = 100
                    await db.commit()

                    logger.info(f"✅ Tarea completada: {job_id}")

                    return result

                finally:
                    await browser.close()

        except Exception as e:
            logger.error(f"❌ Error en tarea {job_id}: {e}")

            # Marcar job como fallido
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            await db.commit()

            return {'success': False, 'error': str(e)}


@celery_app.task(bind=True, name="import_products")
def import_products_task(self, importer_name: str, selected_categories: List[str]) -> dict:
    """
    Tarea de Celery para importar productos

    Args:
        importer_name: Nombre del importador
        selected_categories: Lista de categorías a importar

    Returns:
        Dict con el resultado de la importación
    """
    job_id = str(uuid.uuid4())

    # Crear un nuevo event loop para esta tarea
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_run_import_products(importer_name, selected_categories, job_id))
    finally:
        loop.close()
