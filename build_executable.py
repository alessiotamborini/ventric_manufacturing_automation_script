#!/usr/bin/env python3
"""
Simple build script to create Windows executable
Run this script to build the executable
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("✗ Failed to install requirements")
        return False
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Detect platform and adjust accordingly
    import platform
    current_platform = platform.system()
    
    print(f"Current platform: {current_platform}")
    
    if current_platform != "Windows":
        print("⚠️  WARNING: You're building on macOS/Linux but targeting Windows")
        print("   The executable may not work on Windows.")
        print("   For best results, build on a Windows machine or use Wine.")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",              # Single executable file
        "--windowed",             # No console window (GUI only)
        "--name", "JSON_Analysis_Tool",  # Executable name
        "--distpath", "dist",     # Output directory
        "--workpath", "build",    # Build directory
        "--clean",                # Clean build
        "analyze_json_file_batch.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✓ Executable built successfully!")
        print("✓ Location: dist/JSON_Analysis_Tool.exe")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to build executable")
        return False

def main():
    """Main build process"""
    print("JSON Analysis Tool - Build Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("analyze_json_file_batch.py"):
        print("✗ Error: analyze_json_file_batch.py not found")
        print("Please run this script from the same directory as the main script")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Build executable
    if not build_executable():
        return
    
    print("\n" + "=" * 40)
    print("Build completed successfully!")
    print("Your executable is ready: dist/JSON_Analysis_Tool.exe")
    print("\nTo distribute:")
    print("1. Copy the entire 'dist' folder to the target Windows machine")
    print("2. Run JSON_Analysis_Tool.exe")

if __name__ == "__main__":
    main()