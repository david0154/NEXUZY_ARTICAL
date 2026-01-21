#!/usr/bin/env python3
"""Complete Build Script - ALL Configs + Assets Included

Builds executable with:
- Logo (assets/logo.png)
- Icon (assets/icon.ico)  
- Firebase config template
- FTP config template
- All dependencies
- Config folder structure

Author: Manoj Konar (monoj@nexuzy.in)
Version: 4.0
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
ASSETS_DIR = PROJECT_ROOT / "assets"
CONFIG_DIR = PROJECT_ROOT / "config"
MAIN_SCRIPT = PROJECT_ROOT / "main.py"

APP_NAME = "NEXUZY_ARTICAL"
ICON_PATH = ASSETS_DIR / "icon.ico"
LOGO_PATH = ASSETS_DIR / "logo.png"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_prerequisites():
    print_header("Checking Prerequisites")
    
    # Check main script
    if not MAIN_SCRIPT.exists():
        print(f"❌ ERROR: main.py not found at {MAIN_SCRIPT}")
        return False
    print(f"✅ Found: main.py")
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        print("❌ ERROR: PyInstaller not installed")
        print("   Install: pip install pyinstaller")
        return False
    
    # Check assets
    if ICON_PATH.exists():
        print(f"✅ Icon: {ICON_PATH}")
    else:
        print(f"⚠️  WARNING: Icon not found at {ICON_PATH}")
        print("   Build will continue without icon")
    
    if LOGO_PATH.exists():
        print(f"✅ Logo: {LOGO_PATH}")
    else:
        print(f"⚠️  WARNING: Logo not found at {LOGO_PATH}")
    
    # Check assets directory
    if ASSETS_DIR.exists():
        assets = list(ASSETS_DIR.glob('*'))
        print(f"✅ Assets folder: {len(assets)} file(s)")
        for asset in assets:
            print(f"   - {asset.name}")
    else:
        print(f"⚠️  WARNING: Assets directory missing")
    
    # Check config templates
    config_templates = [
        (PROJECT_ROOT / "firebase_config.json.example", "Firebase config template"),
        (PROJECT_ROOT / "ftp_config.json.example", "FTP config template"),
    ]
    
    for template_path, description in config_templates:
        if template_path.exists():
            print(f"✅ {description}: {template_path.name}")
        else:
            print(f"⚠️  WARNING: {description} missing")
            print(f"   Expected at: {template_path}")
    
    # Check credentials.json
    creds_path = PROJECT_ROOT / "credentials.json"
    if creds_path.exists():
        print(f"✅ Firebase credentials: credentials.json")
    else:
        print(f"⚠️  WARNING: credentials.json missing (needed for Firebase)")
    
    return True

def clean_previous_builds():
    print_header("Cleaning Previous Builds")
    
    dirs_to_clean = [
        DIST_DIR,
        BUILD_DIR / "dist",
        BUILD_DIR / "build",
        PROJECT_ROOT / "__pycache__",
    ]
    
    for directory in dirs_to_clean:
        if directory.exists():
            try:
                shutil.rmtree(directory)
                print(f"🗑️  Removed: {directory}")
            except Exception as e:
                print(f"⚠️  Could not remove {directory}: {e}")
    
    # Remove spec file
    spec_file = PROJECT_ROOT / f"{APP_NAME}.spec"
    if spec_file.exists():
        spec_file.unlink()
        print(f"🗑️  Removed: {spec_file}")
    
    print("✅ Cleanup complete")

def build_executable():
    print_header("Building Executable with PyInstaller")
    
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        "--clean",
        "--noconfirm",
    ]
    
    # Add icon
    if ICON_PATH.exists():
        pyinstaller_cmd.extend([f"--icon={ICON_PATH}"])
        print(f"🎨 Using icon: {ICON_PATH}")
    
    # Hidden imports for all dependencies
    hidden_imports = [
        "firebase_admin",
        "firebase_admin.credentials",
        "firebase_admin.firestore",
        "google.cloud.firestore",
        "google.cloud.firestore_v1",
        "PIL",
        "PIL._tkinter_finder",
        "PIL.Image",
        "PIL.ImageTk",
        "openpyxl",
        "reportlab",
        "reportlab.pdfgen",
        "reportlab.lib",
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "json",
        "sqlite3",
        "ftplib",
        "hashlib",
        "urllib",
        "urllib.request",
        "io",
    ]
    
    print("\n📦 Adding hidden imports:")
    for module in hidden_imports:
        pyinstaller_cmd.extend([f"--hidden-import={module}"])
        print(f"   - {module}")
    
    # Collect all packages
    packages_to_collect = [
        "firebase_admin",
        "google-cloud-firestore",
        "PIL",
        "openpyxl",
        "reportlab",
    ]
    
    print("\n📦 Collecting packages:")
    for package in packages_to_collect:
        pyinstaller_cmd.extend([f"--collect-all={package}"])
        print(f"   - {package}")
    
    # Add data files - ALL configs and assets
    print("\n📁 Adding data files:")
    
    # Assets folder (logo.png, icon.ico)
    if ASSETS_DIR.exists():
        pyinstaller_cmd.append(f"--add-data={ASSETS_DIR}{os.pathsep}assets")
        print(f"   - assets/ folder")
    
    # Config folder
    if CONFIG_DIR.exists():
        pyinstaller_cmd.append(f"--add-data={CONFIG_DIR}{os.pathsep}config")
        print(f"   - config/ folder")
    
    # Firebase config template
    firebase_template = PROJECT_ROOT / "firebase_config.json.example"
    if firebase_template.exists():
        pyinstaller_cmd.append(f"--add-data={firebase_template}{os.pathsep}.")
        print(f"   - firebase_config.json.example")
    
    # FTP config template
    ftp_template = PROJECT_ROOT / "ftp_config.json.example"
    if ftp_template.exists():
        pyinstaller_cmd.append(f"--add-data={ftp_template}{os.pathsep}.")
        print(f"   - ftp_config.json.example")
    
    # Firebase credentials (if exists)
    credentials = PROJECT_ROOT / "credentials.json"
    if credentials.exists():
        pyinstaller_cmd.append(f"--add-data={credentials}{os.pathsep}.")
        print(f"   - credentials.json")
    
    # Add main script
    pyinstaller_cmd.extend([
        "--noupx",
        "--log-level=INFO",
        str(MAIN_SCRIPT)
    ])
    
    print("\n🛠️  Starting build...")
    print(f"\nCommand: {' '.join(pyinstaller_cmd)}\n")
    print("="*70)
    
    try:
        result = subprocess.run(
            pyinstaller_cmd,
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=False
        )
        print("\n" + "="*70)
        print("✅ PyInstaller build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "="*70)
        print(f"❌ Build failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print("\n" + "="*70)
        print(f"❌ Unexpected error: {e}")
        return False

def verify_build():
    print_header("Verifying Build Output")
    
    exe_name = f"{APP_NAME}.exe" if sys.platform == "win32" else APP_NAME
    exe_path = DIST_DIR / exe_name
    
    if not exe_path.exists():
        print(f"❌ ERROR: Executable not found at {exe_path}")
        return False
    
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"✅ Executable created: {exe_path}")
    print(f"   Size: {size_mb:.2f} MB")
    
    # Check for bundled files in dist
    expected_files = [
        "firebase_config.json.example",
        "ftp_config.json.example",
    ]
    
    print("\n📝 Checking bundled files:")
    for filename in expected_files:
        file_path = DIST_DIR / filename
        if file_path.exists():
            print(f"   ✅ {filename}")
        else:
            print(f"   ⚠️  {filename} (missing - will copy)")
    
    return True

def copy_additional_files():
    """Copy config templates and documentation to dist folder"""
    print_header("Copying Additional Files to dist/")
    
    files_to_copy = [
        ("firebase_config.json.example", "Config template"),
        ("ftp_config.json.example", "Config template"),
        ("README.md", "Documentation"),
        ("QUICK_START.md", "Documentation"),
        ("FIREBASE_SETUP.md", "Documentation"),
        ("FTP_SETUP.md", "Documentation"),
    ]
    
    for filename, file_type in files_to_copy:
        src = PROJECT_ROOT / filename
        dst = DIST_DIR / filename
        
        if src.exists():
            try:
                shutil.copy2(src, dst)
                print(f"✅ Copied: {filename} ({file_type})")
            except Exception as e:
                print(f"⚠️  Failed to copy {filename}: {e}")
        else:
            print(f"⚠️  Not found: {filename}")
    
    # Create folders in dist
    folders_to_create = [
        "data",
        "logs",
        "image_cache",
    ]
    
    print("\n📂 Creating folders:")
    for folder in folders_to_create:
        folder_path = DIST_DIR / folder
        folder_path.mkdir(exist_ok=True)
        print(f"✅ Created: {folder}/")

def create_setup_instructions():
    """Create SETUP_INSTRUCTIONS.txt in dist folder"""
    print_header("Creating Setup Instructions")
    
    instructions = """NEXUZY ARTICAL - SETUP INSTRUCTIONS
