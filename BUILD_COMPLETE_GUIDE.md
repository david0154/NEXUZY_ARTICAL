# NEXUZY ARTICAL - Complete Build & Deploy Guide

## Overview

This guide covers building a complete installer with **ALL** files included:
- ✅ Main executable (NEXUZY_ARTICAL.exe)
- ✅ Logo (assets/logo.png)
- ✅ Icon (assets/icon.ico)
- ✅ Firebase config template (firebase_config.json.example)
- ✅ FTP config template (ftp_config.json.example)
- ✅ All documentation
- ✅ Config folder structure
- ✅ Image cache folder

---

## Prerequisites

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Install Inno Setup (Windows)
- Download from: https://jrsoftware.org/isdl.php
- Install with default settings
- Add to PATH (optional but recommended)

### 3. Prepare Assets

Ensure you have:
```
assets/
  ├── logo.png        # App logo (PNG format)
  └── icon.ico        # App icon (ICO format)
```

If missing, create placeholders or use default Windows icons.

---

## Step 1: Build Executable with PyInstaller

### Quick Build
```bash
python build/build.py
```

This script:
1. ✅ Checks all prerequisites
2. ✅ Cleans previous builds
3. ✅ Bundles ALL config files
4. ✅ Includes logo and icon
5. ✅ Copies documentation
6. ✅ Creates folder structure
7. ✅ Generates SETUP_INSTRUCTIONS.txt

### Build Output
```
dist/
  ├── NEXUZY_ARTICAL.exe              # Main executable
  ├── firebase_config.json.example     # Firebase template
  ├── ftp_config.json.example          # FTP template
  ├── SETUP_INSTRUCTIONS.txt           # User guide
  ├── README.md                        # Project readme
  ├── QUICK_START.md                   # Quick start guide
  ├── FIREBASE_SETUP.md                # Firebase guide
  ├── FTP_SETUP.md                     # FTP guide
  ├── data/                            # Database folder
  ├── logs/                            # Logs folder
  └── image_cache/                     # Image cache folder
```

### Manual Build (Alternative)
```bash
pyinstaller --onefile --windowed \
  --name=NEXUZY_ARTICAL \
  --icon=assets/icon.ico \
  --add-data="assets:assets" \
  --add-data="config:config" \
  --add-data="firebase_config.json.example:." \
  --add-data="ftp_config.json.example:." \
  --hidden-import=firebase_admin \
  --hidden-import=PIL \
  --hidden-import=tkinter \
  --collect-all=firebase_admin \
  --collect-all=PIL \
  main.py
```

---

## Step 2: Test the Executable

### Before Creating Installer

1. **Test basic run:**
   ```bash
   cd dist
   .\NEXUZY_ARTICAL.exe
   ```

2. **Test without configs:**
   - App should start in offline mode
   - Local database should work
   - No Firebase/FTP errors

3. **Test with configs:**
   - Rename `firebase_config.json.example` → `firebase_config.json`
   - Rename `ftp_config.json.example` → `ftp_config.json`
   - Add your credentials
   - Test Firebase sync
   - Test FTP image upload

4. **Test features:**
   - ✅ User login
   - ✅ Article creation
   - ✅ Image upload (if FTP configured)
   - ✅ Image preview
   - ✅ Export to PDF/Excel
   - ✅ User management (admin)

---

## Step 3: Create Installer with Inno Setup

### Using Inno Setup GUI

1. **Open Inno Setup:**
   - Launch "Inno Setup Compiler"

2. **Open script:**
   - File → Open → Select `inno_setup.iss`

3. **Compile:**
   - Build → Compile
   - Or press `Ctrl + F9`

4. **Wait for completion:**
   - Progress shows in bottom panel
   - Success message appears when done

5. **Find installer:**
   ```
   installer_output/
     └── NEXUZY_ARTICAL_Setup_v2.1.exe
   ```

