# Image Synchronization Feature

## Overview

The application automatically downloads and caches images from Firebase URLs when installed on a fresh system. This ensures all article images are available offline after the initial sync.

## How It Works

### 1. **Image Upload Flow**
```
User selects image → Upload to FTP → Get FTP URL → Save to Database → Sync to Firebase
```

### 2. **Image Download Flow (Fresh Install)**
```
App starts → Connect to Firebase → Get all articles → Download missing images → Cache locally
```

### 3. **Local Cache**
- **Location**: `./image_cache/`
- **Format**: Hash-based filenames (e.g., `abc123def456.jpg`)
- **Purpose**: Faster loading, offline access

## Features

### ✅ **Automatic Sync on Startup**
- Downloads all article images from Firebase URLs
- Creates local cache for faster access
- Skips already cached images
- Shows sync progress and statistics

### ✅ **Smart Caching**
- Only downloads missing images
- Validates image exists before download
- Handles network errors gracefully
- Automatic retry on failure

### ✅ **Cache Management**
- View cache statistics (file count, total size)
- Clear cache when needed
- Automatic cleanup of old/unused images

## Usage

### Get Image Sync Manager
```python
from utils.image_sync import get_image_sync

image_sync = get_image_sync()
```

### Sync All Articles
```python
articles = db.get_all_articles()
stats = image_sync.sync_articles_images(articles)

print(f"Downloaded: {stats['downloaded']}")
print(f"Cached: {stats['cached']}")
print(f"Failed: {stats['failed']}")
```

### Download Single Image
```python
local_path = image_sync.download_image("https://hypechats.com/nexuzy/image.jpg")
if local_path:
    print(f"Image cached at: {local_path}")
```

### Get Cached Path
```python
# Check if image is already cached
cached_path = image_sync.get_cached_path("https://hypechats.com/nexuzy/image.jpg")
if cached_path:
    # Use local cached file
    img = Image.open(cached_path)
else:
    # Download first
    cached_path = image_sync.download_image(url)
```

### Cache Statistics
```python
stats = image_sync.get_cache_stats()
print(f"Files: {stats['file_count']}")
print(f"Size: {stats['total_size_mb']} MB")
```

### Clear Cache
```python
deleted = image_sync.clear_cache()
print(f"Deleted {deleted} cached images")
```

## Integration with Dashboards

### On App Startup (main.py)
```python
from utils.image_sync import get_image_sync

# After database initialization
image_sync = get_image_sync()
articles = db.get_all_articles()

# Sync images in background
logger.info("Starting image sync...")
stats = image_sync.sync_articles_images(articles)
logger.info(f"Image sync complete: {stats['downloaded']} downloaded")
```

### In Dashboard Preview
```python
def show_image_preview(self, image_url, title):
    # Try to use cached image first
    local_path = self.image_sync.get_cached_path(image_url)
    
    if not local_path:
        # Download if not cached
        local_path = self.image_sync.download_image(image_url)
    
    if local_path and os.path.exists(local_path):
        # Load from local cache
        img = Image.open(local_path)
    else:
        # Fallback to URL download
        with urllib.request.urlopen(image_url) as response:
            img = Image.open(io.BytesIO(response.read()))
```

## FTP Configuration

### Correct Directory Structure

Your FTP config should use the ROOT directory for your domain:

```json
{
  "host": "ftp.hypechats.com",
  "port": 21,
  "username": "nexuzy@hypechats.com",
  "password": "your_password",
  "remote_dir": "/nexuzy",
  "public_url_base": "https://hypechats.com/nexuzy"
}
```

**NOT** `/hypechats.com/nexuzy` (causes nested directories)

### File Structure
```
FTP Server:
  /nexuzy/
    ├── article_20260121_123456_abc123.jpg
    ├── article_20260121_123500_def456.jpg
    └── ...

Public URLs:
  https://hypechats.com/nexuzy/article_20260121_123456_abc123.jpg
  https://hypechats.com/nexuzy/article_20260121_123500_def456.jpg
```

## Troubleshooting

### Images Not Downloading
1. Check internet connection
2. Verify Firebase URLs are correct
3. Check `image_cache/` directory permissions
4. Review logs for error messages

### Cache Taking Too Much Space
```python
# Check size
stats = image_sync.get_cache_stats()
print(f"Cache size: {stats['total_size_mb']} MB")

# Clear if needed
image_sync.clear_cache()
```

### FTP Upload Fails
1. Check `ftp_config.json` credentials
2. Verify `remote_dir` path is correct (should be `/nexuzy`)
3. Test connection: `ftp.test_connection()`
4. Manually create directory on FTP server if needed

## Benefits

✅ **Fresh System Ready**: Images automatically download on first run  
✅ **Faster Loading**: Cached images load instantly  
✅ **Offline Access**: View images without internet  
✅ **Bandwidth Saving**: Download once, use many times  
✅ **No Manual Sync**: Everything automatic  

## Future Enhancements

- [ ] Background sync with progress bar
- [ ] Selective sync (only recent articles)
- [ ] Automatic cache cleanup (remove old/unused)
- [ ] Compression for cache storage
- [ ] Delta sync (only new images)