========================================

THANK YOU FOR USING NEXUZY ARTICAL!

QUICK START:
------------
1. Run NEXUZY_ARTICAL.exe
2. App works in offline mode (local database only)
3. For cloud sync and image upload, follow configuration below

CONFIGURATION (Optional):
-------------------------

FIREBASE SETUP (for cloud sync):
  1. Rename 'firebase_config.json.example' to 'firebase_config.json'
  2. Edit firebase_config.json with your Firebase credentials:
     - apiKey
     - authDomain
     - projectId
     - storageBucket
     - messagingSenderId
     - appId
  3. Get credentials from Firebase Console:
     https://console.firebase.google.com/
  4. See FIREBASE_SETUP.md for detailed guide

FTP SETUP (for image upload):
  1. Rename 'ftp_config.json.example' to 'ftp_config.json'
  2. Edit ftp_config.json with your FTP server details:
     - host: your-ftp-server.com
     - port: 21
     - username: your_ftp_username
     - password: your_ftp_password
     - remote_dir: /path/to/upload/folder
  3. See FTP_SETUP.md for detailed guide

FEATURES:
---------
✅ Article Management (offline + cloud sync)
✅ User Management (admin only)
✅ Image Upload (FTP)
✅ Image Preview (with caching)
✅ Export to PDF/Excel
✅ Automatic sync with Firebase
✅ Works offline without configs

