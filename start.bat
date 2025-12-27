@echo off
REM WhereSpace Unified Application Startup Script
REM This script starts the new unified Flask application

echo ============================================================
echo WhereSpace - Starting Unified Application
echo ============================================================
echo.

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if in correct directory
if not exist "app.py" (
    echo ERROR: app.py not found
    echo Please run this script from the WhereSpace directory
    pause
    exit /b 1
)

REM Start the application
echo Starting WhereSpace on http://127.0.0.1:5000
echo Press Ctrl+C to stop
echo.
python app.py

pause
