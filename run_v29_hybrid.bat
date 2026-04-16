@echo off
setlocal

if "%~1"=="" (
    echo [ERROR] Please drag and drop a Sinhala Police PDF onto this file.
    pause
    exit /b 1
)

echo ======================================================
echo 🛡️ HYBRID MASTER: GEMINI VISION + OLLAMA LOCAL
echo ======================================================
echo.
echo [1/2] OCR: Gemini Vision Engaging...
echo [2/2] Translation: Local Ollama (Super-Fast) Processing...
echo.

python v29_hybrid_master.py "%~1"

echo.
echo [DONE] Hybrid Processing complete!
echo [DONE] Results: outputs\v29_hybrid_results
echo.
pause
