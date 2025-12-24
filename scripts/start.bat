@echo off
REM JW zijn babbeldoos - Quick Start Script
REM ========================================

echo.
echo ============================================================
echo    JW zijn babbeldoos - AI Document Chat System
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python niet gevonden!
    echo Installeer Python van: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python gevonden!
echo.

REM Check dependencies
echo Checking dependencies...
python check_dependencies.py
if errorlevel 1 (
    echo.
    echo ERROR: Dependency check failed!
    echo Please install missing packages manually.
    echo.
    pause
    exit /b 1
)

echo.
echo Dependencies OK!
echo.

REM Start main menu
python main.py

pause
