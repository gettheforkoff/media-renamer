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
    
    # Find package data directories
    def find_package_data():
        """Find babelfish and guessit data directories"""
        import sys
        import importlib.util
        
        datas = []
        
        # Try to find babelfish data
        try:
            spec = importlib.util.find_spec('babelfish')
            if spec and spec.origin:
                babelfish_path = Path(spec.origin).parent
                babelfish_data = babelfish_path / 'data'
                if babelfish_data.exists():
                    datas.append((str(babelfish_data), 'babelfish/data'))
                    print(f"Found babelfish data at: {babelfish_data}")
        except Exception as e:
            print(f"Warning: Could not find babelfish data: {e}")
        
        # Try to find guessit data
        try:
            spec = importlib.util.find_spec('guessit')
            if spec and spec.origin:
                guessit_path = Path(spec.origin).parent
                guessit_data = guessit_path / 'data'
                if guessit_data.exists():
                    datas.append((str(guessit_data), 'guessit/data'))
                    print(f"Found guessit data at: {guessit_data}")
        except Exception as e:
            print(f"Warning: Could not find guessit data: {e}")
        
        return datas
    
    # Get data files
    try:
        data_files = find_package_data()
        data_str = ',\n        '.join([f"('{src}', '{dst}')" for src, dst in data_files])
        if data_str:
            data_str = f"        {data_str},"
    except Exception as e:
        print(f"Warning: Could not find package data files: {e}")
        data_str = ""
    
    # Create a temporary spec file for PyInstaller
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['media_renamer/main.py'],
    pathex=[],
    binaries=[],
    datas=[
{data_str}
    ],
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
        'pymediainfo',
        'requests',
        'click',
        'rich',
        'pydantic',
        'dateutil',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={{}},
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
""".format(data_str=data_str)
    
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