@echo off
echo 🚀 REBUILDING SRI LANKA POLICE AI (MASTER V2)...
echo --------------------------------------------------

:: Ensure Ollama is running
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Ollama is not running. Please start Ollama and try again.
    exit /b 1
)

:: Rebuild the model
ollama create sri-lanka-police-ai -f Modelfile

echo --------------------------------------------------
echo ✅ SUCCESS! The Police AI has been updated with the latest knowledge.
echo Model name: sri-lanka-police-ai
pause
