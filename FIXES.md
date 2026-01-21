# Bug Fixes and New Features

## 🐛 Critical Bug Fixes

### 1. **Dialog Closing Bug - FIXED** ✅

**Problem:**
- When opening "Create Article" or "Add User" dialog in Admin/User dashboard
- Dialog would close unexpectedly
- All entry windows would hide/minimize
- Application kept running but was unusable
- Only the dialog window was affected

**Root Cause:**
- `Toplevel` dialogs were not properly bound to parent window
- Missing `transient()` and `grab_set()` calls
- Window manager was treating dialog as independent window

**Solution:**
```python
# BEFORE (Broken)
dialog = tk.Toplevel(self.root)
dialog.title("Create Article")
# ... rest of code

# AFTER (Fixed)
dialog = tk.Toplevel(self.root)
dialog.title("Create Article")
dialog.transient(self.root)  # Make dialog child of root
dialog.grab_set()            # Modal dialog (blocks parent)
dialog.wait_window()         # Wait until dialog closes
```

**Files Changed:**
- `dashboard/admin_dashboard.py` - Lines 280-282
- `dashboard/user_dashboard.py` - Lines 220-222

---

## ✨ New Features

### 2. **FTP Image Upload** 📷

**Feature:**
- Upload article images to FTP server
- Store public image URL in database and Firebase
- Automatic filename generation with timestamp
- Progress indicator during upload
- Graceful fallback if upload fails

**Configuration:**

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your FTP credentials:
```env
FTP_HOST=ftp.yourdomain.com
FTP_USER=your_username
FTP_PASS=your_password
FTP_REMOTE_DIR=/public_html/articles/images
FTP_BASE_URL=https://yourdomain.com/articles/images
```

3. Install required package:
```bash
pip install python-dotenv
```

**Usage:**

1. Click "Create Article" in Admin or User dashboard
2. Fill in article details
3. Click "📷 Select Image" button
4. Choose image file (PNG, JPG, GIF, BMP)
5. Image filename will be displayed
6. Click "Save Article"
7. Status will show: "⏳ Uploading image to server..."
8. On success: "✅ Image uploaded successfully!"
9. Image URL is saved to database and synced to Firebase

**How It Works:**

```python
from utils.ftp_uploader import get_ftp_uploader

# Get FTP uploader instance
ftp = get_ftp_uploader()

# Upload image (returns public URL)
image_url = ftp.upload_image('/path/to/local/image.jpg')
# Returns: "https://yourdomain.com/articles/images/article_20260121_143022_a3x9k2.jpg"

# Store URL in database
article.image_path = image_url
db.add_article(article)

# Sync to Firebase with image URL
firebase.sync_articles([article.to_dict()])
```

**File Structure:**
```
utils/
└── ftp_uploader.py       # FTP upload handler
.env.example              # Configuration template
.env                      # Your credentials (gitignored)
```

---

### 3. **Image URL Storage in Firebase** ☁️

**Before:**
- Only local file path was stored: `/home/user/image.jpg`
- Image not accessible from other devices
- No cloud backup of images

**After:**
- Public FTP URL stored: `https://yourdomain.com/articles/images/article_xxx.jpg`
- Images accessible from anywhere
- URL synced to Firebase Firestore
- Images can be displayed in web dashboard

**Database Schema:**
```sql
CREATE TABLE articles (
    id TEXT PRIMARY KEY,              -- Fides-XXXXXX
    article_name TEXT NOT NULL,
    mould TEXT NOT NULL,
    size TEXT NOT NULL,
    gender TEXT NOT NULL,
    created_by TEXT NOT NULL,
    image_path TEXT,                  -- FTP URL (NEW)
    created_at DATETIME,
    updated_at DATETIME,
    sync_status INTEGER DEFAULT 0
);
```

**Firebase Document:**
```json
{
  "id": "Fides-A7K9M2",
  "article_name": "Premium Shoe",
  "mould": "M-001",
  "size": "42",
  "gender": "Male",
  "created_by": "admin_user_id",
  "image_path": "https://yourdomain.com/articles/images/article_20260121_143022_a3x9k2.jpg",
  "created_at": "2026-01-21T14:30:22Z",
  "sync_status": 1
}
```

---

### 4. **Image Display in Dashboard** 🖼️

**Planned Features (Coming Soon):**

- Thumbnail preview in article list
- Full-size image viewer on click
- Image download option
- Image cache for offline viewing

