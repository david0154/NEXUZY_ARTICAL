# NEXUZY ARTICAL - Article Management System

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📝 About

**NEXUZY ARTICAL** is an offline-first article management system built with Python and Tkinter, designed for manufacturing and inventory tracking. It provides a robust desktop application for creating, managing, and syncing articles with Firebase backend support.

### Key Features

✅ **Offline-First Architecture** - Works seamlessly without internet connection  
✅ **User Authentication** - Secure login with role-based access (Admin/User)  
✅ **Remember Me** - Auto-fill saved credentials on next login  
✅ **Article Management** - Create, view, edit, and delete articles  
✅ **Unique Article IDs** - Auto-generated `Fides-XXXXXX` identifiers  
✅ **Image Support** - Attach images to articles with built-in picker  
✅ **Username Display** - Shows logged-in user in dashboard header  
✅ **Full Scrollbar Support** - Smooth mouse wheel and keyboard navigation  
✅ **Firebase Sync** - Automatic cloud synchronization when online  
✅ **Export Functionality** - Export articles to Excel/PDF formats  
✅ **Admin Dashboard** - Full CRUD operations for administrators  
✅ **User Dashboard** - Limited create-only access for regular users  

---

## 🛠️ Technology Stack

- **Language:** Python 3.8+
- **GUI Framework:** Tkinter with ttk widgets
- **Database:** SQLite (local), Firebase Firestore (cloud)
- **Image Processing:** Pillow (PIL)
- **Build Tool:** PyInstaller
- **Export:** openpyxl (Excel), reportlab (PDF)

---

## 💾 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone the repository**

```bash
git clone https://github.com/david0154/NEXUZY_ARTICAL.git
cd NEXUZY_ARTICAL
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure Firebase (Optional for cloud sync)**

Create `firebase_config.json` in the project root:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "your-cert-url"
}
```

4. **Run the application**

```bash
python main.py
```

---

## 📦 Building Executable

Create a standalone `.exe` file for distribution:

```bash
python build/build.py
```

The executable will be created in the `dist/` folder.

### Manual Build (Alternative)

```bash
pyinstaller --onefile --windowed --name=NEXUZY_ARTICAL \
  --add-data="assets:assets" \
  --add-data="config:config" \
  --hidden-import=firebase_admin \
  --hidden-import=PIL._tkinter_finder \
  --icon=assets/icon.ico \
  main.py
```

---

## 🚀 Usage

### First Launch

1. Run the application (`main.py` or `.exe`)
2. Login screen will appear
3. Enter username and password
4. Check **Remember Me** to save credentials
5. Default admin credentials are set by admin during initial setup

### User Roles

#### **Admin**
- Create, edit, and delete articles
- Manage users
- Export data to Excel/PDF
- Full system access

#### **User**
- Create new articles
- View own articles
- Share articles
- Read-only access to others' articles

### Creating Articles

1. Click **"+ Create New Article"** or **"+ Add New Article"**
2. Fill in the form:
   - **Article Name** - Product/article name
   - **Mould** - Manufacturing mould type
   - **Size** - Article size
   - **Gender** - Target gender category
3. Click **"📷 Select Image"** to attach an image (optional)
4. Auto-generated **Fides-XXXXXX** ID is displayed
5. **Created by** shows your username
6. Click **"Save Article"**

### Remember Me Feature

- Check **"Remember Me"** checkbox before login
- Credentials are encrypted and saved locally
- Next time you open the app, username and password will be auto-filled
- Uncheck to clear saved credentials

### Article ID System

Each article gets a unique identifier:
- Format: `Fides-XXXXXX`
- X = Random uppercase letter or digit (A-Z, 0-9)
- Example: `Fides-A7K9M2`, `Fides-X3P1Q8`
- Guaranteed uniqueness check before creation

---

## 📁 Project Structure

```
NEXUZY_ARTICAL/
├── assets/              # Images, icons, and static files
│   ├── logo.png        # Application logo (shown in login)
│   └── icon.ico        # Application icon
├── auth/               # Authentication modules
│   ├── login.py        # Login screen with Remember Me
│   └── register.py     # (Disabled - admin-only user creation)
├── build/              # Build scripts
│   └── build.py        # PyInstaller build automation
├── config/             # Configuration files
│   ├── __init__.py     # App settings and constants
│   └── saved_credentials.json  # Saved login credentials
├── dashboard/          # Dashboard modules
│   ├── admin_dashboard.py   # Admin panel
│   └── user_dashboard.py    # User panel (with article ID gen)
├── db/                 # Database modules
│   ├── local_db.py     # SQLite operations
│   ├── firebase_db.py  # Firebase operations
│   └── models.py       # Data models
├── utils/              # Utility modules
│   ├── security.py     # Password hashing
│   ├── network.py      # Network connectivity check
│   └── logger.py       # Logging configuration
├── data/               # Generated at runtime
│   └── fides.db        # Local SQLite database
├── logs/               # Application logs
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🔧 Development

### Running in Development Mode

```bash
python main.py
```

### Database Schema

**Users Table:**
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Articles Table:**
```sql
CREATE TABLE articles (
    id TEXT PRIMARY KEY,              -- Fides-XXXXXX format
    article_name TEXT NOT NULL,
    mould TEXT NOT NULL,
    size TEXT NOT NULL,
    gender TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sync_status INTEGER DEFAULT 0,
    image_path TEXT,                  -- Path to attached image
    FOREIGN KEY(created_by) REFERENCES users(id)
);
```

---

## ✨ Recent Updates (v2.0)

✅ **Login Enhancements**
- Added **Remember Me** checkbox
- Auto-fill saved username and password
- Encrypted credential storage
- Logo display from `assets/logo.png`
- Full scrollbar support with mouse wheel
- Keyboard navigation (Tab, Enter keys)

✅ **Article Creation Improvements**
- Auto-generated **Fides-XXXXXX** unique IDs
- Image picker with file browser
- Display selected image filename
- Show **Created by** username in form
- Image path stored in database

✅ **Dashboard Enhancements**
- Username displayed in header: **"Welcome, [username] 👤"**
- Full scrollbar support in all views
- Article ID column in list views
- Improved UI/UX with emojis

✅ **Build System**
- Comprehensive dependency collection
- Hidden imports for all modules
- Proper asset packaging
- Optimized executable size
- Detailed build verification

---

## 🐛 Known Issues

- Firebase sync requires valid `firebase_config.json`
- First launch may take a few seconds to initialize database
- Large images (>5MB) may slow down the UI

---

## 🛣️ Roadmap

- [ ] Bulk article import from CSV/Excel
- [ ] Advanced search and filtering
- [ ] Article templates
- [ ] Multi-language support
- [ ] Mobile companion app
- [ ] Barcode/QR code generation
- [ ] Print labels directly from app

---

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

**Developer:** Manoj Konar  
**Email:** monoj@nexuzy.in  
**Company:** Nexuzy Tech Pvt Ltd  
**Location:** Kolkata, India  
**GitHub:** [@david0154](https://github.com/david0154)  

---

## 👏 Acknowledgments

- Firebase for cloud database services
- Python community for excellent libraries
- Tkinter for cross-platform GUI framework
- All contributors and testers

---

**Built with ❤️ by Nexuzy Tech**
