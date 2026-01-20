# NEXUZY ARTICAL

> **Offline-First Python Tkinter Windows Application**  
> Admin + User Dashboard | Firebase + Local DB Sync  
> Developed by **Manoj Konar** | monoj@nexuzy.in  
> **Nexuzy** © 2026

---

## 🎯 Overview

**NEXUZY ARTICAL** is a complete, production-ready application for managing articles with:

- ✅ **Offline-First Architecture** - Works without internet, syncs when online
- ✅ **Role-Based Access** - Admin and User permissions
- ✅ **Real-Time Sync** - Firebase Firestore integration
- ✅ **Secure Authentication** - PBKDF2-SHA256 password hashing
- ✅ **Windows Application** - PyInstaller + Inno Setup for distribution
- ✅ **Professional UI** - Modern Tkinter interface
- ✅ **Complete Logging** - Audit trail and error tracking

---

## 📋 Features

### Admin Features
- ✅ Add, Edit, Delete Articles
- ✅ Create New Users
- ✅ View All Articles and Users
- ✅ Force Manual Sync
- ✅ View Sync Status
- ✅ Analytics Dashboard

### User Features
- ✅ Add Articles
- ✅ View All Articles
- ✅ Automatic Sync (Offline Queue)
- ✅ Internet Status Indicator
- ✅ Quick Actions

### Technical Features
- ✅ SQLite Local Database
- ✅ Firebase Firestore Cloud Storage
- ✅ Automatic Offline-Online Detection
- ✅ Intelligent Sync Engine
- ✅ Security Rules & Custom Claims
- ✅ Comprehensive Error Handling
- ✅ Detailed Application Logs

---

## 📊 Data Fields

**ARTICLE:**
- Article ID (Auto-generated UUID)
- Article Name
- Mould
- Size (XS, S, M, L, XL, XXL, Free)
- Gender (Male, Female, Unisex)
- Created By (User ID)
- Created At (Timestamp)
- Last Updated (Timestamp)
- Sync Status (Pending/Synced)

---

## 🗂️ Project Structure

```
NEXUZY_ARTICAL/
├── main.py                      # Entry point
├── config.py                    # Global configuration
├── requirements.txt             # Dependencies
├── firebase_config.json         # Firebase credentials (YOUR OWN)
├── inno_setup.iss              # Windows installer
├── README.md                    # This file
│
├── auth/
│   ├── __init__.py
│   └── login.py               # Login Screen
│
├── dashboard/
│   ├── __init__.py
│   ├── admin_dashboard.py     # Admin Panel
│   ├── user_dashboard.py      # User Panel
│   └── widgets.py             # Custom Widgets
│
├── db/
│   ├── __init__.py
│   ├── models.py              # Data Models
│   ├── local_db.py            # SQLite Manager
│   └── firebase_sync.py       # Cloud Sync
│
├── utils/
│   ├── __init__.py
│   ├── constants.py           # Constants
│   ├── network.py             # Internet Check
│   ├── security.py            # Password Hashing
│   └── logger.py              # Logging Setup
│
├── assets/
│   ├── logo.png               # Logo (256x256)
│   ├── logo.ico               # Windows Icon
│   └── icon.ico               # EXE Icon
│
└── build/
    └── build.py               # Build Script
```

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/david0154/NEXUZY_ARTICAL.git
cd NEXUZY_ARTICAL
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Firebase

