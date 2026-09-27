@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: SIH26163 - Security Assessment Platform Launcher
:: National Technical Research Organisation (NTRO) - Problem Statement 26163
:: ============================================================================

title SIH26163 Security Assessment Platform

:: 1. Determine Project Root relative to script location
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo ========================================================================
echo   SIH26163 - Security Assessment Platform
echo   Target: World Monitor (https://www.worldmonitor.app)
echo ========================================================================
echo.

:: 2. Verify Python Virtual Environment
set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python virtual environment not found at:
    echo         %PYTHON_EXE%
    echo.
    echo Please create and configure the virtual environment first:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r backend\requirements.txt
    echo.
    pause
    exit /b 1
)

:: 3. Verify Frontend Production Build
set "INDEX_HTML=%PROJECT_ROOT%frontend\dist\index.html"
if not exist "%INDEX_HTML%" (
    echo [INFO] Frontend production build not found. Building now...
    echo.
    call npm run build --prefix frontend
    if not exist "%INDEX_HTML%" (
        echo [ERROR] Frontend build failed. Please run 'npm run build' inside 'frontend\' directory.
        pause
        exit /b 1
    )
    echo [SUCCESS] Frontend bundle built successfully.
    echo.
) else (
    echo [OK] Frontend production build verified.
)

:: 4. Check for Port 8000 Conflict
netstat -ano -p tcp | findstr /R /C:":8000 .*LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [WARNING] Port 8000 is already in use by an active listener.
    echo Opening browser to http://127.0.0.1:8000...
    start http://127.0.0.1:8000
    echo.
    echo If the existing server is not responding, terminate the process on port 8000 and restart this script.
    pause
    exit /b 0
)

:: 5. Launch Browser Helper in Background after server starts
start /b "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000"

:: 6. Launch Unified Single-Service Backend (FastAPI + Static SPA)
echo.
echo [STARTING] Launching unified FastAPI server on http://127.0.0.1:8000...
echo [INFO] Serving REST API (/api) and React Frontend SPA from single service.
echo.
"%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend

pause