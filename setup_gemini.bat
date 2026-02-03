@echo off
REM Quick setup script for Google Gemini API

echo ========================================
echo Google Gemini API Setup
echo ========================================
echo.

REM Check if API key is provided
if "%1"=="" (
    echo Usage: setup_gemini.bat "YOUR_GEMINI_API_KEY"
    echo.
    echo Example:
    echo   setup_gemini.bat "AIzaSyAbc123..."
    echo.
    echo Get your API key from:
    echo   https://makersuite.google.com/app/apikey
    echo   or
    echo   https://aistudio.google.com/app/apikey
    echo.
    pause
    exit /b 1
)

REM Set environment variables
set GEMINI_API_KEY=%~1
set OCR_ENGINE=gemini

echo ✅ Environment variables set:
echo    GEMINI_API_KEY=%GEMINI_API_KEY%
echo    OCR_ENGINE=%OCR_ENGINE%
echo.

REM Install required package
echo 📦 Installing google-generativeai package...
pip install google-generativeai
echo.

echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo ⚠️  SECURITY NOTE: Keep your API key secure!
echo    Do not share it or commit it to version control
echo.
echo To make these changes permanent, add to your system environment variables:
echo   GEMINI_API_KEY = %GEMINI_API_KEY%
echo   OCR_ENGINE = gemini
echo.
echo Or add to Windows PowerShell profile:
echo   $env:GEMINI_API_KEY="%GEMINI_API_KEY%"
echo   $env:OCR_ENGINE="gemini"
echo.
echo Now you can run:
echo   python app.py
echo.
pause
