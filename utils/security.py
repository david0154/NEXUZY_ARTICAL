"""
Security utilities for password hashing and encryption
Author: Manoj Konar (monoj@nexuzy.in)
"""

from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

def hash_password(password):
    """
    Hash a password using werkzeug
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    try:
        return generate_password_hash(password, method='pbkdf2:sha256')
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        return None

def verify_password(password, password_hash):
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password
        password_hash: Hashed password
        
    Returns:
        bool: True if password matches
    """
    try:
        return check_password_hash(password_hash, password)
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False

def validate_password_strength(password):
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        tuple: (is_valid, message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not has_letter or not has_number:
        return False, "Password must contain letters and numbers"
    
    return True, "Password is strong"
