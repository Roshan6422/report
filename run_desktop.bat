@echo off
echo "============================================================"
echo "  Sinhala Police AI | Desktop Intelligence Tool Launcher  "
echo "============================================================"
echo.
echo Launching Application...
python police_desktop_ui.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo "❌ ERROR: Failed to launch application."
    echo "Make sure Python is installed and dependencies are met."
    pause
)
