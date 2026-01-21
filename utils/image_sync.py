#!/usr/bin/env python3
"""Image Sync Utility

Automatically downloads images from FTP paths when app starts on fresh system.
Uses FTP authentication to download images (not public URLs).

PyInstaller-safe: Uses writable cache directory from config.
"""

import os
import sys
import logging
import hashlib
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class ImageSyncManager:
    """Manages image synchronization and local caching via FTP"""

    def __init__(self, cache_dir: str = None):
        """
        Initialize image sync manager.
        
        Args:
            cache_dir: Directory to store cached images (default: from config)
        """
        if cache_dir is None:
            # PyInstaller-safe: use writable directory from config
            try:
                import config
                cache_dir = str(config.IMAGE_CACHE_DIR)
            except Exception:
                # Fallback to current directory
                cache_dir = os.path.join(os.getcwd(), 'image_cache')
        
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
        self.ftp = None

    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Image cache directory: {self.cache_dir}")
        except Exception as e:
            logger.error(f"Failed to create cache directory: {e}")

    def _get_ftp(self):
        """Get FTP uploader instance (lazy load)"""
        if self.ftp is None:
            from utils.ftp_uploader import get_ftp_uploader
            self.ftp = get_ftp_uploader()
        return self.ftp

    def _get_cache_filename(self, ftp_path: str) -> str:
        """Generate cache filename from FTP path"""
        # Use hash of path as filename to avoid conflicts
        path_hash = hashlib.md5(ftp_path.encode()).hexdigest()[:12]
        # Get file extension from path
        ext = os.path.splitext(ftp_path)[1] or '.jpg'
        return f"{path_hash}{ext}"

    def get_cached_path(self, ftp_path: str) -> Optional[str]:
        """
        Get local cached path for FTP image path.
        
        Args:
            ftp_path: FTP path (e.g., /nexuzy/article_*.jpg)
            
        Returns:
            Local path to cached image, or None if not cached
        """
        if not ftp_path or not ftp_path.startswith('/'):
            return None
        
        cache_filename = self._get_cache_filename(ftp_path)
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        if os.path.exists(cache_path):
            return cache_path
        
        return None

    def download_image(self, ftp_path: str, force: bool = False) -> Optional[str]:
        """
        Download image from FTP path to local cache using FTP authentication.
        
        Args:
            ftp_path: FTP path to download (e.g., /nexuzy/article_*.jpg)
            force: Force re-download even if cached
            
        Returns:
            Local path to downloaded image, or None if download failed
        """
        try:
            if not ftp_path or not ftp_path.startswith('/'):
                logger.warning(f"Invalid FTP path: {ftp_path}")
                return None

            cache_filename = self._get_cache_filename(ftp_path)
            cache_path = os.path.join(self.cache_dir, cache_filename)

            # Check if already cached
            if os.path.exists(cache_path) and not force:
                logger.debug(f"Image already cached: {cache_filename}")
                return cache_path

            # Download via FTP
            logger.info(f"Downloading image via FTP: {ftp_path}")
            ftp = self._get_ftp()
            
            if ftp.download_image(ftp_path, cache_path):
                logger.info(f"Image cached: {cache_filename}")
                return cache_path
            else:
                logger.error(f"FTP download failed for: {ftp_path}")
                return None

        except Exception as e:
            logger.error(f"Failed to download image {ftp_path}: {e}")
            return None

    def sync_articles_images(self, articles: List) -> dict:
        """
        Sync images for all articles from FTP paths.
        
        Args:
            articles: List of article objects with image_path attributes
            
        Returns:
            Dictionary with sync statistics
        """
        stats = {
            'total': 0,
            'downloaded': 0,
            'cached': 0,
            'failed': 0,
            'no_image': 0
        }

        for article in articles:
            stats['total'] += 1
            
            if not article.image_path:
                stats['no_image'] += 1
                continue

            # Check if already cached
            cached_path = self.get_cached_path(article.image_path)
            if cached_path:
                stats['cached'] += 1
                continue

            # Download if not cached
            result = self.download_image(article.image_path)
            if result:
                stats['downloaded'] += 1
            else:
                stats['failed'] += 1

        logger.info(
            f"Image sync complete: {stats['downloaded']} downloaded, "
            f"{stats['cached']} cached, {stats['failed']} failed, "
            f"{stats['no_image']} no image"
        )

        return stats

    def clear_cache(self) -> int:
        """Clear all cached images. Returns number of files deleted."""
        count = 0
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    count += 1
            logger.info(f"Cleared {count} cached images")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
        return count

    def get_cache_size(self) -> int:
        """Get total size of cached images in bytes"""
        total_size = 0
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"Failed to get cache size: {e}")
        return total_size

    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        try:
            files = os.listdir(self.cache_dir)
            file_count = len([f for f in files if os.path.isfile(os.path.join(self.cache_dir, f))])
            total_size = self.get_cache_size()
            
            return {
                'file_count': file_count,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'file_count': 0, 'total_size_bytes': 0, 'total_size_mb': 0}


# Singleton instance
_image_sync_instance = None


def get_image_sync() -> ImageSyncManager:
    """Get singleton image sync manager instance"""
    global _image_sync_instance
    if _image_sync_instance is None:
        _image_sync_instance = ImageSyncManager()
    return _image_sync_instance
