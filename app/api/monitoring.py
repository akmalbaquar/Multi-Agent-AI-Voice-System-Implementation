"""
Monitoring and Metrics API
System health and performance monitoring
"""
from fastapi import APIRouter
from datetime import datetime
import logging
import psutil
import os

router = APIRouter()
logger = logging.getLogger(__name__)

# Track metrics
metrics = {
    "calls_total": 0,
    "calls_success": 0,
    "calls_failed": 0,
    "orders_total": 0,
    "orders_completed": 0,
    "start_time": datetime.now().isoformat()
}


@router.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - datetime.fromisoformat(metrics["start_time"])).total_seconds()
    }


@router.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_used_percent": memory.percent,
            "memory_available_mb": memory.available / 1024 / 1024,
            "disk_used_percent": disk.percent,
            "disk_free_gb": disk.free / 1024 / 1024 / 1024
        },
        "calls": {
            "total": metrics["calls_total"],
            "success": metrics["calls_success"],
            "failed": metrics["calls_failed"],
            "success_rate": (metrics["calls_success"] / metrics["calls_total"] * 100) if metrics["calls_total"] > 0 else 0
        },
        "orders": {
            "total": metrics["orders_total"],
            "completed": metrics["orders_completed"],
            "completion_rate": (metrics["orders_completed"] / metrics["orders_total"] * 100) if metrics["orders_total"] > 0 else 0
        },
        "uptime_seconds": (datetime.now() - datetime.fromisoformat(metrics["start_time"])).total_seconds()
    }


@router.get("/status")
async def system_status():
    """Detailed system status"""
    return {
        "status": "operational",
        "services": {
            "api": "running",
            "voice": "running",
            "orders": "running",
            "agents": "running"
        },
        "components": {
            "twilio": "connected",
            "openai": "connected",
            "database": "in-memory",
            "redis": "not configured"
        },
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }


def increment_call_metric(success: bool = True):
    """Increment call metrics"""
    metrics["calls_total"] += 1
    if success:
        metrics["calls_success"] += 1
    else:
        metrics["calls_failed"] += 1


def increment_order_metric(completed: bool = False):
    """Increment order metrics"""
    metrics["orders_total"] += 1
    if completed:
        metrics["orders_completed"] += 1
