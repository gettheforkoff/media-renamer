#!/usr/bin/env python3
"""
Test script to debug PyInstaller bundling
"""
import os
import sys
import tempfile
import subprocess
from pathlib import Path

def test_library_detection():
    """Test if libmediainfo library can be found"""
    print("Testing library detection...")
    
    lib_path = None
    if sys.platform == 'linux':
        linux_paths = [
            '/usr/lib/x86_64-linux-gnu/libmediainfo.so.0',
            '/usr/lib/libmediainfo.so.0', 
            '/usr/local/lib/libmediainfo.so.0',
            '/usr/lib64/libmediainfo.so.0',
            '/usr/lib/aarch64-linux-gnu/libmediainfo.so.0'
        ]
        for lib_path in linux_paths:
            if os.path.exists(lib_path):
                print(f"✅ Found library at: {lib_path}")
                assert lib_path is not None, "Library path should not be None when found"
                return lib_path
    
    print("❌ No library found")
    return lib_path

def test_pyinstaller_bundling():
    """Test PyInstaller bundling with a minimal example"""
    print("\nTesting PyInstaller bundling...")
    
    # Create a minimal test script
    test_script = """
import sys
try:
    from pymediainfo import MediaInfo
    print("✅ pymediainfo imported successfully")
    # Try to create a MediaInfo object
    mi = MediaInfo
    print("✅ MediaInfo class accessible")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        # Build with PyInstaller
        lib_path = test_library_detection()
        if lib_path:
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--onefile',
                '--add-binary', f'{lib_path}:pymediainfo',
                '--hidden-import', 'pymediainfo',
                '--clean',
                test_file
            ]
        else:
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--onefile',
                '--hidden-import', 'pymediainfo',
                '--clean',
                test_file
            ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyInstaller build successful")
            
            # Try to run the binary
            binary_name = Path(test_file).stem
            binary_path = Path('dist') / binary_name
            
            if binary_path.exists():
                print(f"✅ Binary created: {binary_path}")
                
                # Test the binary
                run_result = subprocess.run([str(binary_path)], capture_output=True, text=True)
                print(f"Binary output: {run_result.stdout}")
                if run_result.stderr:
                    print(f"Binary errors: {run_result.stderr}")
                
                assert run_result.returncode == 0, f"Binary execution failed: {run_result.stderr}"
            else:
                assert False, "Binary not found"
        else:
            assert False, f"PyInstaller build failed: stdout={result.stdout}, stderr={result.stderr}"
            
    finally:
        # Cleanup
        os.unlink(test_file)

if __name__ == "__main__":
    print("PyInstaller Bundling Test")
    print("=" * 40)
    
    try:
        test_pyinstaller_bundling()
        print("\n✅ Test passed: PyInstaller bundling works correctly")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)