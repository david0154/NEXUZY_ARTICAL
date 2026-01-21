#!/usr/bin/env python3
"""FTP Image Uploader Utility

Handles uploading article images to FTP server and returns FTP paths (not URLs).
Author: Manoj Konar (monoj@nexuzy.in)

Build-safe config loading:
- In a PyInstaller build, users will keep ftp_config.json in the writable app-data folder
  (Option B via config.BASE_DIR).
"""

import ftplib
import os
import logging
import json
from pathlib import Path
from typing import Optional

from config import FTP_CONFIG_PATH

logger = logging.getLogger(__name__)


class FTPUploader:
    """Handles FTP file uploads for article images"""

    def __init__(
        self,
        host: str = None,
        port: int = 21,
        username: str = None,
        password: str = None,
        remote_dir: str = "/public_html/articles/images",
        base_url: str = "https://yourdomain.com/articles/images",
    ):
        # Try to load from ftp_config.json first
        self._load_config()

        # Override with provided params or env vars
        self.host = host or self.host or os.getenv("FTP_HOST")
        self.port = port if port != 21 else self.port
        self.username = username or self.username or os.getenv("FTP_USER")
        self.password = password or self.password or os.getenv("FTP_PASS")
        self.remote_dir = remote_dir if remote_dir != "/public_html/articles/images" else self.remote_dir
        self.base_url = base_url.rstrip("/") if base_url != "https://yourdomain.com/articles/images" else self.base_url.rstrip("/")
        self.connected = False
        self.ftp = None

    def _load_config(self):
        """Load FTP configuration from ftp_config.json (supports multiple key formats)."""
        try:
            config_path = Path(FTP_CONFIG_PATH)
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # Support both 'host' and 'ftp_host' formats
                self.host = config.get("host") or config.get("ftp_host")
                self.port = config.get("port", 21)
                self.username = config.get("username") or config.get("ftp_user")
                self.password = config.get("password") or config.get("ftp_pass")
                self.remote_dir = config.get("remote_dir") or config.get("ftp_remote_dir", "/public_html/articles/images")
                self.base_url = (config.get("public_url_base") or config.get("ftp_base_url", "https://yourdomain.com/articles/images")).rstrip("/")

                logger.info(f"FTP config loaded: {self.host}:{self.port}")
                logger.info(f"Remote directory: {self.remote_dir}")
                return
        except Exception as e:
            logger.error(f"Error loading ftp_config.json: {e}")

        # Default values if config file doesn't exist
        self.host = None
        self.port = 21
        self.username = None
        self.password = None
        self.remote_dir = "/public_html/articles/images"
        self.base_url = "https://yourdomain.com/articles/images"

    def connect(self) -> bool:
        """Establish FTP connection"""
        try:
            if not all([self.host, self.username, self.password]):
                logger.warning("FTP credentials not configured. Please update ftp_config.json")
                return False

            logger.info(f"Connecting to FTP: {self.username}@{self.host}:{self.port}")

            # Connect with port support
            if self.port and self.port != 21:
                self.ftp = ftplib.FTP(timeout=30)
                self.ftp.connect(self.host, self.port)
                self.ftp.login(self.username, self.password)
            else:
                self.ftp = ftplib.FTP(self.host, timeout=30)
                self.ftp.login(self.username, self.password)

            self.ftp.set_pasv(True)  # Use passive mode

            current_dir = self.ftp.pwd()
            logger.info(f"FTP login successful! Current directory: {current_dir}")

            # Navigate to remote directory
            try:
                logger.info(f"Attempting to change to: {self.remote_dir}")
                self.ftp.cwd(self.remote_dir)
                logger.info(f"Successfully changed to directory: {self.remote_dir}")
                logger.info(f"Current directory: {self.ftp.pwd()}")
            except ftplib.error_perm as e:
                logger.error(f"Directory {self.remote_dir} not accessible: {e}")

                # Try to create the directory
                try:
                    logger.info(f"Attempting to create directory: {self.remote_dir}")
                    self.ftp.mkd(self.remote_dir)
                    self.ftp.cwd(self.remote_dir)
                    logger.info(f"Created and changed to directory: {self.remote_dir}")
                except Exception as mkdir_error:
                    logger.error(f"Cannot create or access directory: {mkdir_error}")
                    logger.error(f"Please manually create the directory '{self.remote_dir}' on your FTP server")
                    return False

            self.connected = True
            logger.info(f"FTP connected successfully to {self.host}")
            return True

        except ftplib.error_perm as e:
            logger.error(f"FTP permission error: {e}")
            logger.error(f"Check credentials: {self.username}@{self.host}")
            self.connected = False
            return False
        except ftplib.all_errors as e:
            logger.error(f"FTP connection failed: {e}")
            logger.error(f"Host: {self.host}:{self.port}, User: {self.username}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected FTP error: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Close FTP connection"""
        if self.ftp:
            try:
                self.ftp.quit()
            except Exception:
                try:
                    self.ftp.close()
                except Exception:
                    pass
            self.connected = False
            logger.info("FTP disconnected")

    def upload_image(self, local_path: str, remote_filename: Optional[str] = None) -> Optional[str]:
        """Upload image file to FTP server and return FTP path."""
        try:
            if not os.path.exists(local_path):
                logger.error(f"Local file not found: {local_path}")
                return None

            # Connect if not already connected
            if not self.connected:
                if not self.connect():
                    logger.error("Cannot upload: FTP connection failed")
                    return None

            # Generate unique filename if not provided
            if not remote_filename:
                file_ext = Path(local_path).suffix.lower()
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                import random
                import string
                random_str = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
                remote_filename = f"article_{timestamp}_{random_str}{file_ext}"

            # Ensure we're in the correct directory
            try:
                self.ftp.cwd(self.remote_dir)
            except Exception:
                logger.error(f"Cannot access remote directory: {self.remote_dir}")
                return None

            logger.info(f"Uploading {os.path.basename(local_path)} as {remote_filename}")
            with open(local_path, "rb") as file:
                self.ftp.storbinary(f"STOR {remote_filename}", file)

            ftp_path = f"{self.remote_dir}/{remote_filename}"
            logger.info(f"✅ Image uploaded successfully to FTP: {ftp_path}")
            return ftp_path

        except ftplib.error_perm as e:
            logger.error(f"FTP permission error during upload: {e}")
            return None
        except Exception as e:
            logger.error(f"FTP upload failed: {e}")
            return None

    def download_image(self, ftp_path: str, local_path: str) -> bool:
        """Download image from FTP server with authentication"""
        try:
            if not self.connected:
                if not self.connect():
                    logger.error("Cannot download: FTP connection failed")
                    return False

            directory = os.path.dirname(ftp_path)
            filename = os.path.basename(ftp_path)

            if directory:
                try:
                    self.ftp.cwd(directory)
                except Exception:
                    logger.error(f"Cannot access directory: {directory}")
                    return False

            logger.info(f"Downloading from FTP: {ftp_path}")
            with open(local_path, "wb") as file:
                self.ftp.retrbinary(f"RETR {filename}", file.write)

            logger.info(f"✅ Downloaded to: {local_path}")
            return True

        except ftplib.error_perm as e:
            logger.error(f"FTP permission error during download: {e}")
            return False
        except Exception as e:
            logger.error(f"FTP download failed: {e}")
            return False


# Singleton instance
_ftp_uploader_instance = None


def get_ftp_uploader() -> FTPUploader:
    """Get singleton FTP uploader instance"""
    global _ftp_uploader_instance
    if _ftp_uploader_instance is None:
        _ftp_uploader_instance = FTPUploader()
    return _ftp_uploader_instance
