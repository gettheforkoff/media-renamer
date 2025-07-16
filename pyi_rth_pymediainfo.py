"""
Runtime hook for pymediainfo to handle libmediainfo library loading
"""
import os
import sys
import shutil
from pathlib import Path

def setup_mediainfo_library():
    """Setup libmediainfo library for pymediainfo"""
    if not hasattr(sys, 'frozen') or not sys.frozen:
        # Not a PyInstaller frozen app, skip
        return
    
    # Get the temporary directory where PyInstaller extracts files
    bundle_dir = Path(sys._MEIPASS)
    
    # Look for libmediainfo in the bundle
    lib_files = []
    
    if sys.platform == 'linux':
        # Look for the library file
        for pattern in ['libmediainfo.so.0', 'libmediainfo.so.*']:
            lib_files.extend(bundle_dir.glob(f'**/{pattern}'))
    elif sys.platform == 'darwin':
        for pattern in ['libmediainfo.dylib', 'libmediainfo.*.dylib']:
            lib_files.extend(bundle_dir.glob(f'**/{pattern}'))
    elif sys.platform == 'win32':
        for pattern in ['MediaInfo.dll', 'libmediainfo.dll']:
            lib_files.extend(bundle_dir.glob(f'**/{pattern}'))
    
    if lib_files:
        # Found library, ensure it's in the right place
        lib_file = lib_files[0]
        pymediainfo_dir = bundle_dir / 'pymediainfo'
        pymediainfo_dir.mkdir(exist_ok=True)
        
        # Copy with the expected name
        if sys.platform == 'linux':
            target_name = 'libmediainfo.so.0'
        elif sys.platform == 'darwin':
            target_name = 'libmediainfo.dylib'
        elif sys.platform == 'win32':
            target_name = 'MediaInfo.dll'
        
        target_path = pymediainfo_dir / target_name
        if not target_path.exists():
            shutil.copy2(lib_file, target_path)
            
        # Also try to copy to the root of the bundle for fallback
        fallback_path = bundle_dir / target_name
        if not fallback_path.exists():
            shutil.copy2(lib_file, fallback_path)

# Run the setup
setup_mediainfo_library()