#!/usr/bin/env python3
"""Enhanced Build Script - Includes ALL configs and assets

Includes:
- firebase_config.json.example
- ftp_config.json.example
- All assets (logo.png, icon.ico)
- Config folder
- Complete dependency collection

Author: Manoj Konar (monoj@nexuzy.in)
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

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_prerequisites():
    print_header("Checking Prerequisites")
    
    if not MAIN_SCRIPT.exists():
        print(f"❌ ERROR: main.py not found")
        return False
    print(f"✅ Found main.py")
    
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("❌ ERROR: PyInstaller not installed")
        return False
    
    if ICON_PATH.exists():
        print(f"✅ Icon: {ICON_PATH}")
    else:
        print(f"⚠️  WARNING: Icon not found")
    
    if ASSETS_DIR.exists():
        assets = list(ASSETS_DIR.glob('*'))
        print(f"✅ Assets: {len(assets)} file(s)")
    else:
        print(f"⚠️  WARNING: Assets directory missing")
    
    # Check config templates
    config_templates = [
        PROJECT_ROOT / "firebase_config.json.example",
        PROJECT_ROOT / "ftp_config.json.example",
    ]
    
    for template in config_templates:
        if template.exists():
            print(f"✅ Template: {template.name}")
        else:
            print(f"⚠️  WARNING: {template.name} missing")
    
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
    
    spec_file = PROJECT_ROOT / f"{APP_NAME}.spec"
    if spec_file.exists():
        spec_file.unlink()
        print(f"🗑️  Removed: {spec_file}")
    
    print("✅ Cleanup complete")

def build_executable():
    print_header("Building Executable")
    
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        "--clean",
        "--noconfirm",
    ]
    
    if ICON_PATH.exists():
        pyinstaller_cmd.extend([f"--icon={ICON_PATH}"])
    
    # Comprehensive hidden imports
    hidden_imports = [
        "firebase_admin",
        "firebase_admin.credentials",
        "firebase_admin.firestore",
        "google.cloud.firestore",
        "PIL",
        "PIL._tkinter_finder",
        "PIL.Image",
        "PIL.ImageTk",
        "openpyxl",
        "reportlab",
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "json",
        "sqlite3",
        "ftplib",
    ]
    
    for module in hidden_imports:
        pyinstaller_cmd.extend([f"--hidden-import={module}"])
    
    # Collect all packages
    for package in ["firebase_admin", "google-cloud-firestore", "PIL", "openpyxl"]:
        pyinstaller_cmd.extend([f"--collect-all={package}"])
    
    # Add data files - CRITICAL: Include all configs and assets
    data_files = []
    
    # Assets folder (logo.png, icon.ico)
    if ASSETS_DIR.exists():
        data_files.append(f"--add-data={ASSETS_DIR}{os.pathsep}assets")
    
    # Config folder
    if CONFIG_DIR.exists():
        data_files.append(f"--add-data={CONFIG_DIR}{os.pathsep}config")
    
    # Config templates (firebase_config.json.example, ftp_config.json.example)
    config_templates = [
        PROJECT_ROOT / "firebase_config.json.example",
        PROJECT_ROOT / "ftp_config.json.example",
    ]
    
    for template in config_templates:
        if template.exists():
            data_files.append(f"--add-data={template}{os.pathsep}.")
    
    pyinstaller_cmd.extend(data_files)
    
    pyinstaller_cmd.extend([
        "--noupx",
        "--log-level=INFO",
    ])
    
    pyinstaller_cmd.append(str(MAIN_SCRIPT))
    
    print("\n📦 Running PyInstaller...")
    print(f"Command: {' '.join(pyinstaller_cmd)}\n")
    
    try:
        subprocess.run(pyinstaller_cmd, cwd=PROJECT_ROOT, check=True)
        print("\n✅ Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def verify_build():
    print_header("Verifying Build")
    
    exe_name = f"{APP_NAME}.exe" if sys.platform == "win32" else APP_NAME
    exe_path = DIST_DIR / exe_name
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executable: {exe_path}")
        print(f"   Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"❌ ERROR: Executable not found")
        return False

def copy_config_templates():
    """Copy config templates to dist folder"""
    print_header("Copying Config Templates")
    
    templates = [
        "firebase_config.json.example",
        "ftp_config.json.example",
    ]
    
    for template in templates:
        src = PROJECT_ROOT / template
        dst = DIST_DIR / template
        
        if src.exists():
            try:
                shutil.copy2(src, dst)
                print(f"✅ Copied: {template}")
            except Exception as e:
                print(f"⚠️  Failed to copy {template}: {e}")
        else:
            print(f"⚠️  Template not found: {template}")

def print_summary():
    print_header("Build Complete")
    
    exe_name = f"{APP_NAME}.exe" if sys.platform == "win32" else APP_NAME
    exe_path = DIST_DIR / exe_name
    
    print("\n🎉 BUILD SUCCESSFUL!\n")
    print(f"📂 Executable: {exe_path}\n")
    print("📝 Next Steps:")
    print("   1. Test the executable")
    print("   2. Copy firebase_config.json.example to firebase_config.json")
    print("   3. Copy ftp_config.json.example to ftp_config.json")
    print("   4. Configure both JSON files with your credentials")
    print("   5. Place configured files in same folder as EXE")
    print("   6. Run Inno Setup to create installer")
    print("   7. Distribute to users\n")
    print("⚠️  Important:")
    print("   - EXE needs firebase_config.json for cloud sync")
    print("   - EXE needs ftp_config.json for image upload")
    print("   - App works offline without configs (local-only mode)")
    print("   - First run: Downloads existing Firebase data\n")

def main():
    print_header(f"{APP_NAME} - Enhanced Build Script v3.0")
    print(f"Project: {PROJECT_ROOT}")
    
    if not check_prerequisites():
        print("\n❌ Build aborted")
        sys.exit(1)
    
    clean_previous_builds()
    
    if not build_executable():
        print("\n❌ Build failed")
        sys.exit(1)
    
    if not verify_build():
        print("\n❌ Verification failed")
        sys.exit(1)
    
    copy_config_templates()
    print_summary()
    
    print("="*60)
    print("✅ All build steps completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
