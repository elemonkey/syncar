"""
Endpoints de desarrollo para scraping con navegador visible

Estos endpoints ejecutan las importaciones de forma síncrona (bloqueante)
con el navegador visible para facilitar el desarrollo y debugging.

⚠️ NO USAR EN PRODUCCIÓN - Solo para desarrollo
"""

import uuid
from typing import List

from app.core.database import get_db
from app.core.logger import logger
from app.importers.emasa import EmasaAuthComponent, EmasaCategoriesComponent
from app.importers.noriega import NoriegaAuthComponent, NoriegaCategoriesComponent
from app.models import Importer, ImporterType, ImportJob, JobStatus, JobType
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from playwright.async_api import async_playwright
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

router = APIRouter()


class ImportProductsRequest(BaseModel):
    """Schema para la request de importación de productos"""

    selected_categories: List[str]


@router.post("/{importer_name}/import-categories")
async def dev_import_categories(importer_name: str, db: AsyncSession = Depends(get_db)):
    """
    🔧 MODO DESARROLLO: Importa categorías con navegador visible

    Este endpoint ejecuta el scraping de forma síncrona (bloqueante) con el
    navegador visible para que puedas ver qué está haciendo en tiempo real.

    ⚠️ Solo para desarrollo - El navegador se mantiene abierto 120 segundos
    """
    job_id = str(uuid.uuid4())

    logger.info(
        f"🔧 DEV MODE: Iniciando importación de categorías: {importer_name} | Job ID: {job_id}"
    )

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
                status_code=404, detail=f"Importador '{importer_name}' no encontrado"
            )

        if not importer.config:
            raise HTTPException(
                status_code=404,
                detail=f"Configuración no encontrada para '{importer_name}'",
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
            status=JobStatus.RUNNING,
        )
        db.add(job)
        await db.commit()

        # Ejecutar scraping con navegador VISIBLE
        async with async_playwright() as p:
            logger.info("🌐 Lanzando Safari (WebKit) en modo visible...")
            # 🍎 Usar WebKit (Safari) que funciona mejor en macOS
            browser = await p.webkit.launch(
                headless=False,  # ✅ Navegador visible
                slow_mo=1000,  # Ralentizar 1 segundo entre acciones
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
                        headless=False,
                    )
                    auth_result = await auth_component.execute()

                    page = auth_result.get("page")
                    context = auth_result.get("context")

                    if not auth_result["success"]:
                        logger.error("❌ Autenticación fallida")
                        job.status = JobStatus.FAILED
                        job.result = {
                            "success": False,
                            "message": auth_result.get("message", ""),
                            "error": auth_result.get("error"),
                        }
                        await db.commit()

                        # Mantener navegador abierto para inspección
                        logger.info(
                            "🔍 Navegador abierto por 120 segundos para inspección..."
                        )
                        import asyncio

                        await asyncio.sleep(120)

                        return {
                            "success": False,
                            "job_id": job_id,
                            "error": auth_result.get("error"),
                            "message": "Revisa el navegador que se abrió para ver qué salió mal",
                        }

                    # Paso 2: Extracción de categorías
                    logger.info("📋 Extrayendo categorías...")
                    categories_component = NoriegaCategoriesComponent(
                        importer_name=importer_name,
                        job_id=job_id,
                        db=db,
                        browser=browser,
                        page=page,
                        context=context,
                    )
                    categories_result = await categories_component.execute()

                    # Actualizar job
                    job.status = (
                        JobStatus.COMPLETED
                        if categories_result["success"]
                        else JobStatus.FAILED
                    )
                    job.result = categories_result
                    job.progress = 100
                    await db.commit()

                    logger.info(f"✅ Importación completada: {job_id}")

                    # ⚠️ MANTENER NAVEGADOR ABIERTO INDEFINIDAMENTE PARA DESARROLLO
                    logger.info("=" * 80)
                    logger.info("🔧 MODO DESARROLLO - NAVEGADOR PERMANECERÁ ABIERTO")
                    logger.info("=" * 80)
                    logger.info("")
                    logger.info(
                        f"✅ {categories_result.get('saved', 0)} categorías importadas"
                    )
                    logger.info("🏠 Navegador en la página de categorías")
                    logger.info("")
                    logger.info("📋 AHORA PUEDES:")
                    logger.info("   1. Inspeccionar las categorías en el navegador")
                    logger.info("   2. Verificar la estructura de las tablas")
                    logger.info("   3. Navegar a una categoría de prueba")
                    logger.info("   4. Desarrollar selectores si es necesario")
                    logger.info("")
                    logger.info("⏸️  El navegador NO se cerrará automáticamente")
                    logger.info("🛑 Presiona Ctrl+C en esta terminal cuando termines")
                    logger.info("")
                    logger.info("=" * 80)

                    # Esperar indefinidamente hasta Ctrl+C
                    import asyncio

                    try:
                        logger.info("⏳ Esperando... (Ctrl+C para cerrar)")
                        while True:
                            await asyncio.sleep(3600)  # Esperar 1 hora, repetir
                    except KeyboardInterrupt:
                        logger.info("\n⚠️  Ctrl+C detectado - Cerrando navegador...")

                    return {
                        "success": True,
                        "job_id": job_id,
                        "categories": categories_result.get("categories", []),
                        "total": categories_result.get("total", 0),
                        "saved": categories_result.get("saved", 0),
                        "message": "Importación completada exitosamente.",
                    }

                elif importer_name.upper() == "EMASA":
                    logger.info("🔧 Ejecutando componente de EMASA")

                    # Paso 1: Autenticación
                    auth_component = EmasaAuthComponent(
                        importer_name=importer_name,
                        job_id=job_id,
                        db=db,
                        browser=browser,
                        credentials=credentials,
                        headless=False,
                    )
                    auth_result = await auth_component.execute()

                    page = auth_result.get("page")
                    context = auth_result.get("context")

                    if not auth_result["success"]:
                        logger.error("❌ Autenticación fallida")
                        job.status = JobStatus.FAILED
                        job.result = {
                            "success": False,
                            "message": auth_result.get("message", ""),
                            "error": auth_result.get("error"),
                        }
                        await db.commit()

                        # Mantener navegador abierto para inspección
                        logger.info(
                            "🔍 Navegador abierto por 120 segundos para inspección..."
                        )
                        import asyncio

                        await asyncio.sleep(120)

                        return {
                            "success": False,
                            "job_id": job_id,
                            "error": auth_result.get("error"),
                            "message": "Revisa el navegador que se abrió para ver qué salió mal",
                        }

                    # Paso 2: Extracción de categorías
                    logger.info("📋 Extrayendo categorías...")
                    categories_component = EmasaCategoriesComponent(
                        importer_name=importer_name,
                        job_id=job_id,
                        db=db,
                        browser=browser,
                        page=page,
                        context=context,
                    )
                    categories_result = await categories_component.execute()

                    # Actualizar job
                    job.status = (
                        JobStatus.COMPLETED
                        if categories_result["success"]
                        else JobStatus.FAILED
                    )
                    job.result = categories_result
                    job.progress = 100
                    await db.commit()

                    logger.info(f"✅ Importación completada: {job_id}")

                    # Mantener navegador abierto brevemente para inspección
                    logger.info("=" * 80)
                    logger.info("🔧 MODO DESARROLLO - Navegador abierto por 3 segundos")
                    logger.info("=" * 80)
                    logger.info("")
                    logger.info(
                        f"✅ {categories_result.get('total', 0)} categorías encontradas"
                    )
                    logger.info("🏠 Navegador en la página de categorías")
                    logger.info("")
                    logger.info("⏳ Esperando 3 segundos antes de cerrar...")
                    logger.info("=" * 80)

                    # Esperar brevemente para poder inspeccionar
                    import asyncio
                    await asyncio.sleep(3)

                    logger.info("✅ Proceso completado, cerrando navegador...")

                    return {
                        "success": True,
                        "job_id": job_id,
                        "categories": categories_result.get("categories", []),
                        "total": categories_result.get("total", 0),
                        "saved": categories_result.get("total", 0),
                        "message": "Importación completada exitosamente.",
                    }

                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Modo desarrollo no implementado para '{importer_name}' aún",
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


