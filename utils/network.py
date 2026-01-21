"""
Network utilities for internet connectivity check
Author: Manoj Konar (monoj@nexuzy.in)

Exports:
- NetworkChecker: class used by the app
- is_online(): functional helper (kept for compatibility)
"""

import socket
import logging
from config import INTERNET_CHECK_TIMEOUT

logger = logging.getLogger(__name__)


def is_online(timeout: int = INTERNET_CHECK_TIMEOUT) -> bool:
    """Check if internet connection is available (Google DNS ping)."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        logger.debug("Internet connection available")
        return True
    except (OSError, socket.timeout):
        logger.debug("No internet connection detected")
        return False


class NetworkChecker:
    """Backward-compatible checker used across the app."""

    def __init__(self, timeout: int = INTERNET_CHECK_TIMEOUT):
        self.timeout = timeout

    def is_connected(self) -> bool:
        return is_online(self.timeout)

    def is_online(self) -> bool:
        return is_online(self.timeout)


def check_firebase_connection(firebase_app) -> bool:
    """Verify Firebase connectivity (basic)."""
    try:
        if not is_online():
            return False
        return True
    except Exception as e:
        logger.error(f"Firebase connection check failed: {e}")
        return False
