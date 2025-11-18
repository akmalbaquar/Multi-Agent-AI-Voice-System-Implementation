"""
Multi-Agent AI Voice System
Main Application Entry Point
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api import voice
from app.api import orders

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Agent AI Voice Calling System for Food Delivery Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include voice API router
# Include routers
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])

# Add monitoring endpoints
from app.api import monitoring
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])


@app.on_event("startup")
async def startup():
    """Startup event"""
    logger.info("Starting Multi-Agent AI Voice System...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event"""
    logger.info("Shutting down...")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multi-Agent AI Voice System API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
