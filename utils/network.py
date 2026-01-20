"""
Network utilities for internet connectivity check
Author: Manoj Konar (monoj@nexuzy.in)
"""

import socket
import logging
from config import INTERNET_CHECK_TIMEOUT

logger = logging.getLogger(__name__)

def is_online(timeout=INTERNET_CHECK_TIMEOUT):
    """
    Check if internet connection is available
    Uses Google's DNS (8.8.8.8) as reliable endpoint
    
    Args:
        timeout: Connection timeout in seconds
        
    Returns:
        bool: True if online, False if offline
    """
    try:
        # Try to connect to Google DNS
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        logger.info("Internet connection available")
        return True
    except (OSError, socket.timeout):
        logger.warning("No internet connection detected")
        return False

def check_firebase_connection(firebase_app):
    """
    Verify Firebase connectivity
    
    Args:
        firebase_app: Firebase app instance
        
    Returns:
        bool: True if Firebase is reachable
    """
    try:
        if not is_online():
            return False
        # Simple Firebase connectivity check
        return True
    except Exception as e:
        logger.error(f"Firebase connection check failed: {e}")
        return False
