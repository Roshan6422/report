@echo off
title PDF Translator Pro Setup
echo ===========================================
echo PDF Translator Pro - Setup and Run
echo ===========================================
echo.
echo Installing required dependencies...
python -m pip install -r requirements.txt
cls

echo ===========================================
echo Launching PDF Translator Pro...
echo ===========================================
echo.
echo Please wait while the application loads...
python app.py
pause
