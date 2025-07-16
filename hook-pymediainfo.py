"""
PyInstaller hook for pymediainfo
"""
import os
import sys
from PyInstaller.utils.hooks import collect_dynamic_libs

# Collect any dynamic libraries that pymediainfo might need
binaries = collect_dynamic_libs('pymediainfo')

# Add platform-specific MediaInfo libraries
if sys.platform == 'linux':
    # Linux library paths
    linux_paths = [
        '/usr/lib/x86_64-linux-gnu/libmediainfo.so.0',
        '/usr/lib/libmediainfo.so.0', 
        '/usr/local/lib/libmediainfo.so.0',
        '/usr/lib64/libmediainfo.so.0'
    ]
    for lib_path in linux_paths:
        if os.path.exists(lib_path):
            binaries.append((lib_path, 'pymediainfo'))
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
            binaries.append((lib_path, 'pymediainfo'))
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
            binaries.append((lib_path, 'pymediainfo'))
            break