"""
Logging configuration
Author: Manoj Konar (monoj@nexuzy.in)

This module provides:
- setup_logger(): returns a configured stdlib logger
- Logger: small wrapper class used across the app (backward compatible)
"""

import logging
import logging.handlers
from datetime import datetime

from config import LOGS_DIR, APP_NAME


def setup_logger(name: str = APP_NAME) -> logging.Logger:
    """Setup application logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Ensure logs directory exists
    LOGS_DIR.mkdir(exist_ok=True)

    # Avoid duplicate handlers if setup_logger called multiple times
    if getattr(logger, "_nexuzy_configured", False):
        return logger

    # File handler - rotating log
    log_file = LOGS_DIR / f"nexuzy_artical_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
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

    logger._nexuzy_configured = True
    return logger


class Logger:
    """Backward-compatible logger wrapper used by the app."""

    def __init__(self, name: str = APP_NAME):
        self._logger = setup_logger(name)

    def debug(self, msg: str):
        self._logger.debug(msg)

    def info(self, msg: str):
        self._logger.info(msg)

    def warning(self, msg: str):
        self._logger.warning(msg)

    def error(self, msg: str):
        self._logger.error(msg)

    def exception(self, msg: str):
        self._logger.exception(msg)
