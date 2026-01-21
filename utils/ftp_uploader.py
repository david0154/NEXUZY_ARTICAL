#!/usr/bin/env python3
"""FTP Image Uploader Utility

Handles uploading article images to FTP server and returns public URLs.
Author: Manoj Konar (monoj@nexuzy.in)
"""

import ftplib
import os
import logging
from pathlib import Path
from typing import Optional
import mimetypes

logger = logging.getLogger(__name__)


class FTPUploader:
    """Handles FTP file uploads for article images"""

    def __init__(self, host: str = None, username: str = None, password: str = None, 
                 remote_dir: str = '/public_html/articles/images', 
                 base_url: str = 'https://yourdomain.com/articles/images'):
        """
        Initialize FTP uploader.
        
        Args:
            host: FTP server hostname
            username: FTP username
            password: FTP password
            remote_dir: Remote directory path on FTP server
            base_url: Public base URL for accessing uploaded files
        """
        self.host = host or os.getenv('FTP_HOST')
        self.username = username or os.getenv('FTP_USER')
        self.password = password or os.getenv('FTP_PASS')
        self.remote_dir = remote_dir
        self.base_url = base_url.rstrip('/')
        self.connected = False
        self.ftp = None

    def connect(self) -> bool:
        """Establish FTP connection"""
        try:
            if not all([self.host, self.username, self.password]):
                logger.warning("FTP credentials not configured")
                return False

            self.ftp = ftplib.FTP(self.host, timeout=30)
            self.ftp.login(self.username, self.password)
            self.ftp.set_pasv(True)  # Use passive mode
            
            # Create remote directory if it doesn't exist
            try:
                self.ftp.cwd(self.remote_dir)
            except:
                # Try to create directory path
                dirs = self.remote_dir.strip('/').split('/')
                current = '/'
                for dir_name in dirs:
                    try:
                        self.ftp.cwd(f"{current}/{dir_name}")
                        current = f"{current}/{dir_name}"
                    except:
                        self.ftp.mkd(f"{current}/{dir_name}")
                        self.ftp.cwd(f"{current}/{dir_name}")
                        current = f"{current}/{dir_name}"
            
            self.connected = True
            logger.info(f"FTP connected to {self.host}")
            return True

        except ftplib.all_errors as e:
            logger.error(f"FTP connection failed: {e}")
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
            Public URL of uploaded image, or None if upload failed
        """
        try:
            if not os.path.exists(local_path):
                logger.error(f"Local file not found: {local_path}")
                return None

            # Connect if not already connected
            if not self.connected:
                if not self.connect():
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
            self.ftp.cwd(self.remote_dir)

            # Upload file in binary mode
            with open(local_path, 'rb') as file:
                self.ftp.storbinary(f'STOR {remote_filename}', file)

            # Construct public URL
            public_url = f"{self.base_url}/{remote_filename}"
            logger.info(f"Image uploaded: {public_url}")
            return public_url

        except Exception as e:
            logger.error(f"FTP upload failed: {e}")
            return None

    def delete_image(self, filename: str) -> bool:
        """Delete image from FTP server"""
        try:
            if not self.connected:
                if not self.connect():
                    return False

            self.ftp.cwd(self.remote_dir)
            self.ftp.delete(filename)
            logger.info(f"Image deleted from FTP: {filename}")
            return True

        except Exception as e:
            logger.error(f"FTP delete failed: {e}")
            return False

    def test_connection(self) -> bool:
        """Test FTP connection"""
        try:
            if self.connect():
                self.disconnect()
                return True
            return False
        except Exception as e:
            logger.error(f"FTP test failed: {e}")
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
