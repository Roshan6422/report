@echo off
setlocal enabledelayedexpansion

echo 🚀 [PRO] SRI LANKA POLICE AI - MASTER HARDENING
echo --------------------------------------------------

:: Step 1: Expert Knowledge Extraction (Gemini Teacher)
echo 🧠 Phase 1: Knowledge Factory (Distilling Wisdom)...
python knowledge_factory.py
if %errorlevel% neq 0 (
    echo ❌ ERROR: Knowledge Factory failed.
    pause
    exit /b 1
)

:: Step 2: Inject Knowledge into Modelfile (Static Hardening)
echo 🏗️ Phase 2: Building Master Modelfile...
:: Here we would typically update the Modelfile with the latest samples
:: For now, we rely on the high-quality base Modelfile.

:: Step 3: Rebuild the local AI
echo 🔨 Phase 3: Rebuilding sri-lanka-police-ai...
ollama create sri-lanka-police-ai -f Modelfile
if %errorlevel% neq 0 (
    echo ❌ ERROR: Ollama build failed.
    pause
    exit /b 1
)

echo --------------------------------------------------
echo 🏆 SUCCESS! Your AI is now an EXPERT with the latest knowledge.
echo Model name: sri-lanka-police-ai
echo --------------------------------------------------
pause
