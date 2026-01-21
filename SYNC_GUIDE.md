# Firebase Sync Guide - Complete Documentation

## Overview

NEXUZY ARTICAL now supports **bidirectional Firebase synchronization**:

### ⬇️ Download (Cloud → Local)
- On fresh install: Downloads all existing Firebase data
- Imports articles and users from cloud to local DB
- Prevents data loss when reinstalling app

### ⬆️ Upload (Local → Cloud)
- Creates/updates articles → Firebase
- Creates users → Firebase
- Image URLs stored in Firebase

### 🗑️ Delete Sync
- Delete article locally → Deletes from Firebase
- Delete user locally → Deletes from Firebase
- **CRITICAL FIX:** Deletes now sync properly!

---

## 🚀 Quick Setup

### 1. Get Firebase Config

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate New Private Key**
5. Download `firebase-adminsdk-xxxxx.json`
6. Rename to `firebase_config.json`
7. Place in same folder as EXE

### 2. Get FTP Config (for images)

1. Copy `ftp_config.json.example` to `ftp_config.json`
2. Edit with your FTP credentials:

```json
{
  "host": "ftp.yourdomain.com",
  "username": "your_ftp_user",
  "password": "your_password",
  "remote_dir": "/public_html/articles/images",
  "base_url": "https://yourdomain.com/articles/images",
  "timeout": 30,
  "passive_mode": true
}
```

### 3. First Run

**With Firebase Config:**
- App automatically downloads existing data from Firebase
- Creates local database with cloud data
- You're ready to go!

**Without Firebase Config:**
- App runs in offline mode
- Local database only
- Add `firebase_config.json` later to enable sync

---

## 🔄 How Sync Works

### Startup Sync (Fresh Install)

```
1. App starts
2. Checks if firebase_config.json exists
3. If yes:
   a. Connects to Firebase
   b. Downloads all articles from Firestore
   c. Downloads all users from Firestore
   d. Imports to local SQLite database
   e. Marks as synced
4. If no:
   a. Runs in offline mode
   b. Creates empty local database
```

### Create Article Sync

```
1. User creates article
2. Saved to local SQLite (sync_status = 0)
3. If image selected:
   a. Upload to FTP server
   b. Get public URL
4. Upload article + image URL to Firebase
5. Mark as synced (sync_status = 1)
```

### Update Article Sync

```
1. User edits article
2. Update local SQLite (sync_status = 0)
3. If image changed:
   a. Upload new image to FTP
   b. Get new URL
4. Update Firebase document with changes
5. Mark as synced (sync_status = 1)
```

### Delete Article Sync ✅ **FIXED**

```
1. User deletes article
2. Delete from local SQLite
3. CRITICAL: Also delete from Firebase Firestore
4. Both local and cloud are now in sync
```

**Previous Bug:** Deleted articles remained in Firebase  
**Fix:** `local_db.py` now calls `firebase_sync.delete_article()`

---

## 💾 Database Schema

### Local SQLite

**articles table:**
```sql
CREATE TABLE articles (
    id TEXT PRIMARY KEY,              -- Fides-XXXXXX
    article_name TEXT NOT NULL,
    mould TEXT NOT NULL,
    size TEXT NOT NULL,
    gender TEXT NOT NULL,
    created_by TEXT NOT NULL,
    image_path TEXT,                  -- FTP URL
    created_at DATETIME,
    updated_at DATETIME,
    sync_status INTEGER DEFAULT 0     -- 0=pending, 1=synced
);
```

**users table:**
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    last_login DATETIME,
    created_at DATETIME
);
```

### Firebase Firestore

**Collection: `articles`**
```json
{
  "id": "Fides-A7K9M2",
  "article_name": "Premium Shoe",
  "mould": "M-001",
  "size": "42",
  "gender": "Male",
  "created_by": "user_id_here",
  "image_path": "https://domain.com/articles/images/article_xxx.jpg",
  "created_at": "2026-01-21T14:30:22Z",
  "updated_at": "2026-01-21T14:30:22Z",
  "sync_status": 1
}
```

**Collection: `users`**
```json
{
  "id": "user_abc123",
  "username": "john_doe",
  "password_hash": "$2b$12$...",
  "role": "user",
  "created_at": "2026-01-20T10:00:00Z"
}
```

---

## 🔧 Technical Implementation

### Files Modified

1. **`db/firebase_sync.py`**
   - Added `download_all_articles()`
   - Added `download_all_users()`
   - Added `delete_article(article_id)`
   - Added `delete_user(user_id)`
   - Added `initial_sync_from_firebase(local_db)`

2. **`db/local_db.py`**
   - Added `firebase_sync` parameter
   - Modified `delete_article()` to sync delete
   - Modified `delete_user()` to sync delete
   - Modified `update_article()` to sync update

3. **`main.py`**
   - Calls `firebase.initial_sync_from_firebase(db)` on startup
   - Attaches Firebase to LocalDatabase

### Code Flow

```python
# main.py initialization
db = LocalDatabase()
firebase = FirebaseSync('firebase_config.json')

# Attach Firebase to DB
db.set_firebase_sync(firebase)

# Perform initial sync (fresh install)
if firebase.is_connected():
    stats = firebase.initial_sync_from_firebase(db)
    print(f"Synced {stats['articles']} articles, {stats['users']} users")
```

```python
# Delete article - FIXED
def delete_article(self, article_id: str) -> bool:
    # Delete locally
    self.cursor.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    self.connection.commit()
    
    # CRITICAL: Delete from Firebase too
    if self.firebase_sync and self.firebase_sync.is_connected():
        self.firebase_sync.delete_article(article_id)
    
    return True
