@echo off
REM Quick start script for backend

cd /d "%~dp0..\backend"

echo.
echo ========================================
echo   Tableau App Backend Server
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup first:
    echo   1. cd backend
    echo   2. python -m venv venv
    echo   3. venv\Scripts\activate
    echo   4. pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Starting FastAPI server...
echo.
echo Backend will be available at: http://localhost:8000
echo API docs available at: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo.

python -m app.main

pause
