@echo off
REM Build script for JSON Analysis Tool
echo Building JSON Analysis Tool executable...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install required packages
    pause
    exit /b 1
)

REM Build the executable
echo Building executable...
pyinstaller --onefile --windowed --name "JSON_Analysis_Tool" --icon=icon.ico analyze_json_file_batch.py

if errorlevel 1 (
    echo ERROR: Failed to build executable
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Executable is located in: dist\JSON_Analysis_Tool.exe
echo.
pause