DEFAULT LOGIN:
--------------
Username: admin
Password: admin123

CHANGE DEFAULT PASSWORD IMMEDIATELY!

FOLDERS:
--------
- data/: Local SQLite database
- logs/: Application logs
- image_cache/: Cached images from FTP
- assets/: Logo and icon files
- config/: User configuration

TROUBLESHOOTING:
----------------
1. App won't start:
   - Check logs/ folder for error messages
   - Ensure all DLL files are present

2. Firebase sync not working:
   - Verify firebase_config.json is correct
   - Check internet connection
   - See logs for detailed errors

3. Image upload fails:
   - Verify ftp_config.json is correct
   - Test FTP connection separately
   - Check FTP server permissions

4. Image preview not working:
   - Check FTP credentials in ftp_config.json
   - Verify image exists on FTP server
   - Check image_cache/ folder permissions

SUPPORT:
--------
GitHub: https://github.com/david0154/NEXUZY_ARTICAL
Developer: Manoj Konar (monoj@nexuzy.in)
Company: Nexuzy Tech Pvt Ltd

ENJOY USING NEXUZY ARTICAL!
"""
    
    instructions_file = DIST_DIR / "SETUP_INSTRUCTIONS.txt"
    try:
        instructions_file.write_text(instructions, encoding='utf-8')
        print(f"✅ Created: SETUP_INSTRUCTIONS.txt")
    except Exception as e:
        print(f"⚠️  Failed to create instructions: {e}")

def print_summary():
    print_header("BUILD COMPLETE - SUMMARY")
    
    exe_name = f"{APP_NAME}.exe" if sys.platform == "win32" else APP_NAME
    exe_path = DIST_DIR / exe_name
    
    print("\n🎉 BUILD SUCCESSFUL!\n")
    print(f"💾 Executable: {exe_path}")
    print(f"📂 Output folder: {DIST_DIR}\n")
    
    print("📦 Included in build:")
    print("   ✅ Logo (assets/logo.png)")
    print("   ✅ Icon (assets/icon.ico)")
    print("   ✅ Firebase config template")
    print("   ✅ FTP config template")
    print("   ✅ All dependencies")
    print("   ✅ Config folder structure")
    print("   ✅ Image cache folder")
    print("   ✅ Documentation files\n")
    
    print("🛠️  Next Steps:")
    print("   1. Test the executable:")
    print(f"      {exe_path}\n")
    print("   2. Create installer with Inno Setup:")
    print("      - Open inno_setup.iss")
    print("      - Compile to create installer")
    print("      - Installer includes all configs\n")
    print("   3. Distribute to users:")
    print("      - Share the installer EXE")
    print("      - Users configure Firebase/FTP as needed")
    print("      - App works offline by default\n")
    
    print("⚠️  Important Notes:")
    print("   - Config templates are EXAMPLES only")
    print("   - Users must rename .example files and add credentials")
    print("   - App works without configs (offline mode)")
    print("   - Firebase sync needs firebase_config.json")
    print("   - Image upload needs ftp_config.json")
    print("   - See SETUP_INSTRUCTIONS.txt in dist/ folder\n")

def main():
    print_header(f"{APP_NAME} - Complete Build Script v4.0")
    print(f"Project: {PROJECT_ROOT}")
    print(f"Platform: {sys.platform}")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Build aborted: Missing prerequisites")
        sys.exit(1)
    
    # Clean old builds
    clean_previous_builds()
    
    # Build executable
    if not build_executable():
        print("\n❌ Build failed")
        sys.exit(1)
    
    # Verify build
    if not verify_build():
        print("\n❌ Verification failed")
        sys.exit(1)
    
    # Copy additional files
    copy_additional_files()
    
    # Create setup instructions
    create_setup_instructions()
    
    # Print summary
    print_summary()
    
    print("="*70)
    print("✅ ALL BUILD STEPS COMPLETED SUCCESSFULLY!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
