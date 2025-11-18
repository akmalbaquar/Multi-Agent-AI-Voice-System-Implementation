"""
Logging Configuration
"""
import logging
import sys
from app.core.config import settings


def setup_logging():
    """Setup simple logging"""
    
    # Configure standard logging
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Simple formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()  # Clear existing handlers
    root_logger.addHandler(handler)

