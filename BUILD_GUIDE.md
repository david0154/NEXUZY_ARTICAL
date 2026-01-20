# NEXUZY ARTICAL - Complete Build Guide

> **Build and Package Your Windows Application**  
> Three methods: Automated Script, Manual PyInstaller, Inno Setup Installer  
> Author: Manoj Konar | monoj@nexuzy.in

---

## 📦 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Method 1: Automated Build (Recommended)](#method-1-automated-build-recommended)
3. [Method 2: Manual PyInstaller](#method-2-manual-pyinstaller)
4. [Method 3: Create Installer with Inno Setup](#method-3-create-installer-with-inno-setup)
5. [Troubleshooting](#troubleshooting)
6. [Distribution](#distribution)

---

## Prerequisites

### Required Software

1. **Python 3.8+** (with pip)
2. **PyInstaller** (install via pip)
3. **Inno Setup** (for creating installer) - [Download](https://jrsoftware.org/isinfo.php)
4. **Git** (optional, for version control)

### Install PyInstaller

```bash
pip install pyinstaller
```

### Verify Installation

```bash
pyinstaller --version
# Should output: 6.3.0 or higher
```

---

## Method 1: Automated Build (Recommended)

### ✅ Easiest Method - One Command!

The automated build script handles everything:

```bash
python build/build.py
```

### What It Does:

✅ Checks all prerequisites  
✅ Cleans previous builds  
✅ Runs PyInstaller with correct parameters  
✅ Bundles assets and dependencies  
✅ Creates single-file EXE in `dist/` folder  
✅ Verifies build success

### Output:

```
dist/NEXUZY_ARTICAL.exe
```

**File Size:** ~40-60 MB (includes Python runtime + all dependencies)

---

## Method 2: Manual PyInstaller

### Basic Command

From the project root directory:

```bash
pyinstaller --onefile --windowed --name="NEXUZY_ARTICAL" --icon=assets/icon.ico main.py
```

### Advanced Command (With All Options)

```bash
pyinstaller ^
  --onefile ^
  --windowed ^
  --name="NEXUZY_ARTICAL" ^
  --icon=assets/icon.ico ^
  --clean ^
  --noconfirm ^
  --add-data="assets;assets" ^
  --hidden-import=firebase_admin ^
  --hidden-import=PIL._tkinter_finder ^
  --hidden-import=openpyxl ^
  --hidden-import=reportlab ^
  main.py
```

### Parameter Explanation:

| Parameter | Description |
|-----------|-------------|
| `--onefile` | Creates single executable (not a folder) |
| `--windowed` | No console window (GUI only) |
| `--name="NEXUZY_ARTICAL"` | Output filename |
| `--icon=assets/icon.ico` | Application icon |
| `--clean` | Clean PyInstaller cache before building |
| `--noconfirm` | Replace output directory without confirmation |
| `--add-data="assets;assets"` | Include assets folder (Windows) |
| `--hidden-import=module` | Explicitly include modules |

### Linux/Mac Command:

Use `:` instead of `;` for `--add-data`:

```bash
pyinstaller --onefile --windowed --name="NEXUZY_ARTICAL" \
  --icon=assets/icon.ico \
  --add-data="assets:assets" \
  --hidden-import=firebase_admin \
  main.py
```

### Output:

```
dist/NEXUZY_ARTICAL.exe          # Your executable
build/                           # Temporary build files (can delete)
NEXUZY_ARTICAL.spec             # PyInstaller spec file (keep for rebuilds)
```

---

## Method 3: Create Installer with Inno Setup

### Prerequisites:

1. Build the EXE first (using Method 1 or 2)
2. Install [Inno Setup](https://jrsoftware.org/isinfo.php)

### Steps:

#### 1. Build the EXE

```bash
python build/build.py
```

#### 2. Open Inno Setup Compiler

- Launch **Inno Setup Compiler**
- File → Open → Select `inno_setup.iss`

#### 3. Compile the Installer

- Click **Build** → **Compile**
- Or press **Ctrl+F9**

#### 4. Find Your Installer

```
installer_output/NEXUZY_ARTICAL_Setup_v1.0.0.exe
```

### Installer Features:

✅ Professional Windows installer  
✅ Desktop shortcut creation  
✅ Start Menu entry  
✅ Automatic directory creation (data, logs, exports)  
✅ Checks if app is running before install/uninstall  
✅ Clean uninstallation  
✅ Compressed installation (~20 MB installer size)

### Command-Line Inno Setup Compilation:

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" inno_setup.iss
```

---

## 🛠️ Troubleshooting

### Issue: PyInstaller not found

**Solution:**

```bash
pip install --upgrade pyinstaller
```

### Issue: Module not found in EXE

**Solution:** Add hidden import:

```bash
pyinstaller --hidden-import=module_name ...
```

### Issue: Assets not found

**Solution:** Verify assets path:

```bash
pyinstaller --add-data="assets;assets" ...
```

### Issue: EXE is too large

**Solutions:**

1. Use `--onefile` (already included)
2. Use UPX compression:

```bash
pip install pyinstaller[upx]
pyinstaller --upx-dir=upx_dir ...
```

### Issue: Antivirus flags the EXE

**Reason:** PyInstaller executables are sometimes flagged as false positives.

**Solutions:**

1. Add exception in antivirus
2. Code-sign the EXE (recommended for distribution)
3. Use `--exclude-module` to remove unused modules

### Issue: Firebase config not found

**Solution:** Ensure `firebase_config.json` is in the same folder as the EXE.

### Issue: DLL errors on older Windows

**Solution:** Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

---

## 📦 Distribution

### Option 1: Distribute EXE Only

**Package Contents:**

```
NEXUZY_ARTICAL_Portable/
├── NEXUZY_ARTICAL.exe
├── firebase_config.json        # User must add their own
├── README.txt                   # Instructions
└── assets/                     # (Optional, if not embedded)
    ├── logo.png
    └── icon.ico
```

**Compression:**

```bash
# Zip for distribution
zip -r NEXUZY_ARTICAL_Portable.zip NEXUZY_ARTICAL_Portable/
```

### Option 2: Distribute Installer

**Single File:**

```
NEXUZY_ARTICAL_Setup_v1.0.0.exe
```

**Upload to:**
- Your website
- GitHub Releases
- Google Drive / Dropbox

### Option 3: Microsoft Store

Use [MSIX Packaging Tool](https://www.microsoft.com/store/productId/9N5LW3JBCXKF) to convert the EXE to MSIX for Microsoft Store submission.

---

## 📝 Build Checklist

### Before Building:

- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Code tested and working (`python main.py`)
- [ ] Assets folder complete (icon.ico, logo.png)
- [ ] README.md updated
- [ ] Version number updated in `config.py` and `inno_setup.iss`

### Build Steps:

- [ ] Run automated build: `python build/build.py`
- [ ] Test the EXE: `dist/NEXUZY_ARTICAL.exe`
- [ ] Create installer (optional): Compile `inno_setup.iss`
- [ ] Test installer on clean Windows machine

### Post-Build:

- [ ] Create release notes
- [ ] Upload to distribution platform
- [ ] Create GitHub Release (optional)
- [ ] Notify users

---

## 🔧 Advanced: Custom Spec File

For more control, edit `NEXUZY_ARTICAL.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=['firebase_admin', 'PIL._tkinter_finder', 'openpyxl', 'reportlab'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NEXUZY_ARTICAL',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
```

### Build with Spec File:

```bash
pyinstaller NEXUZY_ARTICAL.spec
```

---

## 🎉 Success!

You now have:

✅ **Standalone EXE** - `dist/NEXUZY_ARTICAL.exe`  
✅ **Professional Installer** - `installer_output/NEXUZY_ARTICAL_Setup_v1.0.0.exe`  
✅ **Portable Package** - Ready for distribution

---

## 📞 Support

**Issues?** Contact:

- **Email:** monoj@nexuzy.in
- **GitHub:** [NEXUZY_ARTICAL Repository](https://github.com/david0154/NEXUZY_ARTICAL)

---

## 📜 License

Proprietary - Nexuzy © 2026  
All Rights Reserved

---

**Happy Building! 🚀**
