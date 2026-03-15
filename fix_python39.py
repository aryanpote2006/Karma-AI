"""
Fix Python39 to Python312 Migration for KARMA AI
This script helps migrate from Python 3.9 to Python 3.12
"""

import sys
import os
import subprocess
import shutil

def get_python_executable():
    """Get the current Python executable path"""
    return sys.executable

def check_python_version():
    """Check current Python version"""
    version = sys.version_info
    print(f"Current Python version: {version.major}.{version.minor}.{version.micro}")
    return version.major, version.minor

def clean_pycache():
    """Remove all __pycache__ directories"""
    print("Cleaning __pycache__ directories...")
    for root, dirs, files in os.walk('.'):
        for dir in dirs:
            if dir == '__pycache__':
                path = os.path.join(root, dir)
                try:
                    shutil.rmtree(path)
                    print(f"  Removed: {path}")
                except Exception as e:
                    print(f"  Failed to remove {path}: {e}")

def reinstall_dependencies():
    """Reinstall all dependencies with current Python"""
    print("\nReinstalling dependencies...")
    
    # Upgrade pip first
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    
    # Install requirements
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_file):
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
    
    # Reinstall pycaw and comtypes specifically (needed for volume control)
    print("\nReinstalling audio control dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--force-reinstall', 'pycaw'])
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--force-reinstall', 'comtypes'])

def clear_pip_cache():
    """Clear pip cache"""
    print("\nClearing pip cache...")
    subprocess.run([sys.executable, '-m', 'pip', 'cache', 'purge'])

def verify_installations():
    """Verify key packages are installed"""
    print("\nVerifying installations...")
    
    packages = [
        'speech_recognition',
        'pyttsx3', 
        'pyaudio',
        'pycaw',
        'comtypes',
        'pyautogui',
        'customtkinter',
        'opencv_python',
        'numpy'
    ]
    
    for package in packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")

if __name__ == "__main__":
    print("=" * 60)
    print("KARMA AI - Python39 to Python312 Migration Fix")
    print("=" * 60)
    
    major, minor = check_python_version()
    
    if major == 3 and minor == 12:
        print("\n✓ Python 3.12 detected!")
    else:
        print(f"\n⚠ Warning: Expected Python 3.12, but found {major}.{minor}")
    
    print("\n" + "=" * 60)
    print("Step 1: Cleaning cache")
    print("=" * 60)
    clean_pycache()
    
    print("\n" + "=" * 60)
    print("Step 2: Clearing pip cache")
    print("=" * 60)
    clear_pip_cache()
    
    print("\n" + "=" * 60)
    print("Step 3: Reinstalling dependencies")
    print("=" * 60)
    reinstall_dependencies()
    
    print("\n" + "=" * 60)
    print("Step 4: Verifying installations")
    print("=" * 60)
    verify_installations()
    
    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)
    print("\nTo run KARMA AI, use:")
    print(f"  {sys.executable} karma_ai/main.py")
    print("\nOr for voice-only mode:")
    print(f"  {sys.executable} karma_ai/main.py --voice-only")
