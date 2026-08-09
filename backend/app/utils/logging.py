import logging
import sys
from typing import Any


def setup_logging(name: str = "app") -> logging.Logger:
    """Configure structured logging for the application."""
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def get_logger(name: str = "app") -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
