#!/usr/bin/env python3
"""
Script to build a standalone binary for the media renamer using PyInstaller
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        # Try uv first, fallback to pip
        try:
            subprocess.check_call(["uv", "pip", "install", "pyinstaller"])
        except (subprocess.CalledProcessError, FileNotFoundError):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def build_binary():
    """Build the binary using PyInstaller"""
    
    # Ensure we're in the correct directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Create a temporary spec file for PyInstaller with data collection
    spec_content = """# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
import os

block_cipher = None

# Collect data files for packages that need them
babelfish_datas = collect_data_files('babelfish')
guessit_datas = collect_data_files('guessit')

# Collect dynamic libraries for pymediainfo
pymediainfo_binaries = collect_dynamic_libs('pymediainfo')

# Try to find system libmediainfo library based on platform
libmediainfo_binaries = []
import sys
import platform

if sys.platform == 'linux':
    # Linux library paths - bundle with the exact name pymediainfo expects
    linux_paths = [
        '/usr/lib/x86_64-linux-gnu/libmediainfo.so.0',
        '/usr/lib/libmediainfo.so.0', 
        '/usr/local/lib/libmediainfo.so.0',
        '/usr/lib64/libmediainfo.so.0'
    ]
    for lib_path in linux_paths:
        if os.path.exists(lib_path):
            # Bundle with the exact name pymediainfo expects
            libmediainfo_binaries.append((lib_path, 'pymediainfo'))
            break
elif sys.platform == 'darwin':
    # macOS library paths
    macos_paths = [
        '/usr/local/lib/libmediainfo.dylib',
        '/opt/homebrew/lib/libmediainfo.dylib',
        '/usr/lib/libmediainfo.dylib'
    ]
    for lib_path in macos_paths:
        if os.path.exists(lib_path):
            # Bundle with the exact name pymediainfo expects
            libmediainfo_binaries.append((lib_path, 'pymediainfo'))
            break
elif sys.platform == 'win32':
    # Windows DLL paths
    windows_paths = [
        'C:\\Windows\\System32\\MediaInfo.dll',
        'C:\\Program Files\\MediaInfo\\MediaInfo.dll',
        'C:\\Program Files (x86)\\MediaInfo\\MediaInfo.dll'
    ]
    for lib_path in windows_paths:
        if os.path.exists(lib_path):
            # Bundle with the exact name pymediainfo expects
            libmediainfo_binaries.append((lib_path, 'pymediainfo'))
            break

# Warn if libmediainfo not found
if not libmediainfo_binaries:
    print("WARNING: libmediainfo library not found on this system.")
    print("The binary may not work properly for quality analysis.")
    if sys.platform == 'linux':
        print("Install with: sudo apt-get install libmediainfo0v5")
    elif sys.platform == 'darwin':
        print("Install with: brew install libmediainfo")
    elif sys.platform == 'win32':
        print("Download from: https://mediaarea.net/en/MediaInfo/Download/Windows")

a = Analysis(
    ['media_renamer/main.py'],
    pathex=[],
    binaries=pymediainfo_binaries + libmediainfo_binaries,
    datas=babelfish_datas + guessit_datas,
    hiddenimports=[
        'media_renamer.cli',
        'media_renamer.config',
        'media_renamer.models',
        'media_renamer.metadata_extractor',
        'media_renamer.api_clients',
        'media_renamer.renamer',
        'guessit',
        'guessit.rules',
        'guessit.rules.properties',
        'babelfish',
        'babelfish.country',
        'babelfish.language',
        'babelfish.converters',
        'babelfish.converters.alpha2',
        'babelfish.converters.alpha3b',
        'babelfish.converters.alpha3t',
        'babelfish.converters.countryname',
        'babelfish.converters.name',
        'babelfish.converters.opensubtitles',
        'babelfish.converters.scope',
        'babelfish.converters.type',
        'pymediainfo',
        'requests',
        'click',
        'rich',
        'pydantic',
        'dateutil',
        'dotenv',
    ],
    hookspath=['.'],
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
    name='media-renamer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    # Write the spec file
    spec_file = project_root / "media_renamer.spec"
    with open(spec_file, "w") as f:
        f.write(spec_content)
    
    # Build the binary
    print("Building binary...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        str(spec_file)
    ]
    
    subprocess.check_call(cmd)
    
    # Clean up
    spec_file.unlink()
    
    # Check if binary was created
    dist_dir = project_root / "dist"
    binary_path = dist_dir / "media-renamer"
    if sys.platform == "win32":
        binary_path = binary_path.with_suffix(".exe")
    
    if binary_path.exists():
        print(f"Binary created successfully: {binary_path}")
        print(f"Binary size: {binary_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Make it executable on Unix systems
        if sys.platform != "win32":
            os.chmod(binary_path, 0o755)
            
        return binary_path
    else:
        print("Failed to create binary")
        return None


def main():
    """Main function"""
    print("Media Renamer Binary Builder")
    print("=" * 40)
    
    install_pyinstaller()
    binary_path = build_binary()
    
    if binary_path:
        print(f"\nBinary build completed successfully!")
        print(f"Location: {binary_path}")
        print(f"\nUsage: {binary_path} /path/to/media/files --dry-run")
    else:
        print("\nBinary build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()