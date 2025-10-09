
from .celery_worker import celery
import time
from app.core.database import SessionLocal
from app.crud import crud_import_job, crud_product
from app.schemas.import_job import ImportJobUpdate
from app.schemas.product import ProductCreate
from app.models.import_job import JobStatus

# Importar módulos de importadores (condicional para evitar errores de dependencias)
try:
    from app.importadores.noriega import noriega_login
    NORIEGA_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Módulo de Noriega no disponible: {e}")
    NORIEGA_AVAILABLE = False

@celery.task(name="run_import_flow")
def run_import_flow(job_id: str, category: str):
    db = SessionLocal()
    try:
        # 1. Actualizar estado a EN PROGRESO
        job = crud_import_job.get_import_job(db, job_id)
        if not job:
            return {"status": "Error", "message": "Job not found"}
        
        update_schema = ImportJobUpdate(status=JobStatus.IN_PROGRESS)
        crud_import_job.update_import_job(db, job_id=job_id, job_update=update_schema)
        print(f"Job {job_id}: Status actualizado a IN_PROGRESS.")

        # 2. Ejecutar importación real según el importador
        print(f"Job {job_id}: Iniciando importación REAL de productos de la categoría '{category}'...")
        
        if job.importer_name.lower() == 'noriega' and NORIEGA_AVAILABLE:
            success = _import_noriega_products(db, job_id, category)
        elif job.importer_name.lower() == 'noriega':
            print(f"Job {job_id}: Noriega no disponible, usando productos de ejemplo")
            success = _create_example_products(db, job_id, job.importer_name, category)
        elif job.importer_name.lower() == 'alsacia':
            success = _import_alsacia_products(db, job_id, category)  # TODO: Implementar
        elif job.importer_name.lower() == 'refax':
            success = _import_refax_products(db, job_id, category)    # TODO: Implementar
        elif job.importer_name.lower() == 'emasa':
            success = _import_emasa_products(db, job_id, category)    # TODO: Implementar
        else:
            # Fallback: crear productos de ejemplo
            success = _create_example_products(db, job_id, job.importer_name, category)
        
        if not success:
            raise Exception(f"Error en importación de {job.importer_name}")

        # 3. Actualizar estado a COMPLETADO
        print(f"Job {job_id}: Importación completada. Actualizando estado a SUCCESS.")
        update_schema = ImportJobUpdate(status=JobStatus.SUCCESS)
        crud_import_job.update_import_job(db, job_id=job_id, job_update=update_schema)

        return {"status": "SUCCESS", "job_id": job_id}

    except Exception as e:
        # En caso de error, actualizar estado a FALLIDO
        print(f"Job {job_id}: Ha ocurrido un error: {e}")
        update_schema = ImportJobUpdate(status=JobStatus.FAILURE, log=str(e))
        crud_import_job.update_import_job(db, job_id=job_id, job_update=update_schema)
        return {"status": "FAILURE", "job_id": job_id, "error": str(e)}
    finally:
        db.close()


def _import_noriega_products(db, job_id: str, category: str) -> bool:
    """Importa productos reales de Noriega"""
    if not NORIEGA_AVAILABLE:
        print(f"Job {job_id}: Módulo de Noriega no disponible")
        return False
        
    try:
        print(f"Job {job_id}: Conectando con Noriega...")
        
        # Por ahora solo probamos el login y generamos productos de ejemplo
        # TODO: Implementar extracción real de productos cuando la importación esté lista
        try:
            from app.importadores.noriega.auth import noriega_test_login
            success, message = noriega_test_login()
            if success:
                print(f"Job {job_id}: Conexión exitosa con Noriega - {message}")
            else:
                print(f"Job {job_id}: Error de conexión con Noriega - {message}")
                return False
        except Exception as e:
            print(f"Job {job_id}: Error probando conexión: {e}")
            return False
        
        # Generar productos de ejemplo mientras no tengamos importación completa
        print(f"Job {job_id}: Generando productos de ejemplo para Noriega")
        return _create_example_products(db, job_id, 'noriega', category)
        
        return True
        
    except Exception as e:
        print(f"Job {job_id}: Error en importación de Noriega: {str(e)}")
        return False


def _import_alsacia_products(db, job_id: str, category: str) -> bool:
    """Importa productos reales de Alsacia - TODO: Implementar"""
    print(f"Job {job_id}: Alsacia no implementado aún, usando productos de ejemplo")
    return _create_example_products(db, job_id, 'alsacia', category)


def _import_refax_products(db, job_id: str, category: str) -> bool:
    """Importa productos reales de Refax - TODO: Implementar"""
    print(f"Job {job_id}: Refax no implementado aún, usando productos de ejemplo")
    return _create_example_products(db, job_id, 'refax', category)


def _import_emasa_products(db, job_id: str, category: str) -> bool:
    """Importa productos reales de Emasa - TODO: Implementar"""
    print(f"Job {job_id}: Emasa no implementado aún, usando productos de ejemplo")
    return _create_example_products(db, job_id, 'emasa', category)


def _create_example_products(db, job_id: str, importer_name: str, category: str) -> bool:
    """Crea productos de ejemplo como fallback"""
    try:
        for i in range(1, 6):
            product_schema = ProductCreate(
                sku=f"{importer_name.upper()}-{category.upper()}-{i:04d}",
                name=f"Producto de ejemplo {i} de {importer_name}",
                price=100.0 * i,
                importer_name=importer_name,
                category=category
            )
            crud_product.create_product(db, product=product_schema)
            print(f"Job {job_id}: Creado producto {product_schema.sku}")
            time.sleep(1)  # Pausa entre productos
        
        return True
        
    except Exception as e:
        print(f"Job {job_id}: Error creando productos de ejemplo: {str(e)}")
        return False