### Using Command Line

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" inno_setup.iss
```

### Installer Includes:

✅ **Files:**
- NEXUZY_ARTICAL.exe
- firebase_config.json.example
- ftp_config.json.example
- All assets (logo.png, icon.ico)
- All documentation (*.md files)
- SETUP_INSTRUCTIONS.txt

✅ **Folders Created:**
- data/ (with full permissions)
- logs/ (with full permissions)
- config/ (with full permissions)
- assets/ (with full permissions)
- image_cache/ (with full permissions)

✅ **Start Menu Icons:**
- NEXUZY ARTICAL
- Setup Instructions
- Uninstall

✅ **Desktop Icon** (optional)

✅ **Post-Install:**
- Creates FIRST_RUN.txt with instructions
- Shows setup options
- Opens SETUP_INSTRUCTIONS.txt

---

## Step 4: Test the Installer

### Installation Test

1. **Run installer:**
   ```bash
   installer_output\NEXUZY_ARTICAL_Setup_v2.1.exe
   ```

2. **Follow wizard:**
   - Accept license
   - Choose install location
   - Select desktop icon (optional)
   - Choose configuration options:
     * Setup Firebase? (Yes/No)
     * Setup FTP? (Yes/No)
   - Install

3. **Verify installation:**
   ```
   C:\Program Files\NEXUZY ARTICAL\
     ├── NEXUZY_ARTICAL.exe
     ├── assets/
     │   ├── logo.png
     │   └── icon.ico
     ├── config/
     ├── data/
     ├── logs/
     ├── image_cache/
     ├── firebase_config.json.example
     ├── ftp_config.json.example
     ├── SETUP_INSTRUCTIONS.txt
     ├── FIRST_RUN.txt
     └── *.md files
   ```

4. **Test installed app:**
   - Double-click desktop icon OR
   - Start Menu → NEXUZY ARTICAL
   - App should launch successfully

5. **Test offline mode:**
   - App works without any configs
   - Local database functional

### Configuration Test

1. **Configure Firebase:**
   ```bash
   cd "C:\Program Files\NEXUZY ARTICAL"
   copy firebase_config.json.example firebase_config.json
   notepad firebase_config.json
   # Add your Firebase credentials
   ```

2. **Configure FTP:**
   ```bash
   copy ftp_config.json.example ftp_config.json
   notepad ftp_config.json
   # Add your FTP credentials
   ```

3. **Restart app and test:**
   - Firebase sync should work
   - Image upload should work
   - Image preview should work

### Uninstallation Test

1. **Uninstall:**
   - Control Panel → Programs → Uninstall
   - OR Start Menu → NEXUZY ARTICAL → Uninstall

2. **Verify cleanup:**
   - App files removed
   - User data preserved (optional)
   - Logs cleaned up

---

## Step 5: Distribution

### Package Contents

**Single File to Distribute:**
```
NEXUZY_ARTICAL_Setup_v2.1.exe  (~50-80 MB)
```

**What's Inside:**
- ✅ Complete application
- ✅ All assets (logo + icon)
- ✅ Config templates
- ✅ Documentation
- ✅ Folder structure

### Distribution Methods

1. **Direct Download:**
   - Upload to website/cloud storage
   - Share download link

2. **GitHub Release:**
   ```bash
   gh release create v2.1 \
     installer_output/NEXUZY_ARTICAL_Setup_v2.1.exe \
     --title "NEXUZY ARTICAL v2.1" \
     --notes "Complete installer with all configs and assets"
   ```

3. **USB/Physical Media:**
   - Copy installer to USB drive
   - Include README.txt with:
     * System requirements
     * Installation instructions
     * Support contact

### User Instructions

**Include with installer:**

```markdown
NEXUZY ARTICAL v2.1
===================

QUICK INSTALL:
1. Run NEXUZY_ARTICAL_Setup_v2.1.exe
2. Follow installation wizard
3. Launch from desktop icon

DEFAULT LOGIN:
Username: admin
Password: admin123

** CHANGE PASSWORD AFTER FIRST LOGIN **

OFFLINE MODE:
- App works immediately without configuration
- Local database only

