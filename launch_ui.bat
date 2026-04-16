@echo off 
cd /d "%~dp0" 
"C:\Python313\python.exe" police_desktop_ui.py 
if %ERRORLEVEL% NEQ 0 pause 
