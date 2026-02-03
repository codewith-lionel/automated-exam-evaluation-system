@echo off
REM Quick setup script for Google Cloud Vision API

echo ========================================
echo Google Cloud Vision API Setup
echo ========================================
echo.

REM Check if credentials file path is provided
if "%1"=="" (
    echo Usage: setup_google_vision.bat "path\to\credentials.json"
    echo.
    echo Example:
    echo   setup_google_vision.bat "C:\keys\google-vision-key.json"
    echo.
    echo Get your credentials from:
    echo   https://console.cloud.google.com/apis/credentials
    echo.
    pause
    exit /b 1
)

REM Set environment variable
set GOOGLE_APPLICATION_CREDENTIALS=%~1
set OCR_ENGINE=google_vision

echo ✅ Environment variables set:
echo    GOOGLE_APPLICATION_CREDENTIALS=%GOOGLE_APPLICATION_CREDENTIALS%
echo    OCR_ENGINE=%OCR_ENGINE%
echo.

REM Check if file exists
if not exist "%GOOGLE_APPLICATION_CREDENTIALS%" (
    echo ❌ ERROR: Credentials file not found!
    echo    Path: %GOOGLE_APPLICATION_CREDENTIALS%
    echo.
    pause
    exit /b 1
)

echo ✅ Credentials file found
echo.

REM Install required package
echo 📦 Installing google-cloud-vision package...
pip install google-cloud-vision
echo.

echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo To make these changes permanent, add to your system environment variables:
echo   GOOGLE_APPLICATION_CREDENTIALS = %GOOGLE_APPLICATION_CREDENTIALS%
echo   OCR_ENGINE = google_vision
echo.
echo Or add to Windows PowerShell profile:
echo   $env:GOOGLE_APPLICATION_CREDENTIALS="%GOOGLE_APPLICATION_CREDENTIALS%"
echo   $env:OCR_ENGINE="google_vision"
echo.
echo Now you can run:
echo   python test_google_vision.py
echo   python app.py
echo.
pause
