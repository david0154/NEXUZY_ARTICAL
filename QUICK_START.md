# 🚀 NEXUZY ARTICAL - Quick Start Guide

**Get NEXUZY ARTICAL running in 10 minutes!**

---

## 📋 Prerequisites

- Python 3.7 or higher
- Git
- Internet connection (for Firebase setup)
- Windows, Mac, or Linux

### Check Python Version
```bash
python --version
# Should show Python 3.7 or higher
```

---

## ⚡ 5-Minute Setup

### 1️⃣ Clone Repository (1 min)
```bash
git clone https://github.com/david0154/NEXUZY_ARTICAL.git
cd NEXUZY_ARTICAL
```

### 2️⃣ Install Dependencies (2 min)
```bash
pip install -r requirements.txt
```

**Troubleshooting:**
- On Linux/Mac, use: `pip3 install -r requirements.txt`
- If `pip` not found, install from: https://www.python.org/downloads/

### 3️⃣ Firebase Setup (CRITICAL - 5 min)

#### A. Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **Add Project** → Name it `NEXUZY_ARTICAL`
3. Enable Google Analytics (optional)
4. Create project

#### B. Download Service Account Key
1. Click **Settings** ⚙️ (top-left)
2. Go to **Service Accounts** tab
3. Click **Generate New Private Key**
4. Save the JSON file

#### C. Place in Project
```bash
# Copy downloaded file to project root
cp ~/Downloads/nexuzy-artical-*.json ./firebase_config.json

# Verify it's there
ls firebase_config.json
```

**⚠️ Important:** Never push `firebase_config.json` to GitHub!

### 4️⃣ Run Application (1 min)
```bash
python main.py
```

✅ **Done!** The application should open.

---

## 🔐 Create First Account

1. **First Launch:** Click **Create New Account**
2. **Fill Form:**
   - Username: `admin`
   - Password: `admin@123` (change later!)
   - Role: Select **Admin**
3. **Click Register**
4. **Login** with credentials above

---

## 📝 Create Test Data

### Create Article
1. Click **📄 Articles** in sidebar
2. Click **+ Add New Article**
3. Fill form:
   - Article Name: `Test Item`
   - Mould: `M-001`
   - Size: `Large`
   - Gender: `Male`
4. Click **Save**

✅ Article appears in list and Firebase!

### Create Test User
1. Click **👥 Users** in sidebar
2. Click **+ Add New User**
3. Fill form:
   - Username: `user1`
   - Password: `user@123`
   - Role: Select **User**
4. Click **Create User**

---

## 🔍 Verify Firebase Sync

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Open your project: `NEXUZY_ARTICAL`
3. Click **Firestore Database** (left menu)
4. Check collections:
   - ✅ `articles` - Should have your test article
   - ✅ `users` - Should have admin and user1

---

## 🛠️ Project Structure

```
NEXUZY_ARTICAL/
├── main.py                 ← Run this!
├── config.py              ← Configuration
├── requirements.txt       ← Dependencies
├── firebase_config.json   ← Firebase credentials
├── .gitignore            ← Git ignore rules
├── README.md             ← Full documentation
├── FIREBASE_SETUP.md     ← Firebase guide
│
├── auth/
│   ├── __init__.py
│   └── login.py         ← Login & Register screens
│
├── dashboard/
│   ├── __init__.py
│   ├── admin_dashboard.py    ← Admin panel
│   └── user_dashboard.py     ← User panel
│
├── db/
│   ├── __init__.py
│   ├── models.py             ← Data models
│   ├── local_db.py           ← SQLite database
│   └── firebase_sync.py      ← Cloud sync
│
├── utils/
│   ├── __init__.py
│   ├── security.py           ← Password hashing
│   ├── network.py            ← Internet check
│   ├── logger.py             ← Logging
│   └── constants.py          ← App constants
│
├── build/
│   ├── __init__.py
│   └── build.py              ← Build EXE
│
├── assets/
│   ├── logo.png          ← Add your logo
│   └── icon.ico          ← App icon
│
├── data/
│   └── nexuzy_artical.db ← Created at runtime
│
└── logs/
    └── nexuzy_artical_*.log ← Debug logs
```

---

## 🎯 Key Features

✅ **Offline-First**
- Works completely offline
- Syncs when online
- No data loss

✅ **Role-Based Access**
- Admin: Full control
- User: Limited access
- Secure authentication

✅ **Cloud Sync**
- Firebase Firestore integration
- Real-time updates
- Automatic backup

✅ **Professional UI**
- Modern Tkinter interface
- Easy navigation
- Admin & user dashboards

---

## ⚠️ Common Issues & Solutions

### "ModuleNotFoundError: No module named 'firebase_admin'"
```bash
pip install firebase-admin
```

### "firebase_config.json not found"
- Download from Firebase Console
- Place in project root as `firebase_config.json`
- See **Firebase Setup** section above

### "Connection refused / Network error"
- App works offline!
- Check internet connection
- Data syncs when online

### "Application won't start"
```bash
# See error messages
python main.py

# Missing Tkinter (Linux)?
sudo apt-get install python3-tk
```

### "No module named Tkinter" (Linux)
```bash
sudo apt-get install python3-tk
```

---

## 🚀 Next Steps

1. ✅ **Test Application**
   - Create articles
   - Create users
   - Switch roles

2. ✅ **Explore Features**
   - Admin dashboard
   - User dashboard  
   - Sync status
   - Settings

3. ✅ **Read Full Docs**
   - [README.md](README.md) - Complete guide
   - [FIREBASE_SETUP.md](FIREBASE_SETUP.md) - Firebase details

4. ✅ **Deploy**
   - Build EXE: `python build/build.py`
   - Create installer
   - Distribute

---

## 📞 Support

**Issues?**
1. Check troubleshooting above
2. Read [README.md](README.md)
3. Check logs: `cat logs/nexuzy_artical_*.log`
4. Email: monoj@nexuzy.in

**GitHub:**
- Repository: [NEXUZY_ARTICAL](https://github.com/david0154/NEXUZY_ARTICAL)
- Issues: [GitHub Issues](https://github.com/david0154/NEXUZY_ARTICAL/issues)

---

## 🎓 Learn More

- **Firebase:** https://firebase.google.com/docs
- **Python Tkinter:** https://docs.python.org/3/library/tkinter.html
- **SQLite:** https://www.sqlite.org/docs.html
- **PyInstaller:** https://pyinstaller.readthedocs.io/

---

**Happy coding! 🚀**

*Last updated: January 20, 2026*
