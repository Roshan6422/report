@echo off
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: verify_pdf_reports.bat "path\to\sinhala_report.pdf"
  exit /b 1
)
python verify_sinhala_pdf_reports.py %*
exit /b %ERRORLEVEL%