1. Go to [Firebase Console](https://firebase.google.com)
2. Create a new project
3. Enable Firestore Database (Start in test mode)
4. Download Service Account Key (JSON)
5. Save as `firebase_config.json` in project root

### 4. Initialize Database

```bash
python -c "from db.local_db import LocalDatabase; db = LocalDatabase(); print('Database initialized')"
```

### 5. Create Admin User (Optional)

The app will create tables automatically. Run and use login screen.

### 6. Run Application

```bash
python main.py
```

---

## 🔐 Firebase Setup

### Create Firestore Collections

**Manual Setup (if auto-creation fails):**

```javascript
// Firestore Rules (Important!)
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.role == "admin";
    }
    match /articles/{articleId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null;
      allow update, delete: if request.auth.token.role == "admin";
    }
  }
}
```

---

## 👤 Test Users

Create these users for testing:

| Username | Password | Role |
|----------|----------|------|
| admin | admin@123 | admin |
| user1 | user@123 | user |

**How to create:**
1. Run `python main.py`
2. Admin creates users via "Add User" in admin panel
3. Users login with their credentials

---

## 🔄 How Sync Works

```
App Starts
    ↓
Check Internet Connection
    ├→ ONLINE: Sync pending data to Firebase
    │          Download latest from cloud
    └→ OFFLINE: Queue changes locally in SQLite
    ↓
User Creates/Updates Article
    ↓
Save to SQLite (mark as pending)
    ↓
Auto-sync every 30 seconds if online
    ↓
Once synced, mark as "synced" in local DB
```

**Manual Sync:** Admin can force sync via "Force Sync" button

---

## 🏗️ Build & Package

### Build EXE with PyInstaller

```bash
# Single file executable
pyinstaller --onefile --windowed --icon=assets/icon.ico --name="NEXUZY_ARTICAL" main.py

# Output: dist/NEXUZY_ARTICAL.exe
```

### Create Windows Installer (Inno Setup)

1. Download [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Open `inno_setup.iss`
3. Compile → Creates installer EXE
4. Share installer for deployment

### Automated Build

```bash
python build/build.py
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# UI Dimensions
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

# Network Sync
SYNC_INTERVAL_SECONDS = 30

# Security
PASSWORD_MIN_LENGTH = 6
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 300

# Colors
PRIMARY_COLOR = "#1f77d4"
ERROR_COLOR = "#e74c3c"
SUCCESS_COLOR = "#27ae60"
```

---

## 🛠️ Troubleshooting

### "Firebase config not found"
- **Solution:** Ensure `firebase_config.json` exists in project root

### "No internet connection" message
- **Solution:** App is in offline mode (expected). Changes will sync when online.

### "Database locked" error
- **Solution:** Close other instances of the app running

### EXE won't start
- **Solution:** Run from Command Prompt to see detailed error
  ```bash
  NEXUZY_ARTICAL.exe
  ```

### Sync not working
- **Checklist:**
  - [ ] Firebase config is valid
  - [ ] Internet connection available
  - [ ] Firebase Firestore rules are set correctly
  - [ ] Check logs in `logs/` folder

---

## 📝 Logging

Logs are stored in `logs/` folder:

```
logs/
├── nexuzy_artical_2026-01-20.log
├── nexuzy_artical_2026-01-21.log
└── ...
```

**View logs:**
```bash
tail -f logs/nexuzy_artical_*.log
```

---

## 🔒 Security

### Password Security
- ✅ PBKDF2-SHA256 hashing
- ✅ Minimum 6 characters
- ✅ Letters + Numbers required
- ✅ Never stored as plain text

### Firebase Security
- ✅ Custom Claims for admin verification
- ✅ Firestore Rules enforcement
- ✅ Read/Write access control

### Local Security
- ✅ SQLite in user data folder
- ✅ Separate logs directory
- ✅ No credentials in logs

---

## 📱 System Requirements

- **OS:** Windows 7+
- **Python:** 3.8+
- **RAM:** 512MB minimum
- **Disk:** 100MB (with all dependencies)
- **Internet:** For sync (optional)

---

## 🐛 Bug Reports

Found a bug? Report it:
- **Email:** monoj@nexuzy.in
- **GitHub:** Issues on repository
- **Include:** 
  - Steps to reproduce
  - Error message
  - Log files

---

## 📚 Documentation

- **[Complete Implementation Guide](./docs/IMPLEMENTATION.md)**
- **[Database Schema](./docs/DATABASE.md)**
- **[Firebase Setup Guide](./docs/FIREBASE.md)**
- **[Build & Deployment](./docs/BUILD.md)**

---

## 📞 Support

**Developer:** Manoj Konar  
**Email:** monoj@nexuzy.in  
**Company:** Nexuzy  
**Website:** nexuzy.in  
**GitHub:** [github.com/david0154/NEXUZY_ARTICAL](https://github.com/david0154/NEXUZY_ARTICAL)

---

## 📄 Version History

### v1.0.0 (January 2026)
- ✅ Initial Release
- ✅ Offline-First Architecture
- ✅ Firebase Sync
- ✅ Admin/User Roles
- ✅ Windows Installer
- ✅ Complete Documentation

---

## 📜 License

Proprietary - Nexuzy © 2026  
All Rights Reserved

---

## 🎉 Thank You!

Thank you for using **NEXUZY ARTICAL**!  
For questions or suggestions, reach out to **monoj@nexuzy.in**

**Happy Coding! 🚀**
