"""
Global Configuration for NEXUZY ARTICAL
Author: Manoj Konar (monoj@nexuzy.in)
"""

import os
from pathlib import Path

# Application Info
APP_NAME = "NEXUZY ARTICAL"
APP_VERSION = "1.0.0"
DEVELOPER_NAME = "Manoj Konar"
DEVELOPER_EMAIL = "monoj@nexuzy.in"
COMPANY = "Nexuzy"

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"

# Create directories if not exist
DATABASE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Database paths
LOCAL_DB_PATH = DATABASE_DIR / "nexuzy_artical.db"

# Firebase Configuration
FIREBASE_CONFIG_PATH = BASE_DIR / "firebase_config.json"

# UI Configuration
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_RESIZABLE = True

# Colors
PRIMARY_COLOR = "#1f77d4"
DARK_COLOR = "#2c3e50"
LIGHT_COLOR = "#ecf0f1"
SUCCESS_COLOR = "#27ae60"
ERROR_COLOR = "#e74c3c"
WARNING_COLOR = "#f39c12"

# Fonts
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_HEADER = ("Segoe UI", 12, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)

# Network
INTERNET_CHECK_TIMEOUT = 3
SYNC_INTERVAL_SECONDS = 30  # Auto-sync every 30 seconds

# Security
PASSWORD_MIN_LENGTH = 6
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 300  # 5 minutes

# Roles
ROLE_ADMIN = "admin"
ROLE_USER = "user"

# Database Tables
USERS_TABLE = "users"
ARTICLES_TABLE = "articles"

# Sync Status
SYNC_PENDING = 0
SYNC_SYNCED = 1