CLOUD FEATURES (Optional):
- Configure Firebase for cloud sync
- Configure FTP for image upload
- See SETUP_INSTRUCTIONS.txt after install

SUPPORT:
GitHub: https://github.com/david0154/NEXUZY_ARTICAL
Email: monoj@nexuzy.in
```

---

## Troubleshooting

### Build Issues

**PyInstaller fails:**
```bash
# Reinstall PyInstaller
pip uninstall pyinstaller
pip install pyinstaller

# Try with --debug flag
python build/build.py --debug
```

**Missing dependencies:**
```bash
# Install all requirements
pip install -r requirements.txt

# Verify installations
pip list | findstr "firebase PIL openpyxl reportlab"
```

**Icon not found:**
```bash
# Check icon exists
dir assets\icon.ico

# If missing, skip icon:
pyinstaller --onefile --windowed --name=NEXUZY_ARTICAL main.py
```

### Installer Issues

**Inno Setup errors:**
- Check all paths in `inno_setup.iss`
- Ensure `dist/` folder exists and contains EXE
- Verify all referenced files exist

**Permission errors:**
- Run Inno Setup as Administrator
- Check file permissions in dist/

### Runtime Issues

**App won't start:**
- Check logs in `C:\Program Files\NEXUZY ARTICAL\logs\`
- Run from command line to see errors:
  ```bash
  cd "C:\Program Files\NEXUZY ARTICAL"
  .\NEXUZY_ARTICAL.exe
  ```

**Missing DLLs:**
- Install Visual C++ Redistributable:
  https://aka.ms/vs/17/release/vc_redist.x64.exe

**Firebase not working:**
- Verify `firebase_config.json` exists (not .example)
- Check credentials are correct
- Test internet connection

**FTP not working:**
- Verify `ftp_config.json` exists (not .example)
- Test FTP credentials separately
- Check firewall settings

---

## Version Update Process

### When Releasing New Version

1. **Update version numbers:**
   ```python
   # config.py
   APP_VERSION = "2.2"
   ```
   
   ```iss
   ; inno_setup.iss
   #define MyAppVersion "2.2"
   ```

2. **Update changelog:**
   - Add release notes to README.md
   - Document new features
   - List bug fixes

3. **Rebuild:**
   ```bash
   python build/build.py
   ```

4. **Test thoroughly:**
   - All features
   - Upgrade from previous version
   - Fresh installation

5. **Create installer:**
   - Compile with Inno Setup
   - Test installer

6. **Tag release:**
   ```bash
   git tag -a v2.2 -m "Version 2.2 release"
   git push origin v2.2
   ```

7. **Publish:**
   - Upload to GitHub Releases
   - Update download links
   - Announce to users

---

## Summary

### Complete Build Process:

```bash
# 1. Build executable
python build/build.py

# 2. Test executable
cd dist
.\NEXUZY_ARTICAL.exe

# 3. Create installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" inno_setup.iss

# 4. Test installer
installer_output\NEXUZY_ARTICAL_Setup_v2.1.exe

# 5. Distribute
# Upload installer or create GitHub release
```

### What Gets Packaged:

✅ **Application:**
- NEXUZY_ARTICAL.exe (50-80 MB)
- All Python dependencies bundled

✅ **Assets:**
- logo.png
- icon.ico

✅ **Config Templates:**
- firebase_config.json.example
- ftp_config.json.example

✅ **Documentation:**
- README.md
- QUICK_START.md
- FIREBASE_SETUP.md
- FTP_SETUP.md
- SETUP_INSTRUCTIONS.txt

✅ **Folder Structure:**
- data/ (database)
- logs/ (app logs)
- config/ (user configs)
- assets/ (images)
- image_cache/ (cached images)

---

## Support

**Developer:** Manoj Konar (monoj@nexuzy.in)  
**Company:** Nexuzy Tech Pvt Ltd  
**GitHub:** https://github.com/david0154/NEXUZY_ARTICAL

---

**Happy Building! 🚀**
