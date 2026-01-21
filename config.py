"""
Global Configuration for NEXUZY ARTICAL
Author: Manoj Konar (monoj@nexuzy.in)

Build-safe paths:
- When packaged with PyInstaller (--onefile/--windowed), use a writable app-data directory
  so DB/logs/config work reliably after install.
"""

import os
import sys
from pathlib import Path

# Application Info
APP_NAME = "NEXUZY ARTICAL"
APP_VERSION = "1.0.0"
DEVELOPER_NAME = "Manoj Konar"
DEVELOPER_EMAIL = "monoj@nexuzy.in"
COMPANY = "Nexuzy"


def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def _get_appdata_base_dir() -> Path:
    """Return writable base dir (Option B).

    Windows: %APPDATA%\NEXUZY_ARTICAL
    Other OS: ~/.nexuzy_artical
    """
    app_dir_name = "NEXUZY_ARTICAL"

    # Windows
    appdata = os.getenv("APPDATA")
    if appdata:
        return Path(appdata) / app_dir_name

    # Fallback (mac/linux)
    return Path.home() / ".nexuzy_artical"


def _get_base_dir() -> Path:
    """Base directory for runtime files.

    - Source run (VS Code): project folder (same as this file)
    - Frozen build: writable AppData folder (Option B)
    """
    if _is_frozen():
        return _get_appdata_base_dir()
    return Path(__file__).resolve().parent


# Paths
BASE_DIR = _get_base_dir()
PROJECT_DIR = Path(__file__).resolve().parent  # for bundled assets/templates in source tree

DATABASE_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
ASSETS_DIR = BASE_DIR / "assets"  # for source-run; build should bundle assets separately

# Ensure runtime directories exist
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Database paths
LOCAL_DB_PATH = DATABASE_DIR / "nexuzy_artical.db"

# Firebase Configuration (service account json path)
FIREBASE_CONFIG_PATH = BASE_DIR / "firebase_config.json"

# FTP Configuration
FTP_CONFIG_PATH = BASE_DIR / "ftp_config.json"

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
