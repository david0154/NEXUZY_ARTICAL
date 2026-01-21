#!/usr/bin/env python3
"""FTP Image Uploader Utility

Handles uploading article images to FTP server and returns FTP paths (not URLs).
Author: Manoj Konar (monoj@nexuzy.in)

PyInstaller-safe: Loads config from config.FTP_CONFIG_PATH
"""

import ftplib
import os
import sys
import logging
import json
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FTPUploader:
    """Handles FTP file uploads for article images"""

    def __init__(self, host: str = None, port: int = 21, username: str = None, password: str = None, 
                 remote_dir: str = '/public_html/articles/images', 
                 base_url: str = 'https://yourdomain.com/articles/images'):
        """
        Initialize FTP uploader.
        
        Args:
            host: FTP server hostname
            port: FTP server port (default 21)
            username: FTP username
            password: FTP password
            remote_dir: Remote directory path on FTP server
            base_url: Public base URL (not used for blocked servers)
        """
        # Try to load from ftp_config.json first
        self._load_config()
        
        # Override with provided params or env vars
        self.host = host or self.host or os.getenv('FTP_HOST')
        self.port = port if port != 21 else self.port
        self.username = username or self.username or os.getenv('FTP_USER')
        self.password = password or self.password or os.getenv('FTP_PASS')
        self.remote_dir = remote_dir if remote_dir != '/public_html/articles/images' else self.remote_dir
        self.base_url = base_url.rstrip('/') if base_url != 'https://yourdomain.com/articles/images' else self.base_url.rstrip('/')
        self.connected = False
        self.ftp = None

    def _load_config(self):
        """Load FTP configuration from ftp_config.json - PyInstaller safe"""
        try:
            # PyInstaller-safe: use config.FTP_CONFIG_PATH
            try:
                import config
                config_path = str(config.FTP_CONFIG_PATH)
            except Exception:
                # Fallback for old code
                if getattr(sys, 'frozen', False):
                    # PyInstaller bundle
                    config_path = os.path.join(sys._MEIPASS, 'ftp_config.json')
                else:
                    # Running from source
                    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ftp_config.json')
            
            logger.info(f"Loading FTP config from: {config_path}")
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # Support both 'host' and 'ftp_host' formats
                    self.host = config.get('host') or config.get('ftp_host')
                    self.port = config.get('port', 21)
                    self.username = config.get('username') or config.get('ftp_user')
                    self.password = config.get('password') or config.get('ftp_pass')
                    self.remote_dir = config.get('remote_dir') or config.get('ftp_remote_dir', '/public_html/articles/images')
                    self.base_url = (config.get('public_url_base') or config.get('ftp_base_url', 'https://yourdomain.com/articles/images')).rstrip('/')
                    
                    logger.info(f"✅ FTP config loaded: {self.host}:{self.port}")
                    logger.info(f"   Remote directory: {self.remote_dir}")
                    return
            else:
                logger.warning(f"FTP config file not found: {config_path}")
        except Exception as e:
            logger.error(f"Error loading ftp_config.json: {e}")
        
        # Default values if config file doesn't exist
        self.host = None
        self.port = 21
        self.username = None
        self.password = None
        self.remote_dir = '/public_html/articles/images'
        self.base_url = 'https://yourdomain.com/articles/images'

    def connect(self) -> bool:
        """Establish FTP connection"""
        try:
            if not all([self.host, self.username, self.password]):
                logger.warning("❌ FTP credentials not configured. Please check ftp_config.json")
                logger.warning(f"   Host: {self.host}")
                logger.warning(f"   User: {self.username}")
                logger.warning(f"   Pass: {'***' if self.password else 'None'}")
                return False

            logger.info(f"🔗 Connecting to FTP: {self.username}@{self.host}:{self.port}")
            
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
            logger.info(f"✅ FTP login successful! Current directory: {current_dir}")
            
            # Navigate to remote directory
            try:
                logger.info(f"📁 Attempting to change to: {self.remote_dir}")
                self.ftp.cwd(self.remote_dir)
                logger.info(f"✅ Successfully changed to directory: {self.remote_dir}")
                logger.info(f"   Current directory: {self.ftp.pwd()}")
            except ftplib.error_perm as e:
                logger.error(f"❌ Directory {self.remote_dir} not accessible: {e}")
                
                # List current directory contents for debugging
                try:
                    logger.info("Available directories:")
                    dirs = self.ftp.nlst()
                    for d in dirs[:10]:  # Show first 10
                        logger.info(f"  - {d}")
                except:
                    pass
                
                # Try to create the directory
                try:
                    logger.info(f"🔨 Attempting to create directory: {self.remote_dir}")
                    self.ftp.mkd(self.remote_dir)
                    self.ftp.cwd(self.remote_dir)
                    logger.info(f"✅ Created and changed to directory: {self.remote_dir}")
                except Exception as mkdir_error:
                    logger.error(f"❌ Cannot create or access directory: {mkdir_error}")
                    logger.error(f"   Please manually create '{self.remote_dir}' on your FTP server")
                    return False
            
            self.connected = True
            logger.info(f"✅ FTP connected successfully to {self.host}")
            return True

        except ftplib.error_perm as e:
            logger.error(f"❌ FTP permission error: {e}")
            logger.error(f"   Check credentials: {self.username}@{self.host}")
            self.connected = False
            return False
        except ftplib.all_errors as e:
            logger.error(f"❌ FTP connection failed: {e}")
            logger.error(f"   Host: {self.host}:{self.port}, User: {self.username}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected FTP error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.connected = False
            return False

    def disconnect(self):
        """Close FTP connection"""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                try:
                    self.ftp.close()
                except:
                    pass
            self.connected = False
            logger.info("FTP disconnected")

    def upload_image(self, local_path: str, remote_filename: Optional[str] = None) -> Optional[str]:
        """
        Upload image file to FTP server.
        
        Args:
            local_path: Path to local image file
            remote_filename: Optional custom filename (generated if not provided)
            
        Returns:
            FTP path (e.g., /nexuzy/article_20260121_123456.jpg), or None if upload failed
        """
        try:
            if not os.path.exists(local_path):
                logger.error(f"❌ Local file not found: {local_path}")
                return None

            # Connect if not already connected
            if not self.connected:
                if not self.connect():
                    logger.error("❌ Cannot upload: FTP connection failed")
                    return None

            # Generate unique filename if not provided
            if not remote_filename:
                file_ext = Path(local_path).suffix.lower()
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                import random
                import string
                random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                remote_filename = f"article_{timestamp}_{random_str}{file_ext}"

            # Ensure we're in the correct directory
            try:
                self.ftp.cwd(self.remote_dir)
            except:
                logger.error(f"❌ Cannot access remote directory: {self.remote_dir}")
                return None

            # Upload file in binary mode
            logger.info(f"📤 Uploading {os.path.basename(local_path)} as {remote_filename}")
            with open(local_path, 'rb') as file:
                self.ftp.storbinary(f'STOR {remote_filename}', file)

            # Return FTP path (not URL)
            ftp_path = f"{self.remote_dir}/{remote_filename}"
            logger.info(f"✅ Image uploaded successfully to FTP: {ftp_path}")
            return ftp_path

        except ftplib.error_perm as e:
            logger.error(f"❌ FTP permission error during upload: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ FTP upload failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def download_image(self, ftp_path: str, local_path: str) -> bool:
        """Download image from FTP server with authentication
        
        Args:
            ftp_path: FTP path (e.g., /nexuzy/article_*.jpg)
            local_path: Local path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"📥 Attempting to download: {ftp_path}")
            
            # Connect if not already connected
            if not self.connected:
                logger.info("   Connecting to FTP server...")
                if not self.connect():
                    logger.error("❌ Cannot download: FTP connection failed")
                    return False

            # Extract directory and filename from path
            directory = os.path.dirname(ftp_path)
            filename = os.path.basename(ftp_path)
            
            logger.info(f"   Directory: {directory}")
            logger.info(f"   Filename: {filename}")

            # Change to directory
            if directory:
                try:
                    self.ftp.cwd(directory)
                    logger.info(f"   Changed to directory: {directory}")
                except Exception as e:
                    logger.error(f"❌ Cannot access directory {directory}: {e}")
                    return False

            # Download file
            logger.info(f"   Downloading to: {local_path}")
            with open(local_path, 'wb') as file:
                self.ftp.retrbinary(f'RETR {filename}', file.write)

            logger.info(f"✅ Downloaded successfully: {local_path}")
            return True

        except ftplib.error_perm as e:
            logger.error(f"❌ FTP permission error during download: {e}")
            logger.error(f"   File may not exist: {ftp_path}")
            return False
        except Exception as e:
            logger.error(f"❌ FTP download failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def delete_image(self, filename: str) -> bool:
        """Delete image from FTP server"""
        try:
            if not self.connected:
                if not self.connect():
                    return False

            self.ftp.cwd(self.remote_dir)
            self.ftp.delete(filename)
            logger.info(f"✅ Image deleted from FTP: {filename}")
            return True

        except Exception as e:
            logger.error(f"❌ FTP delete failed: {e}")
            return False

    def test_connection(self) -> bool:
        """Test FTP connection"""
        try:
            if self.connect():
                logger.info("✅ FTP connection test: SUCCESS")
                self.disconnect()
                return True
            logger.error("❌ FTP connection test: FAILED")
            return False
        except Exception as e:
            logger.error(f"❌ FTP test failed: {e}")
            return False

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Singleton instance
_ftp_uploader_instance = None


def get_ftp_uploader() -> FTPUploader:
    """Get singleton FTP uploader instance"""
    global _ftp_uploader_instance
    if _ftp_uploader_instance is None:
        _ftp_uploader_instance = FTPUploader()
    return _ftp_uploader_instance
