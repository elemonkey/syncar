"""
Endpoints de desarrollo para scraping con navegador visible

Estos endpoints ejecutan las importaciones de forma síncrona (bloqueante)
con el navegador visible para facilitar el desarrollo y debugging.

⚠️ NO USAR EN PRODUCCIÓN - Solo para desarrollo
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from playwright.async_api import async_playwright
import uuid

from app.core.database import get_db
from app.core.logger import logger
from app.models import Importer, ImporterType, ImportJob, JobStatus, JobType
from app.importers.noriega import NoriegaAuthComponent, NoriegaCategoriesComponent

router = APIRouter()


@router.post("/{importer_name}/import-categories")
async def dev_import_categories(
    importer_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    🔧 MODO DESARROLLO: Importa categorías con navegador visible

    Este endpoint ejecuta el scraping de forma síncrona (bloqueante) con el
    navegador visible para que puedas ver qué está haciendo en tiempo real.

    ⚠️ Solo para desarrollo - El navegador se mantiene abierto 120 segundos
    """
    job_id = str(uuid.uuid4())

    logger.info(f"🔧 DEV MODE: Iniciando importación de categorías: {importer_name} | Job ID: {job_id}")

    try:
        # Obtener importador y credenciales
        result = await db.execute(
            select(Importer)
            .options(joinedload(Importer.config))
            .where(Importer.name == importer_name.upper())
        )
        importer = result.unique().scalar_one_or_none()

        if not importer:
            raise HTTPException(
                status_code=404,
                detail=f"Importador '{importer_name}' no encontrado"
            )

        if not importer.config:
            raise HTTPException(
                status_code=404,
                detail=f"Configuración no encontrada para '{importer_name}'"
            )

        credentials = importer.config.credentials or {}

        logger.info(f"📋 Credenciales cargadas desde BDD:")
        logger.info(f"   - RUT: {credentials.get('rut', 'N/A')}")
        logger.info(f"   - Usuario: {credentials.get('username', 'N/A')}")
        logger.info(f"   - Password: {'*' * len(credentials.get('password', ''))}")

        # Crear job en la base de datos
        job = ImportJob(
            job_id=job_id,
            importer_id=importer.id,
            job_type=JobType.CATEGORIES,
            status=JobStatus.RUNNING
        )
        db.add(job)
        await db.commit()

        # Ejecutar scraping con navegador VISIBLE
        async with async_playwright() as p:
            logger.info("🌐 Lanzando Safari (WebKit) en modo visible...")
            # 🍎 Usar WebKit (Safari) que funciona mejor en macOS
            browser = await p.webkit.launch(
                headless=False,  # ✅ Navegador visible
                slow_mo=1000     # Ralentizar 1 segundo entre acciones
            )

            page = None
            context = None

            try:
                if importer_name.upper() == "NORIEGA":
                    logger.info("🔧 Ejecutando componente de Noriega")

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

                    page = auth_result.get('page')
                    context = auth_result.get('context')

                    if not auth_result['success']:
                        logger.error("❌ Autenticación fallida")
                        job.status = JobStatus.FAILED
                        job.result = {
                            'success': False,
                            'message': auth_result.get('message', ''),
                            'error': auth_result.get('error')
                        }
                        await db.commit()

                        # Mantener navegador abierto para inspección
                        logger.info("🔍 Navegador abierto por 120 segundos para inspección...")
                        import asyncio
                        await asyncio.sleep(120)

                        return {
                            "success": False,
                            "job_id": job_id,
                            "error": auth_result.get('error'),
                            "message": "Revisa el navegador que se abrió para ver qué salió mal"
                        }

                    # Paso 2: Extracción de categorías
                    logger.info("📋 Extrayendo categorías...")
                    categories_component = NoriegaCategoriesComponent(
                        importer_name=importer_name,
                        job_id=job_id,
                        db=db,
                        browser=browser,
                        page=page,
                        context=context
                    )
                    categories_result = await categories_component.execute()

                    # Actualizar job
                    job.status = JobStatus.COMPLETED if categories_result['success'] else JobStatus.FAILED
                    job.result = categories_result
                    job.progress = 100
                    await db.commit()

                    logger.info(f"✅ Importación completada: {job_id}")

                    # Mantener navegador abierto brevemente para inspección
                    logger.info("🔍 Navegador permanecerá abierto por 10 segundos...")
                    import asyncio
                    await asyncio.sleep(10)

                    return {
                        "success": True,
                        "job_id": job_id,
                        "categories": categories_result.get('categories', []),
                        "total": categories_result.get('total', 0),
                        "saved": categories_result.get('saved', 0),
                        "message": "Importación completada exitosamente."
                    }

                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Modo desarrollo no implementado para '{importer_name}' aún"
                    )

            except Exception as e:
                logger.error(f"❌ Error en scraping: {e}")
                import traceback
                logger.error(traceback.format_exc())

                job.status = JobStatus.FAILED
                job.error_message = str(e)
                await db.commit()

                # Mantener navegador abierto brevemente para debug
                logger.info("🔍 Navegador abierto por 15 segundos para debug...")
                import asyncio
                await asyncio.sleep(15)

                raise HTTPException(status_code=500, detail=str(e))

            finally:
                # El navegador se cerrará automáticamente al salir del context manager
                logger.info("🔒 Cerrando navegador...")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}")
async def get_dev_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el estado de un job de desarrollo
    """
    result = await db.execute(
        select(ImportJob).where(ImportJob.job_id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")

    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "result": job.result,
        "error": job.error_message,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }
