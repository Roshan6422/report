@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

echo =========================================================
echo    Sinhala Police Intelligence Tool - Automated Setup
echo =========================================================
echo.

:: ── 0. Python Check ────────────────────────────────────────
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ and add to system PATH.
    pause
    exit /b 1
)
echo [OK] Python detected.
echo.

:: ── 1. Install Dependencies ────────────────────────────────
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found in current directory.
    pause
    exit /b 1
)

echo [1/3] Installing Required Python Packages...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to install dependencies. Check internet/connection.
    pause
    exit /b 1
)
echo [OK] Python dependencies installed successfully.
echo.

:: ── 2. Environment Config ──────────────────────────────────
echo [2/3] Checking environment configuration...
if not exist ".env" (
    (
        echo # Sinhala Police AI - Environment Configuration
        echo GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE
        echo OPENROUTER_API_KEY=YOUR_OPENROUTER_KEY_HERE
        echo SINHALA_FIRST_PIPELINE=1
        echo AI_DISPATCH_MODE=sequential
    ) > .env
    echo [WARNING] Created a new .env file. Please edit it to add your API keys.
) else (
    echo [OK] .env file already exists.
)
echo.

:: ── 3. Desktop Shortcuts (Space-Safe VBS) ─────────────────
echo [3/3] Creating Desktop Shortcuts...
set "VBS_SCRIPT=%temp%\PoliceAISetup.vbs"
set "TOOL_PATH=%CD%"

:: Use """ to safely quote paths containing spaces in VBS
(
    echo Set oWS = WScript.CreateObject("WScript.Shell")
    echo.
    echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\Police AI Desktop.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile)
    echo oLink.TargetPath = """%TOOL_PATH%\run_desktop.bat"""
    echo oLink.WorkingDirectory = """%TOOL_PATH%"""
    echo oLink.Description = "Police AI Fast Report Generator"
    echo oLink.Save
    echo.
    echo sLinkFile2 = oWS.SpecialFolders("Desktop") ^& "\Unified Manual Assistant.lnk"
    echo Set oLink2 = oWS.CreateShortcut(sLinkFile2)
    echo oLink2.TargetPath = "pythonw.exe"
    echo oLink2.Arguments = """%TOOL_PATH%\unified_manual_assistant.py"""
    echo oLink2.WorkingDirectory = """%TOOL_PATH%"""
    echo oLink2.Description = "Police Unified Manual HUD"
    echo oLink2.Save
) > "%VBS_SCRIPT%"

cscript /nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

echo [OK] Shortcuts created on your Desktop.
echo.
echo =========================================================
echo    ✅ Setup Complete! 
echo    You can now launch the application from your Desktop.
echo =========================================================
pause