```

---

## ✅ Testing Checklist

### Test Fresh Install Sync

1. **Prepare:**
   - Have existing data in Firebase (5+ articles, 2+ users)
   - Delete local `articles.db` if exists
   - Place `firebase_config.json` in app folder

2. **Run App:**
   - Launch NEXUZY_ARTICAL.exe
   - Watch console/logs for sync messages

3. **Verify:**
   - Check local database has articles
   - Check dashboard shows downloaded articles
   - All articles should have `sync_status = 1`

**Expected Output:**
```
[INFO] Firebase initialized successfully
[INFO] Downloading articles from Firebase...
[INFO] Downloaded 5 articles from Firebase
[INFO] Importing 5 articles from Firebase...
[INFO] Downloaded 2 users from Firebase
[INFO] Firebase import complete: 5 articles, 2 users
```

### Test Delete Sync

1. **Setup:**
   - Have Firebase configured
   - Create test article
   - Verify it appears in Firebase Firestore console

2. **Delete:**
   - Go to Articles page
   - Select article
   - Click "Delete"
   - Confirm deletion

3. **Verify:**
   - Article removed from local dashboard
   - Open Firebase Console
   - Check Firestore → `articles` collection
   - Article should be GONE from Firebase

**Expected Logs:**
```
[INFO] Article deleted: Fides-ABC123
[INFO] Deleted article Fides-ABC123 from Firebase
```

### Test Image Upload Sync

1. Create article with image
2. Image uploads to FTP
3. Article saves with FTP URL
4. Check Firebase document has `image_path` field
5. URL should be accessible

---

## 🐛 Troubleshooting

### "Firebase not initialized"

**Cause:** `firebase_config.json` missing or invalid

**Fix:**
1. Check file exists in same folder as EXE
2. Verify JSON is valid (use JSONLint.com)
3. Ensure Firebase project is active
4. Check Firebase credentials haven't expired

### "Downloaded 0 articles" but Firebase has data

**Cause:** Collection name mismatch

**Fix:**
1. Open Firebase Console
2. Go to Firestore Database
3. Verify collection is named `articles` (not `Articles` or `article`)
4. Case-sensitive!

### Deletes not syncing

**Previous Issue:** Fixed in this update

**Verify Fix:**
1. Pull latest code from GitHub
2. Check `db/local_db.py` line ~280
3. Should contain `self.firebase_sync.delete_article(article_id)`

### Sync status stuck at "Pending"

**Cause:** Firebase upload failed

**Fix:**
1. Check internet connection
2. Verify Firebase config is correct
3. Check Firebase Console for errors
4. Try manual sync from Sync Status page

---

## 📊 Monitoring Sync

### Dashboard Indicators

- **Total Articles:** Shows all articles in local DB
- **Pending Sync:** Shows articles with `sync_status = 0`
- **Status:** Online/Offline (Firebase connection)

### Logs

**Location:** `logs/app.log`

**What to look for:**
```
[INFO] Firebase initialized successfully       ✅ Good
[INFO] Downloaded 10 articles from Firebase    ✅ Sync working
[INFO] Uploaded article Fides-XXX to Firebase  ✅ Create working
[INFO] Deleted article Fides-XXX from Firebase ✅ Delete working
[ERROR] Firebase connection failed              ❌ Check config
[WARNING] FTP upload failed                      ⚠️ Check FTP config
```

---

## 🚀 Advanced Usage

### Manual Sync

If automatic sync fails, manually sync pending articles:

```python
# From Admin Dashboard → Sync Status
pending_articles = db.get_pending_articles()

for article in pending_articles:
    firebase.upload_article(article.to_dict())
    db.mark_article_synced(article.id)
```

### Backup & Restore

**Backup to Firebase:**
```bash
# All local data uploads to Firebase automatically
# No manual backup needed if sync is enabled
```

**Restore from Firebase:**
```bash
# Delete local database
rm data/articles.db

# Restart app with firebase_config.json
# All data downloads automatically
```

### Offline Mode

**Works without Firebase:**
- All features functional
- Local database only
- No cloud backup
- Add Firebase config later to sync

---

## 📝 Configuration Files

### firebase_config.json

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id-here",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

### ftp_config.json

```json
{
  "host": "ftp.yourdomain.com",
  "username": "ftp_user",
  "password": "secure_password",
  "remote_dir": "/public_html/articles/images",
  "base_url": "https://yourdomain.com/articles/images",
  "timeout": 30,
  "passive_mode": true
}
```

---

## ✅ Summary

### What's Fixed:

1. ✅ **Bidirectional Sync:** Download + Upload
2. ✅ **Fresh Install:** Auto-downloads Firebase data
3. ✅ **Delete Sync:** Deletes propagate to Firebase
4. ✅ **Image URLs:** Stored in Firebase
5. ✅ **Offline Mode:** Works without Firebase
6. ✅ **Config Templates:** Easy setup
7. ✅ **Build System:** Includes all configs
8. ✅ **Installer:** Inno Setup with configs

### Files Updated:

- `db/firebase_sync.py` - Bidirectional sync
- `db/local_db.py` - Delete sync integration
- `build/build.py` - Include configs in build
- `inno_setup.iss` - Enhanced installer
- `firebase_config.json.example` - Template
- `ftp_config.json.example` - Template

---

**Need Help?**  
Email: monoj@nexuzy.in  
GitHub: [david0154/NEXUZY_ARTICAL](https://github.com/david0154/NEXUZY_ARTICAL)