**Example Implementation:**
```python
# In show_articles() method
if article.image_path and article.image_path.startswith('http'):
    try:
        from PIL import Image, ImageTk
        import requests
        from io import BytesIO
        
        # Download image
        response = requests.get(article.image_path, timeout=5)
        img = Image.open(BytesIO(response.content))
        
        # Create thumbnail
        img.thumbnail((50, 50), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        # Display in Treeview or Label
        image_label = tk.Label(frame, image=photo)
        image_label.image = photo  # Keep reference
        image_label.pack()
    except Exception as e:
        logger.error(f"Failed to load image: {e}")
```

---

## 🛠️ Technical Details

### FTP Upload Process

1. **Connection**
   - Connect to FTP server using credentials from `.env`
   - Switch to passive mode for firewall compatibility
   - Navigate to remote directory

2. **File Upload**
   - Generate unique filename: `article_YYYYMMDD_HHMMSS_random6.ext`
   - Upload file in binary mode
   - Return public URL

3. **Error Handling**
   - Connection timeout: 30 seconds
   - Automatic retry: No (fails gracefully)
   - Fallback: Save article without image

### Security Considerations

1. **Credentials**
   - Never commit `.env` file to git
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **File Validation**
   - Check file extension before upload
   - Validate MIME type
   - Scan for malware (recommended in production)

3. **Access Control**
   - FTP user should have limited permissions
   - Read-write only to images directory
   - No shell access

---

## 📝 Testing Instructions

### Test Dialog Fix

1. Login as Admin or User
2. Click "Create Article" or "Add New Article"
3. Dialog should open WITHOUT closing parent window
4. Fill form and click "Save"
5. Dialog should close properly
6. Dashboard should remain visible

**Expected Result:** ✅ Dialog works normally
**Previous Bug:** ❌ Parent window would minimize

### Test FTP Upload

1. Configure `.env` with valid FTP credentials
2. Login to application
3. Click "Create Article"
4. Click "📷 Select Image"
5. Choose an image file
6. Fill other fields
7. Click "Save Article"
8. Watch for upload status:
   - "⏳ Uploading image to server..."
   - "✅ Image uploaded successfully!"
9. Check database: `image_path` should contain URL
10. Verify image is accessible at URL

**Expected Result:** ✅ Image uploaded and URL stored

### Test Without FTP (Fallback)

1. Don't configure `.env` or use invalid credentials
2. Try to create article with image
3. Should see: "⚠️ Image upload failed, saving without image"
4. Article should still be created
5. `image_path` will be `null`

**Expected Result:** ✅ Article saves without image

---

## 🚀 Deployment

### For Development

```bash
# Install dependencies
pip install python-dotenv requests Pillow

# Configure FTP
cp .env.example .env
nano .env  # Edit with your credentials

# Run application
python main.py
```

### For Production (Executable)

```bash
# Build with FTP support
python build/build.py

# Copy .env to dist folder
cp .env dist/

# Distribute
zip -r NEXUZY_ARTICAL.zip dist/
```

**Important:** Users must have `.env` file in same directory as executable!

---

## 🐛 Known Issues

1. **Large Images**
   - Images over 5MB may timeout
   - Recommend max 2MB per image
   - Add image compression in future

2. **Slow FTP Servers**
   - 30-second timeout may not be enough
   - Increase in `ftp_uploader.py` line 35

3. **No Image Preview**
   - Dashboard doesn't show image thumbnails yet
   - Planned for next release

---

## 📚 Additional Resources

- [FTP Setup Guide](https://help.dreamhost.com/hc/en-us/articles/115000675027-FTP-overview-and-credentials)
- [Environment Variables](https://pypi.org/project/python-dotenv/)
- [Tkinter Dialogs Best Practices](https://tkdocs.com/tutorial/windows.html)

---

## ✅ Changelog

### Version 2.1 (2026-01-21)

**Fixed:**
- 🐛 Dialog closing bug in Admin/User dashboards
- 🐛 Parent window minimizing when opening dialogs
- 🐛 Application becoming unresponsive after dialog close

**Added:**
- ✨ FTP image upload functionality
- ✨ Image URL storage in database and Firebase
- ✨ Upload progress indicators
- ✨ Graceful fallback for failed uploads
- ✨ FTP configuration via `.env` file
- 📄 `.env.example` template
- 📄 `utils/ftp_uploader.py` module
- 📄 This FIXES.md documentation

**Changed:**
- 🔄 `image_path` now stores URL instead of local path
- 🔄 Dialog windows now properly modal and transient
- 🔄 Build script includes FTP dependencies

---

**Need Help?**

Contact: monoj@nexuzy.in  
GitHub Issues: [github.com/david0154/NEXUZY_ARTICAL/issues](https://github.com/david0154/NEXUZY_ARTICAL/issues)
