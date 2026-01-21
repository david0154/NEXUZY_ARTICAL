# Assets Folder

This folder contains application assets like logos and icons.

## Required Files

### 1. Logo (`logo.png`)
- **Size:** 200x200 pixels (will be resized to 80x80 in login)
- **Format:** PNG with transparent background recommended
- **Purpose:** Displayed on login screen above app name
- **Location:** `assets/logo.png`

### 2. Icon (`icon.ico`)
- **Format:** ICO file
- **Purpose:** Window icon/taskbar icon
- **Location:** `assets/icon.ico`

## Setup Instructions

1. **Add your logo:**
   ```bash
   # Place your logo file here:
   assets/logo.png
   ```

2. **Add your icon:**
   ```bash
   # Place your icon file here:
   assets/icon.ico
   ```

3. **If files are missing:**
   - Login will show app initial letter instead of logo
   - Window will use default system icon

## Creating Logo from Existing Image

If you have an image and need to convert it:

```python
from PIL import Image

# Open your image
img = Image.open('your_logo.png')

# Resize to 200x200
img = img.resize((200, 200), Image.Resampling.LANCZOS)

# Save
img.save('assets/logo.png')
```

## Notes

- Logo is displayed at 80x80px on login screen
- Transparent background recommended for best appearance
- Fallback: First letter of APP_NAME shown if logo not found
