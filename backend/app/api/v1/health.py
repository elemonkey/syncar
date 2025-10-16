"""
Health check endpoint para Docker y monitoreo
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
import redis.asyncio as redis
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check básico - retorna 200 si la API está viva
    """
    return {
        "status": "healthy",
        "service": "SYNCAR 2.0 API",
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check detallado - verifica todos los servicios
    """
    health_status = {
        "status": "healthy",
        "checks": {}
    }

    # Check database
    try:
        await db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"

    # Check Redis
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        await redis_client.close()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"

    return health_status

@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check para Kubernetes/Docker Swarm
    Retorna 200 solo si todos los servicios críticos están listos
    """
    try:
        # Verificar DB
        await db.execute("SELECT 1")

        # Verificar Redis
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await redis_client.ping()
        await redis_client.close()

        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}, 503

@router.get("/health/live")
async def liveness_check():
    """
    Liveness check para Kubernetes/Docker Swarm
    Retorna 200 si el proceso está vivo (no verifica dependencias)
    """
    return {"status": "alive"}
