"""
Logging configuration
Author: Manoj Konar (monoj@nexuzy.in)
"""

import logging
import logging.handlers
from pathlib import Path
from config import LOGS_DIR, APP_NAME
from datetime import datetime

def setup_logger(name=APP_NAME):
    """
    Setup application logger with file and console handlers
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Ensure logs directory exists
    LOGS_DIR.mkdir(exist_ok=True)
    
    # File handler - rotate logs daily
    log_file = LOGS_DIR / f"nexuzy_artical_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
