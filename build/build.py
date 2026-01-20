#!/usr/bin/env python3
"""
Automated Build Script for NEXUZY ARTICAL
Creates executable using PyInstaller as described in README
Author: Manoj Konar (monoj@nexuzy.in)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
ASSETS_DIR = PROJECT_ROOT / "assets"
MAIN_SCRIPT = PROJECT_ROOT / "main.py"

# Build configuration
APP_NAME = "NEXUZY_ARTICAL"
ICON_PATH = ASSETS_DIR / "icon.ico"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_prerequisites():
    """Check if all required files and dependencies exist"""
    print_header("Checking Prerequisites")
    
    # Check if main.py exists
    if not MAIN_SCRIPT.exists():
        print(f"❌ ERROR: main.py not found at {MAIN_SCRIPT}")
        return False
    print(f"✅ Found main.py")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✅ PyInstaller installed (version {PyInstaller.__version__})")
    except ImportError:
        print("❌ ERROR: PyInstaller not installed")
        print("   Install with: pip install pyinstaller")
        return False
    
    # Check if icon exists
    if ICON_PATH.exists():
        print(f"✅ Icon found: {ICON_PATH}")
    else:
        print(f"⚠️  WARNING: Icon not found at {ICON_PATH}")
        print("   Building without icon")
    
    # Check if assets directory exists
    if ASSETS_DIR.exists():
        print(f"✅ Assets directory found")
    else:
        print(f"⚠️  WARNING: Assets directory not found")
    
    return True

def clean_previous_builds():
    """Clean previous build artifacts"""
    print_header("Cleaning Previous Builds")
    
    directories_to_clean = [
        DIST_DIR,
        BUILD_DIR / "dist",
        BUILD_DIR / "build",
        PROJECT_ROOT / "__pycache__"
    ]
    
    files_to_clean = [
        PROJECT_ROOT / f"{APP_NAME}.spec"
    ]
    
    for directory in directories_to_clean:
        if directory.exists():
            try:
                shutil.rmtree(directory)
                print(f"🗑️  Removed: {directory}")
            except Exception as e:
                print(f"⚠️  Could not remove {directory}: {e}")
    
    for file in files_to_clean:
        if file.exists():
            try:
                file.unlink()
                print(f"🗑️  Removed: {file}")
            except Exception as e:
                print(f"⚠️  Could not remove {file}: {e}")
    
    print("✅ Cleanup complete")

def build_executable():
    """Build executable using PyInstaller"""
    print_header("Building Executable")
    
    # Prepare PyInstaller command
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI app)
        f"--name={APP_NAME}",           # Application name
        "--clean",                      # Clean cache before building
        "--noconfirm",                  # Replace output directory without confirmation
    ]
    
    # Add icon if it exists
    if ICON_PATH.exists():
        pyinstaller_cmd.extend([f"--icon={ICON_PATH}"])
    
    # Add hidden imports for dependencies that might not be auto-detected
    hidden_imports = [
        "firebase_admin",
        "PIL._tkinter_finder",
        "openpyxl",
        "reportlab",
    ]
    
    for module in hidden_imports:
        pyinstaller_cmd.extend([f"--hidden-import={module}"])
    
    # Add data files (assets)
    if ASSETS_DIR.exists():
        pyinstaller_cmd.extend([
            f"--add-data={ASSETS_DIR}{os.pathsep}assets"
        ])
    
    # Add main script
    pyinstaller_cmd.append(str(MAIN_SCRIPT))
    
    # Print command
    print("\n📦 Running PyInstaller...")
    print(f"Command: {' '.join(pyinstaller_cmd)}\n")
    
    # Run PyInstaller
    try:
        result = subprocess.run(
            pyinstaller_cmd,
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=False
        )
        
        print("\n✅ Build successful!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error during build: {e}")
        return False

def verify_build():
    """Verify that the executable was created"""
    print_header("Verifying Build")
    
    exe_name = f"{APP_NAME}.exe" if sys.platform == "win32" else APP_NAME
    exe_path = DIST_DIR / exe_name
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executable created successfully!")
        print(f"   Location: {exe_path}")
        print(f"   Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"❌ ERROR: Executable not found at {exe_path}")
        return False

def print_summary():
    """Print build summary and next steps"""
    print_header("Build Complete")
    
    exe_name = f"{APP_NAME}.exe" if sys.platform == "win32" else APP_NAME
    exe_path = DIST_DIR / exe_name
    
    print("\n🎉 BUILD SUCCESSFUL!\n")
    print(f"📂 Executable Location:")
    print(f"   {exe_path}\n")
    print(f"📝 Next Steps:")
    print(f"   1. Test the executable by running it")
    print(f"   2. Create installer using Inno Setup (optional)")
    print(f"   3. Distribute {exe_name} to users\n")
    print(f"⚠️  Important:")
    print(f"   - Ensure firebase_config.json is in the same directory as the EXE")
    print(f"   - The EXE will create 'data' and 'logs' folders automatically")
    print(f"   - First-time users should run the EXE as administrator\n")

def main():
    """Main build process"""
    print_header(f"NEXUZY ARTICAL - Build Script v1.0")
    print(f"Project: {PROJECT_ROOT}")
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Build aborted due to missing prerequisites")
        sys.exit(1)
    
    # Step 2: Clean previous builds
    clean_previous_builds()
    
    # Step 3: Build executable
    if not build_executable():
        print("\n❌ Build process failed")
        sys.exit(1)
    
    # Step 4: Verify build
    if not verify_build():
        print("\n❌ Build verification failed")
        sys.exit(1)
    
    # Step 5: Print summary
    print_summary()
    
    print("="*60)
    print("✅ All build steps completed successfully!")
    print("="*60 + "\n")

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
