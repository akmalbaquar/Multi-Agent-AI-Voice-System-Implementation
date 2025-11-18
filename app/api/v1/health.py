"""
Health Check API
System health and readiness endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis

from app.db.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "voice-ai-system",
        "version": settings.APP_VERSION,
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check with database connectivity"""
    try:
        # Check database
        await db.execute("SELECT 1")
        
        # Check Redis
        redis_client = aioredis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()
        
        return {
            "status": "ready",
            "database": "connected",
            "redis": "connected",
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e),
        }


@router.get("/live")
async def liveness_check():
    """Liveness check"""
    return {"status": "alive"}