async def _execute_dev_import_products(
    job_id: str,
    importer_name: str,
    selected_categories: List[str],
    credentials: dict,
    config: dict,
    importer_id: int,
):
    """
    Función auxiliar que ejecuta la importación de productos en background
    """
    from app.importers.noriega import NoriegaAuthComponent, NoriegaProductsComponent

    # Crear nueva sesión de DB para este task
    async for db in get_db():
        try:
            # Obtener el job
            result = await db.execute(
                select(ImportJob).where(ImportJob.job_id == job_id)
            )
            job = result.scalar_one_or_none()

            if not job:
                logger.error(f"Job {job_id} no encontrado")
                return

            # Actualizar a RUNNING
            job.status = JobStatus.RUNNING
            await db.commit()

            # Ejecutar scraping con navegador VISIBLE
            async with async_playwright() as p:
                logger.info("🌐 Lanzando Safari (WebKit) en modo visible...")
                browser = await p.webkit.launch(
                    headless=False,
                    slow_mo=500,
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
                            headless=False,
                        )
                        auth_result = await auth_component.execute()

                        page = auth_result.get("page")
                        context = auth_result.get("context")

                        if not auth_result["success"]:
                            logger.error("❌ Autenticación fallida")
                            job.status = JobStatus.FAILED
                            job.result = {
                                "success": False,
                                "message": auth_result.get("message", ""),
                                "error": auth_result.get("error"),
                            }
                            await db.commit()
                            return

                        logger.info(
                            "✅ Autenticación exitosa, iniciando extracción de productos..."
                        )

                        # Paso 2: Extracción de productos
                        products_component = NoriegaProductsComponent(
                            importer_name=importer_name,
                            job_id=job_id,
                            db=db,
                            browser=browser,
                            page=page,
                            context=context,
                            selected_categories=selected_categories,
                            config=config,
                        )
                        products_result = await products_component.execute()

                        # Actualizar job
                        job.status = (
                            JobStatus.COMPLETED
                            if products_result["success"]
                            else JobStatus.FAILED
                        )
                        job.result = products_result
                        job.progress = 100
                        await db.commit()

                        logger.info(f"✅ Importación de productos completada: {job_id}")

                        # Mantener navegador abierto brevemente para inspección
                        logger.info("=" * 80)
                        logger.info("🔧 MODO DESARROLLO - Navegador abierto por 3 segundos")
                        logger.info("=" * 80)
                        logger.info("⏳ Esperando 3 segundos antes de cerrar...")
                        logger.info("=" * 80)

                        # Esperar brevemente para poder inspeccionar
                        import asyncio
                        await asyncio.sleep(3)

                        logger.info("✅ Proceso completado, cerrando navegador...")

                except Exception as e:
                    logger.error(f"❌ Error en scraping: {e}")
                    import traceback

                    logger.error(traceback.format_exc())

                    job.status = JobStatus.FAILED
                    job.error_message = str(e)
                    await db.commit()

                finally:
                    logger.info("🔒 Cerrando navegador...")

        except Exception as e:
            logger.error(f"❌ Error en background task: {e}")
        finally:
            break  # Solo queremos una iteración del async for


