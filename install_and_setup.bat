@echo off
setlocal EnableDelayedExpansion

echo =========================================================
echo    Sinhala Police Intelligence Tool - Automated Setup
echo =========================================================
echo.

echo [1/3] Installing Required Python Packages...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to install Python dependencies. Please ensure Python is installed and added to PATH.
    pause
    exit /b
)
echo [OK] Python dependencies installed successfully.
echo.

echo [2/3] Checking environment configuration...
if not exist ".env" (
    echo GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE > .env
    echo OPENROUTER_API_KEY=YOUR_OPENROUTER_KEY_HERE >> .env
    echo [WARNING] Created a new .env file. Please edit it to add your API keys.
) else (
    echo [OK] .env file already exists.
)
echo.

echo [3/3] Creating Desktop Shortcuts...
set "VBS_SCRIPT=%temp%\CreateShortcuts.vbs"
set "TOOL_PATH=%CD%"

:: Create VBS file to generate shortcuts
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\Police AI Desktop.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%TOOL_PATH%\run_desktop.bat" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%TOOL_PATH%" >> "%VBS_SCRIPT%"
echo oLink.Description = "Police AI Fast Report Generator" >> "%VBS_SCRIPT%"
:: You can add an icon here if needed
:: echo oLink.IconLocation = "%TOOL_PATH%\assets\icon.ico" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"

echo sLinkFile2 = oWS.SpecialFolders("Desktop") ^& "\Unified Manual Assistant.lnk" >> "%VBS_SCRIPT%"
echo Set oLink2 = oWS.CreateShortcut(sLinkFile2) >> "%VBS_SCRIPT%"
echo oLink2.TargetPath = "pythonw.exe" >> "%VBS_SCRIPT%"
echo oLink2.Arguments = "unified_manual_assistant.py" >> "%VBS_SCRIPT%"
echo oLink2.WorkingDirectory = "%TOOL_PATH%" >> "%VBS_SCRIPT%"
echo oLink2.Description = "Police Unified Manual HUD" >> "%VBS_SCRIPT%"
echo oLink2.Save >> "%VBS_SCRIPT%"

cscript /nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

echo [OK] Shortcuts created on your Desktop.
echo.
echo =========================================================
echo    Setup Complete! 
echo    You can now launch the application from your Desktop.
echo =========================================================
pause
