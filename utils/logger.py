"""Logging utility"""
import logging
import sys
from config import LOGGING_CONFIG

def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup and return a logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOGGING_CONFIG["formatters"]["default"]["format"]))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

