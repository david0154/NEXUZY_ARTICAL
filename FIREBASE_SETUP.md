# NEXUZY ARTICAL - Firebase Setup & Integration Guide

**Project:** NEXUZY ARTICAL  
**Version:** 1.0.0  
**Developer:** Manoj Konar  
**Email:** monoj@nexuzy.in  
**Date:** January 20, 2026  

---

## 📋 Table of Contents

1. [Firebase Project Setup](#firebase-project-setup)
2. [Firestore Database Configuration](#firestore-database-configuration)
3. [Authentication Setup](#authentication-setup)
4. [Firebase Integration](#firebase-integration)
5. [Security Rules](#security-rules)
6. [Data Synchronization](#data-synchronization)
7. [Troubleshooting](#troubleshooting)

---

## Firebase Project Setup

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **Add Project** or **Create a project**
3. Enter project name: `NEXUZY_ARTICAL`
4. Enable Google Analytics (optional)
5. Click **Create project**
6. Wait for project to initialize

### Step 2: Get Service Account Key

**This is CRITICAL for the application to work!**

1. In Firebase Console, go to **Project Settings** (gear icon)
2. Click **Service Accounts** tab
3. Click **Generate New Private Key**
4. Save the JSON file as `firebase_config.json` in your project root:
   ```
   NEXUZY_ARTICAL/
   ├── firebase_config.json  ← Place it here
   ├── main.py
   ├── config.py
   └── ...
   ```

**⚠️ IMPORTANT:** Never commit `firebase_config.json` to GitHub! It contains sensitive credentials.

### Step 3: Update .gitignore

The `.gitignore` file already includes:
```
firebase_config.json
*.json
.env
```

---

## Firestore Database Configuration

### Step 1: Enable Firestore

1. In Firebase Console, go to **Firestore Database** (left menu)
2. Click **Create database**
3. Select **Start in test mode** (for development)
4. Choose location: **asia-south1** (India)
5. Click **Create**

### Step 2: Create Collections

Firestore will auto-create collections when you first add data. The app creates:

#### Collection: `users`
```
users/
├── {userId1}/
│   ├── id: "uuid-1"
│   ├── username: "admin"
│   ├── password_hash: "hash_value"
│   ├── role: "admin"
│   ├── last_login: "2026-01-20T14:30:00Z"
│   └── created_at: "2026-01-20T10:00:00Z"
├── {userId2}/
│   ├── id: "uuid-2"
│   ├── username: "user1"
│   ├── password_hash: "hash_value"
│   ├── role: "user"
│   ├── last_login: "2026-01-20T14:25:00Z"
│   └── created_at: "2026-01-20T10:15:00Z"
```

#### Collection: `articles`
```
articles/
├── {articleId1}/
│   ├── id: "uuid-1"
│   ├── article_name: "Summer Collection"
│   ├── mould: "MC-001"
│   ├── size: "L"
│   ├── gender: "male"
│   ├── created_by: "uuid-user-1"
│   ├── created_at: "2026-01-20T12:00:00Z"
│   ├── updated_at: "2026-01-20T12:00:00Z"
│   └── sync_status: 1
├── {articleId2}/
│   ├── id: "uuid-2"
│   ├── article_name: "Winter Collection"
│   ├── mould: "MC-002"
│   ├── size: "M"
│   ├── gender: "female"
│   ├── created_by: "uuid-user-1"
│   ├── created_at: "2026-01-20T13:00:00Z"
│   ├── updated_at: "2026-01-20T13:00:00Z"
│   └── sync_status: 1
```

---

## Authentication Setup

### Step 1: Enable Authentication

1. Go to **Authentication** in Firebase Console
2. Click **Get Started**
3. Enable these sign-in methods:
   - Email/Password
   - Anonymous (for testing)

### Step 2: Authentication in Application

The app uses `firebase_admin` SDK for backend authentication:

```python
# Located in: db/firebase_sync.py
from firebase_admin import auth

def authenticate_user(username, password):
    """Authenticate user with Firestore"""
    # Queries users collection
    # Verifies password hash
    # Returns user data if valid
```

---

## Firebase Integration

### File: `db/firebase_sync.py`

This is the main Firebase synchronization module:

```python
import firebase_admin
from firebase_admin import credentials, firestore, auth
import json
import os
from datetime import datetime
from utils.logger import Logger

class FirebaseSync:
    def __init__(self):
        self.logger = Logger(__name__)
        self.db = None
        self.auth = None
    
    def initialize(self):
        """Initialize Firebase"""
        try:
            # Load credentials from firebase_config.json
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'firebase_config.json'
            )
            
            cred = credentials.Certificate(config_path)
            firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.logger.info("Firebase initialized successfully")
        except Exception as e:
            self.logger.error(f"Firebase initialization failed: {e}")
            raise
    
    def sync_articles(self):
        """Sync articles to Firestore"""
        try:
            # Get all articles from local DB
            # Push to Firestore
            # Update sync_status
            pass
        except Exception as e:
            self.logger.error(f"Article sync failed: {e}")
    
    def sync_users(self):
        """Sync users to Firestore"""
        try:
            # Get all users from local DB
            # Push to Firestore (without passwords)
            # Update last_login
            pass
        except Exception as e:
            self.logger.error(f"User sync failed: {e}")
    
    def authenticate_user(self, username, password):
        """Authenticate user from Firestore"""
        try:
            # Query Firestore for user
            # Verify password
            # Return user data
            pass
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return None
```

### How Synchronization Works

1. **Offline-First Architecture:**
   - All data stored in SQLite locally
   - Changes saved to local DB immediately
   - Synced to Firebase when online

2. **Auto-Sync:**
   - Checks connection every 30 seconds
   - Syncs pending changes when online
   - No data loss in offline mode

3. **Conflict Resolution:**
   - Local data takes precedence
   - Last modified wins
   - Admin can force sync

---

## Security Rules

### Configure Firestore Security Rules

1. Go to **Firestore** → **Rules** tab
2. Replace with these rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Users collection
    match /users/{userId} {
      // Allow admins to read all users
      allow read: if request.auth != null && 
                     get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
      // Allow users to read their own data
      allow read: if request.auth.uid == userId;
      // Allow admins to write
      allow write: if get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
      // Allow creation during signup
      allow create: if request.auth != null;
    }
    
    // Articles collection
    match /articles/{articleId} {
      // Allow authenticated users to read
      allow read: if request.auth != null;
      // Allow creation by authenticated users
      allow create: if request.auth != null;
      // Allow admin to update/delete any
      allow update, delete: if get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
      // Allow users to update/delete own articles
      allow update, delete: if request.auth.uid == resource.data.created_by;
    }
  }
}
```

3. Click **Publish**

### Important Security Notes

⚠️ **Development Mode:**
- Current rules allow unrestricted read/write
- Use for development only
- Never use in production

⚠️ **Production Mode:**
- Use rules above for production
- Implement additional auth checks
- Enable API key restrictions

---

## Data Synchronization

### Manual Sync

Admin can trigger manual sync:

```python
# In admin dashboard
def sync_data(self):
    """Sync all data with Firebase"""
    try:
        # Sync articles
        self.firebase.sync_articles()
        # Sync users (metadata only, not passwords)
        self.firebase.sync_users()
        messagebox.showinfo("Success", "Data synchronized")
    except Exception as e:
        messagebox.showerror("Sync Error", str(e))
```

### Automatic Sync

The app auto-syncs every 30 seconds when online:

```python
# In main.py
def refresh_data(self):
    """Auto-sync every 30 seconds"""
    if self.network_checker.is_connected():
        try:
            self.firebase.sync_articles()
            self.firebase.sync_users()
        except:
            pass
    
    self.root.after(30000, self.refresh_data)  # 30 seconds
```

---

## Complete Setup Walkthrough

### Phase 1: Firebase Setup (5 minutes)

```bash
# 1. Create Firebase project in console
#    - Project name: NEXUZY_ARTICAL
#    - Region: asia-south1 (India)

# 2. Download service account key
#    - Console → Settings → Service Accounts
#    - Generate and download JSON

# 3. Place firebase_config.json in project root
cp ~/Downloads/nexuzy-artical-firebase-adminsdk.json ./firebase_config.json
```

### Phase 2: Local Setup (10 minutes)

```bash
# 1. Clone repository
git clone https://github.com/david0154/NEXUZY_ARTICAL.git
cd NEXUZY_ARTICAL

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place firebase_config.json (from Phase 1)
cp ~/Downloads/firebase_config.json .

# 4. Create assets (optional)
mkdir -p assets
# Add: logo.png, icon.ico

# 5. Test application
python main.py
```

### Phase 3: First Run (2 minutes)

```bash
# 1. Start application
python main.py

# 2. Register first admin user
#    - Username: admin
#    - Password: admin@123 (change later!)
#    - Role: Admin
#    - Click Register

# 3. Login
#    - Username: admin
#    - Password: admin@123

# 4. View dashboard
#    - Dashboard shows 0 users, 0 articles initially
```

### Phase 4: Create Test Data (5 minutes)

```bash
# As Admin user:

# 1. Create test article
#    - Article Name: "Test Article"
#    - Mould: "MC-001"
#    - Size: "L"
#    - Gender: "Male"

# 2. Create test user
#    - Username: "user1"
#    - Password: "user@123"
#    - Role: "User"

# 3. Check Firebase Console
#    - Firestore → articles collection
#    - Firestore → users collection
#    - Data should appear there

# 4. Logout and login as user1
#    - See limited dashboard
#    - View own articles only
```

---

## Troubleshooting

### Issue: "No module named 'firebase_admin'"

**Solution:**
```bash
pip install firebase-admin
```

### Issue: "firebase_config.json not found"

**Solution:**
1. Go to Firebase Console
2. Project Settings → Service Accounts
3. Generate New Private Key
4. Save as `firebase_config.json` in project root

### Issue: "Authentication failed"

**Solution:**
1. Check credentials in `firebase_config.json`
2. Verify Firestore is enabled
3. Check Security Rules allow the operation
4. Try offline mode (app works without Firebase)

### Issue: "Connection refused / Network error"

**Solution:**
- App automatically switches to offline mode
- All operations saved locally
- Data syncs when connection restored
- Check internet connection

### Issue: "Permission denied" in Firestore

**Solution:**
1. Check Security Rules in Firebase Console
2. Ensure rules match those provided above
3. Verify user is logged in
4. Check user role in Firestore data

### Issue: "Application won't start"

**Solution:**
```bash
# Run with detailed error output
python main.py

# Check logs
cat logs/nexuzy_artical_*.log

# Common issues:
# 1. Python 3.7+ required
# 2. Missing dependencies - run: pip install -r requirements.txt
# 3. Missing Tkinter - install: sudo apt-get install python3-tk
# 4. Missing assets - create assets/ folder with logo.png
```

---

## Environment Variables (Optional)

Create `.env` file for configuration:

```env
# Firebase
FIREBASE_CONFIG=firebase_config.json

# Application
APP_DEBUG=False
APP_LOG_LEVEL=INFO

# Sync
SYNC_INTERVAL=30
OFFLINE_MODE=True
```

Load in application:
```python
from dotenv import load_dotenv
import os

load_dotenv()
FIREBASE_CONFIG = os.getenv('FIREBASE_CONFIG', 'firebase_config.json')
```

---

## Production Deployment

### Before Going Live

1. **Update Security Rules**
   ```javascript
   // Change test mode to production rules
   // Implement strict access controls
   ```

2. **Set Environment Variables**
   ```bash
   export APP_DEBUG=False
   export SYNC_INTERVAL=60  # Increase sync interval
   ```

3. **Enable Backups**
   - Firebase Console → Backups
   - Schedule daily backups

4. **Monitor Usage**
   - Firebase Console → Usage
   - Set quotas to prevent abuse

5. **Enable Logging**
   ```python
   from utils.logger import Logger
   logger = Logger(__name__)
   logger.info("Production deployment initiated")
   ```

---

## API Reference

### FirebaseSync Class

**Initialization:**
```python
from db.firebase_sync import FirebaseSync

firebase = FirebaseSync()
firebase.initialize()  # Requires firebase_config.json
```

**Methods:**
```python
# Sync data
firebase.sync_articles()   # Push articles to Firestore
firebase.sync_users()      # Push users to Firestore

# Authentication
user = firebase.authenticate_user(username, password)

# User management
firebase.create_user(user_id, username, password, role)
firebase.update_user(user_id, data)
```

---

## Support & Contact

**Developer:** Manoj Konar  
**Email:** monoj@nexuzy.in  
**Company:** Nexuzy  
**Repository:** [NEXUZY_ARTICAL](https://github.com/david0154/NEXUZY_ARTICAL)  

---

**Last Updated:** January 20, 2026  
**Version:** 1.0.0
