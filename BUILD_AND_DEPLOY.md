# Complete Build & Deployment Guide

## 📦 Overview

This guide covers the **complete process** from source code to distributable installer.

---

## 🛠️ Prerequisites

### Required Software

1. **Python 3.8+**
   ```bash
   python --version
   ```

2. **PyInstaller**
   ```bash
   pip install pyinstaller
   ```

3. **Inno Setup** (for Windows installer)
   - Download: [https://jrsoftware.org/isdl.php](https://jrsoftware.org/isdl.php)
   - Install to default location

### Required Files

```
NEXUZY_ARTICAL/
├── assets/
│   ├── logo.png              ✅ Required
│   └── icon.ico              ✅ Required
├── config/                   ✅ Required (empty folder OK)
├── firebase_config.json.example  ✅ Required (template)
├── ftp_config.json.example       ✅ Required (template)
├── build/build.py            ✅ Required
├── inno_setup.iss            ✅ Required
└── main.py                   ✅ Required
```

---

## 📝 Step 1: Prepare Configuration Templates

### 1.1 Firebase Config Template

**File:** `firebase_config.json.example`

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

### 1.2 FTP Config Template

**File:** `ftp_config.json.example`

```json
{
  "host": "ftp.yourdomain.com",
  "username": "your_ftp_username",
  "password": "your_ftp_password",
  "remote_dir": "/public_html/articles/images",
  "base_url": "https://yourdomain.com/articles/images",
  "timeout": 30,
  "passive_mode": true
}
```

### 1.3 Create Assets

**Logo (logo.png):**
- Size: 256x256 pixels minimum
- Format: PNG with transparency
- Location: `assets/logo.png`

**Icon (icon.ico):**
- Size: 256x256 pixels
- Format: ICO (use online converter if needed)
- Location: `assets/icon.ico`

**Tools for creating ICO:**
- [ConvertICO](https://convertico.com/)
- [ICO Convert](https://icoconvert.com/)

---

## 🔨 Step 2: Build Executable

### 2.1 Install Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2.2 Run Build Script

```bash
cd NEXUZY_ARTICAL
python build/build.py
```

**What happens:**

1. ✅ Checks prerequisites
2. 🗑️ Cleans previous builds
3. 📦 Runs PyInstaller with optimizations
4. 📷 Includes assets (logo.png, icon.ico)
5. 📄 Includes config templates
6. ✅ Verifies build
7. 💾 Copies templates to dist folder

### 2.3 Build Output

```
dist/
├── NEXUZY_ARTICAL.exe          ✅ Main executable
├── firebase_config.json.example ✅ Config template
└── ftp_config.json.example      ✅ Config template
```

### 2.4 Test Executable

```bash
cd dist
.\NEXUZY_ARTICAL.exe
```

**Test checklist:**

- [ ] Application launches
- [ ] Login screen appears
- [ ] Can login with default admin (david / 784577)
- [ ] Dashboard loads
- [ ] Can create article (without image first)
- [ ] Application closes properly

---

## 📚 Step 3: Configure for Distribution

### 3.1 Create Actual Configs (Optional)

For pre-configured distribution:

```bash
cd dist
cp firebase_config.json.example firebase_config.json
cp ftp_config.json.example ftp_config.json

# Edit with real credentials
notepad firebase_config.json
notepad ftp_config.json
```

**Warning:** Only include real configs for internal/trusted distribution!

### 3.2 Add Documentation

Copy to `dist/` folder:

```bash
cp README.md dist/
cp FIXES.md dist/
cp SYNC_GUIDE.md dist/
cp FIREBASE_SETUP.md dist/
cp QUICK_START.md dist/
```

---

## 📦 Step 4: Create Installer (Inno Setup)

### 4.1 Verify Inno Setup Script

**File:** `inno_setup.iss`

Key settings:

```ini
AppName=NEXUZY ARTICAL
AppVersion=2.1
DefaultDirName={autopf}\NEXUZY ARTICAL
OutputDir=installer_output
OutputBaseFilename=NEXUZY_ARTICAL_Setup_v2.1
SetupIconFile=assets\icon.ico
```

### 4.2 Build Installer

**Method 1: GUI**

1. Open Inno Setup Compiler
2. File → Open: `inno_setup.iss`
3. Build → Compile
4. Wait for completion

**Method 2: Command Line**

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" inno_setup.iss
```

### 4.3 Installer Output

```
installer_output/
└── NEXUZY_ARTICAL_Setup_v2.1.exe  ✅ Final installer
```

**Installer includes:**

- ✅ NEXUZY_ARTICAL.exe
- ✅ firebase_config.json.example
- ✅ ftp_config.json.example
- ✅ assets/ folder (logo, icon)
- ✅ config/ folder (for saved configs)
- ✅ All documentation (README, FIXES, SYNC_GUIDE, etc.)
- ✅ Desktop shortcut (optional)
- ✅ Start menu entry
- ✅ Uninstaller

### 4.4 Test Installer

1. **Run installer:**
   ```bash
   .\installer_output\NEXUZY_ARTICAL_Setup_v2.1.exe
   ```

2. **Follow installation:**
   - Accept license
   - Choose install location
   - Create desktop shortcut (optional)
   - Install

3. **Verify installation:**
   ```
   C:\Program Files\NEXUZY ARTICAL\
   ├── NEXUZY_ARTICAL.exe
   ├── firebase_config.json.example
   ├── ftp_config.json.example
   ├── FIRST_RUN.txt
   ├── README.md
   ├── FIXES.md
   ├── assets\
   └── config\
   ```

4. **Test installed app:**
   - Launch from desktop shortcut
   - Or from Start menu
   - Verify it runs correctly

---

## 🚀 Step 5: Post-Installation Configuration

### 5.1 First-Time User Setup

**User receives installer and installs. Now they configure:**

1. **Navigate to install folder:**
   ```
   C:\Program Files\NEXUZY ARTICAL
   ```

2. **Configure Firebase (optional):**
   ```bash
   # Copy template
   copy firebase_config.json.example firebase_config.json
   
   # Edit with Firebase credentials
   notepad firebase_config.json
   ```

3. **Configure FTP (optional):**
   ```bash
   # Copy template
   copy ftp_config.json.example ftp_config.json
   
   # Edit with FTP credentials
   notepad ftp_config.json
   ```

4. **Launch application:**
   - Double-click NEXUZY_ARTICAL.exe
   - Or use desktop shortcut

5. **First login:**
   - Username: `david`
   - Password: `784577`
   - Role: Admin

### 5.2 What Happens on First Run

**With Firebase configured:**

```
1. App starts
2. Checks for firebase_config.json ✅ Found
3. Connects to Firebase
4. Downloads existing articles from cloud
5. Downloads existing users from cloud
6. Imports to local database
7. Shows sync complete message
8. Login screen appears
```

**Without Firebase configured:**

```
1. App starts
2. Checks for firebase_config.json ❌ Not found
3. Runs in offline mode
4. Creates empty local database
5. Login screen appears
6. User can add configs later
```

---

## 📤 Step 6: Distribution

### 6.1 Package Contents

Create distribution package:

```
NEXUZY_ARTICAL_v2.1/
├── NEXUZY_ARTICAL_Setup_v2.1.exe   ✅ Installer
├── README.txt                      ✅ Quick start
├── FIREBASE_SETUP_GUIDE.pdf        ✅ Setup guide
└── RELEASE_NOTES.txt               ✅ What's new
```

### 6.2 Create README.txt

```txt
NEXUZY ARTICAL v2.1 - Installation Instructions
================================================

1. Run NEXUZY_ARTICAL_Setup_v2.1.exe
2. Follow installation wizard
3. After installation, configure:
   - firebase_config.json (for cloud sync)
   - ftp_config.json (for image upload)
4. Launch application from desktop
5. Default login: david / 784577

For detailed setup: See FIREBASE_SETUP_GUIDE.pdf

Support: monoj@nexuzy.in
GitHub: github.com/david0154/NEXUZY_ARTICAL
```

### 6.3 Distribution Methods

**Option 1: Direct Download**
```bash
# Create ZIP
zip -r NEXUZY_ARTICAL_v2.1.zip NEXUZY_ARTICAL_v2.1/

# Upload to:
- Google Drive
- Dropbox
- Your website
```

**Option 2: GitHub Releases**
```bash
# Create release on GitHub
1. Go to repository
2. Releases → Create new release
3. Tag: v2.1
4. Upload NEXUZY_ARTICAL_Setup_v2.1.exe
5. Add release notes
6. Publish
```

**Option 3: USB Drive**
```bash
# Copy to USB
cp -r NEXUZY_ARTICAL_v2.1/ /media/usb/
```

---

## ✅ Complete Checklist

### Pre-Build

- [ ] All source code committed to Git
- [ ] `requirements.txt` up to date
- [ ] `assets/logo.png` exists
- [ ] `assets/icon.ico` exists
- [ ] `firebase_config.json.example` created
- [ ] `ftp_config.json.example` created
- [ ] Version number updated in `config.py`

### Build

- [ ] Dependencies installed
- [ ] `python build/build.py` runs successfully
- [ ] `dist/NEXUZY_ARTICAL.exe` created
- [ ] Config templates copied to dist/
- [ ] Executable tested and working

### Installer

- [ ] Inno Setup installed
- [ ] `inno_setup.iss` configured
- [ ] Installer compiled successfully
- [ ] `NEXUZY_ARTICAL_Setup_v2.1.exe` created
- [ ] Installer tested on clean system
- [ ] Uninstaller tested

### Distribution

- [ ] Distribution package created
- [ ] README.txt written
- [ ] Setup guide included
- [ ] Release notes written
- [ ] Package zipped/uploaded
- [ ] Download link shared

---

## 🐛 Troubleshooting

### Build fails with "Module not found"

**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

### Icon not appearing in EXE

**Solution:**
```bash
# Verify icon exists
ls assets/icon.ico

# Rebuild with --clean
python build/build.py
```

### Installer fails to compile

**Solution:**
```bash
# Check Inno Setup path
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" --help

# Verify all paths in .iss file are correct
```

### Config templates missing in installer

**Solution:**
```bash
# Verify files exist in dist/
ls dist/*.example

# Check inno_setup.iss [Files] section
# Should include:
Source: "dist\firebase_config.json.example"; ...
Source: "dist\ftp_config.json.example"; ...
```

### App crashes on startup

**Solution:**
```bash
# Run from command line to see errors
cd dist
.\NEXUZY_ARTICAL.exe

# Check logs
type logs\app.log
```

---

## 📚 Additional Resources

- **PyInstaller Docs:** [https://pyinstaller.org/](https://pyinstaller.org/)
- **Inno Setup Docs:** [https://jrsoftware.org/ishelp/](https://jrsoftware.org/ishelp/)
- **Firebase Setup:** [FIREBASE_SETUP.md](FIREBASE_SETUP.md)
- **Sync Guide:** [SYNC_GUIDE.md](SYNC_GUIDE.md)

---

**Questions or Issues?**

Email: monoj@nexuzy.in  
GitHub Issues: [github.com/david0154/NEXUZY_ARTICAL/issues](https://github.com/david0154/NEXUZY_ARTICAL/issues)
