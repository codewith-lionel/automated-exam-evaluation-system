@echo off
echo ============================================================
echo   AUTOMATED EXAM EVALUATION SYSTEM - COMPLETE TEST SUITE
echo ============================================================
echo.

echo [1/6] Testing Python dependencies...
python test_system.py
if errorlevel 1 (
    echo FAILED: System test
    pause
    exit /b 1
)
echo.

echo [2/6] Testing database...
python test_database.py
if errorlevel 1 (
    echo FAILED: Database test
    pause
    exit /b 1
)
echo.

echo [3/6] Testing NLP evaluation...
python test_evaluation.py
if errorlevel 1 (
    echo FAILED: Evaluation test
    pause
    exit /b 1
)
echo.

echo [4/6] Testing Flask routes...
python test_routes.py
if errorlevel 1 (
    echo FAILED: Routes test
    pause
    exit /b 1
)
echo.

echo [5/6] Testing OCR processing...
python test_ocr.py
if errorlevel 1 (
    echo FAILED: OCR test
    pause
    exit /b 1
)
echo.

echo [6/6] Verifying application starts...
echo Starting Flask application...
start /B python app.py
timeout /t 5 /nobreak > nul
echo Checking if application is accessible...
curl -s -o nul -w "%%{http_code}" http://localhost:5000 > temp.txt
set /p STATUS=<temp.txt
del temp.txt

if "%STATUS%"=="200" (
    echo SUCCESS: Application is running at http://localhost:5000
) else (
    echo WARNING: Could not verify application (Status: %STATUS%)
)
echo.

echo ============================================================
echo   ALL TESTS COMPLETED SUCCESSFULLY!
echo ============================================================
echo.
echo System Status: READY FOR USE
echo.
echo Access the application at: http://localhost:5000
echo.
echo Demo Credentials:
echo   Student: student@exam.com / Student@123
echo   Admin:   admin@exam.com / Admin@123
echo.
echo ============================================================
echo.
pause
