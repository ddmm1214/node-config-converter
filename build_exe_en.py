#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build yaml_to_v2rayn.py as EXE file using PyInstaller
"""

import os
import sys
import subprocess

def build_exe():
    """
    Build EXE file using PyInstaller
    """
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller installed, version:", PyInstaller.__version__)
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installation completed")

    # Build command arguments
    cmd = [
        "pyinstaller",
        "--name=node-converter",           # Program name
        "--windowed",                      # No console window
        "--onefile",                       # Single file mode
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",  # Icon
        "--add-data=README.md;.",          # Add extra files
        "--clean",                         # Clean before build
        "--distpath=dist",                 # Output directory
        "--workpath=build",                # Work directory
        "yaml_to_v2rayn.py"                # Main script
    ]

    # Remove empty arguments
    cmd = [arg for arg in cmd if arg]

    # Execute build command
    print("Starting EXE build...")
    print("Command:", " ".join(cmd))
    
    # Handle GitHub Actions environment with UTF-8 encoding
    import locale
    if os.getenv('GITHUB_ACTIONS'):
        # GitHub Actions environment
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            print("Build failed:")
            print(result.stderr)
            sys.exit(1)
        else:
            print("Build output:")
            print(result.stdout)
    else:
        # Local environment
        subprocess.call(cmd)
        
    print("Build completed!")
    print("EXE file generated in dist directory")

if __name__ == "__main__":
    build_exe()