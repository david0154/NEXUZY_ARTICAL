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
Version: 4.1

Fixes for runtime after build:
- Ensure user editable firebase_config.json + ftp_config.json are copied next to exe (if present)
  so users can just edit those and app reads from Option B (AppData) at runtime.
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
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_prerequisites():
    print_header("Checking Prerequisites")

    if not MAIN_SCRIPT.exists():
        print(f"❌ ERROR: main.py not found at {MAIN_SCRIPT}")
        return False
    print("✅ Found: main.py")

    try:
        import PyInstaller

        print(f"✅ PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        print("❌ ERROR: PyInstaller not installed")
        print("   Install: pip install pyinstaller")
        return False

    if ICON_PATH.exists():
        print(f"✅ Icon: {ICON_PATH}")
    else:
        print(f"⚠️  WARNING: Icon not found at {ICON_PATH}")
        print("   Build will continue without icon")

    if LOGO_PATH.exists():
        print(f"✅ Logo: {LOGO_PATH}")
    else:
        print(f"⚠️  WARNING: Logo not found at {LOGO_PATH}")

    if ASSETS_DIR.exists():
        assets = list(ASSETS_DIR.glob("*"))
        print(f"✅ Assets folder: {len(assets)} file(s)")
        for asset in assets:
            print(f"   - {asset.name}")
    else:
        print("⚠️  WARNING: Assets directory missing")

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

    creds_path = PROJECT_ROOT / "credentials.json"
    if creds_path.exists():
        print("✅ Firebase credentials: credentials.json")
    else:
        print("⚠️  WARNING: credentials.json missing (needed for Firebase)")

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
    print_header("Building Executable with PyInstaller")

    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        "--clean",
        "--noconfirm",
    ]

    if ICON_PATH.exists():
        pyinstaller_cmd.extend([f"--icon={ICON_PATH}"])
        print(f"🎨 Using icon: {ICON_PATH}")

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

    print("\n📁 Adding data files:")

    if ASSETS_DIR.exists():
        pyinstaller_cmd.append(f"--add-data={ASSETS_DIR}{os.pathsep}assets")
        print("   - assets/ folder")

    if CONFIG_DIR.exists():
        pyinstaller_cmd.append(f"--add-data={CONFIG_DIR}{os.pathsep}config")
        print("   - config/ folder")

    firebase_template = PROJECT_ROOT / "firebase_config.json.example"
    if firebase_template.exists():
        pyinstaller_cmd.append(f"--add-data={firebase_template}{os.pathsep}.")
        print("   - firebase_config.json.example")

    ftp_template = PROJECT_ROOT / "ftp_config.json.example"
    if ftp_template.exists():
        pyinstaller_cmd.append(f"--add-data={ftp_template}{os.pathsep}.")
        print("   - ftp_config.json.example")

    credentials = PROJECT_ROOT / "credentials.json"
    if credentials.exists():
        pyinstaller_cmd.append(f"--add-data={credentials}{os.pathsep}.")
        print("   - credentials.json")

    pyinstaller_cmd.extend(["--noupx", "--log-level=INFO", str(MAIN_SCRIPT)])

    print("\n🛠️  Starting build...")
    print(f"\nCommand: {' '.join(pyinstaller_cmd)}\n")
    print("=" * 70)

    try:
        subprocess.run(pyinstaller_cmd, cwd=PROJECT_ROOT, check=True, capture_output=False)
        print("\n" + "=" * 70)
        print("✅ PyInstaller build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 70)
        print(f"❌ Build failed with exit code: {e.returncode}")
        return False
    except Exception as e:
        print("\n" + "=" * 70)
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
        # If real configs exist in project root, copy them too for easy testing
        ("firebase_config.json", "Runtime config"),
        ("ftp_config.json", "Runtime config"),
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
            if filename.endswith(".json") and file_type == "Runtime config":
                # Not an error; user will create in AppData at runtime
                print(f"ℹ️  Not found (ok): {filename} ({file_type})")
            else:
                print(f"⚠️  Not found: {filename}")

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


def main():
    print_header(f"{APP_NAME} - Complete Build Script v4.1")
    print(f"Project: {PROJECT_ROOT}")
    print(f"Platform: {sys.platform}")

    if not check_prerequisites():
        print("\n❌ Build aborted: Missing prerequisites")
        sys.exit(1)

    clean_previous_builds()

    if not build_executable():
        print("\n❌ Build failed")
        sys.exit(1)

    if not verify_build():
        print("\n❌ Verification failed")
        sys.exit(1)

    copy_additional_files()

    print("=" * 70)
    print("✅ ALL BUILD STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 70 + "\n")


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