@router.post("/{importer_name}/import-products")
async def dev_import_products(
    importer_name: str,
    request: ImportProductsRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    🔧 MODO DESARROLLO: Importa productos con navegador visible

    Este endpoint inicia la importación en background y retorna el job_id
    inmediatamente para que el frontend pueda hacer polling del progreso.
    """
    job_id = str(uuid.uuid4())
    selected_categories = request.selected_categories

    logger.info(
        f"🔧 DEV MODE: Iniciando importación de productos: {importer_name} | Job ID: {job_id}"
    )
    logger.info(f"📋 Categorías seleccionadas: {selected_categories}")

    # Obtener importador y configuración
    result = await db.execute(
        select(Importer)
        .options(joinedload(Importer.config))
        .where(Importer.name == importer_name.upper())
    )
    importer = result.unique().scalar_one_or_none()

    if not importer:
        raise HTTPException(
            status_code=404, detail=f"Importador '{importer_name}' no encontrado"
        )

    if not importer.config:
        raise HTTPException(
            status_code=404,
            detail=f"Configuración no encontrada para '{importer_name}'",
        )

    credentials = importer.config.credentials or {}

    # Preparar configuración
    config = {
        "products_per_category": importer.config.products_per_category,
        "scraping_speed_ms": importer.config.scraping_speed_ms,
    }

    logger.info(f"⚙️ Configuración:")
    if config["products_per_category"]:
        logger.info(f"   - Límite: {config['products_per_category']}")
    else:
        logger.info(f"   - Límite: SIN LÍMITE")
    logger.info(f"   - Delay: {config['scraping_speed_ms']}ms")

    # Crear job en la base de datos
    job = ImportJob(
        job_id=job_id,
        importer_id=importer.id,
        job_type=JobType.PRODUCTS,
        status=JobStatus.PENDING,
    )
    db.add(job)
    await db.commit()

    # Ejecutar en background
    background_tasks.add_task(
        _execute_dev_import_products,
        job_id,
        importer_name,
        selected_categories,
        credentials,
        config,
        importer.id,
    )

    # Retornar inmediatamente el job_id
    return {
        "success": True,
        "job_id": job_id,
        "message": "Importación iniciada. El navegador se abrirá automáticamente.",
    }


@router.get("/status/{job_id}")
async def get_dev_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Obtiene el estado de un job de desarrollo
    """
    result = await db.execute(select(ImportJob).where(ImportJob.job_id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")

    # Extraer información adicional del result si existe
    total_items = 0
    processed_items = 0
    current_item = 0

    if job.result and isinstance(job.result, dict):
        total_items = job.result.get("total_items", 0)
        processed_items = job.result.get("processed_items", 0)
        current_item = job.result.get("current_item", 0)

    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "result": job.result,
        "error": job.error_message,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "total_items": total_items,
        "processed_items": processed_items,
        "current_item": current_item,
    }
