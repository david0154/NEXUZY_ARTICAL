#!/usr/bin/env python3
"""Image Sync Utility

Automatically downloads images from Firebase URLs when app starts on fresh system.
Creates local cache for faster loading.
"""

import os
import logging
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Optional
import hashlib

logger = logging.getLogger(__name__)


class ImageSyncManager:
    """Manages image synchronization and local caching"""

    def __init__(self, cache_dir: str = None):
        """
        Initialize image sync manager.
        
        Args:
            cache_dir: Directory to store cached images (default: ./image_cache)
        """
        if cache_dir is None:
            # Create cache directory in app root
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'image_cache')
        
        self.cache_dir = cache_dir
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Image cache directory: {self.cache_dir}")
        except Exception as e:
            logger.error(f"Failed to create cache directory: {e}")

    def _get_cache_filename(self, url: str) -> str:
        """Generate cache filename from URL"""
        # Use hash of URL as filename to avoid conflicts
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        # Get file extension from URL
        ext = os.path.splitext(url.split('?')[0])[1] or '.jpg'
        return f"{url_hash}{ext}"

    def get_cached_path(self, url: str) -> Optional[str]:
        """
        Get local cached path for image URL.
        
        Args:
            url: Image URL
            
        Returns:
            Local path to cached image, or None if not cached
        """
        if not url or not url.startswith(('http://', 'https://')):
            return None
        
        cache_filename = self._get_cache_filename(url)
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        if os.path.exists(cache_path):
            return cache_path
        
        return None

    def download_image(self, url: str, force: bool = False) -> Optional[str]:
        """
        Download image from URL to local cache.
        
        Args:
            url: Image URL to download
            force: Force re-download even if cached
            
        Returns:
            Local path to downloaded image, or None if download failed
        """
        try:
            if not url or not url.startswith(('http://', 'https://')):
                return None

            cache_filename = self._get_cache_filename(url)
            cache_path = os.path.join(self.cache_dir, cache_filename)

            # Check if already cached
            if os.path.exists(cache_path) and not force:
                logger.debug(f"Image already cached: {cache_filename}")
                return cache_path

            # Download image
            logger.info(f"Downloading image: {url}")
            with urllib.request.urlopen(url, timeout=10) as response:
                image_data = response.read()

            # Save to cache
            with open(cache_path, 'wb') as f:
                f.write(image_data)

            logger.info(f"Image cached: {cache_filename}")
            return cache_path

        except urllib.error.HTTPError as e:
            logger.warning(f"HTTP error downloading image {url}: {e.code}")
            return None
        except urllib.error.URLError as e:
            logger.warning(f"URL error downloading image {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to download image {url}: {e}")
            return None

    def sync_articles_images(self, articles: List) -> dict:
        """
        Sync images for all articles from Firebase URLs.
        
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
