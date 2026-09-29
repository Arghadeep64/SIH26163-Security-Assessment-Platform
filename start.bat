@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: SIH26163 - Security Assessment Platform Launcher
:: National Technical Research Organisation (NTRO) - Problem Statement 26163
:: Services:
::   1. Security Assessment Platform   -> http://127.0.0.1:8000
::   2. Local World Monitor Target      -> http://127.0.0.1:3000
::   3. Controlled Security Demo Target -> http://127.0.0.1:9000
:: ============================================================================

title SIH26163 Security Assessment Platform

:: 1. Determine Project Root relative to script location
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo ========================================================================
echo   SIH26163 - Security Assessment Platform Launcher
echo   National Technical Research Organisation (NTRO)
echo ========================================================================
echo.
echo [INFO] Project Root : %PROJECT_ROOT%
echo.

:: 2. Verify Python Virtual Environment
set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"
set "UVICORN_EXE=%PROJECT_ROOT%.venv\Scripts\uvicorn.exe"

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

if not exist "%UVICORN_EXE%" (
    echo [ERROR] Uvicorn executable not found at:
    echo         %UVICORN_EXE%
    echo.
    echo Please install dependencies:
    echo   .venv\Scripts\pip install -r backend\requirements.txt
    echo.
    pause
    exit /b 1
)

echo [OK] Python virtual environment verified.
echo.

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
    echo.
)

:: 4. Service 1: Local World Monitor Target (Port 3000)
echo ------------------------------------------------------------------------
echo [1/3] Local World Monitor Target (Port 3000)
echo       Target: http://127.0.0.1:3000
echo ------------------------------------------------------------------------
(netstat -ano -p tcp | findstr :3000 | findstr LISTENING) >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 3000 is already in use by an active listener.
    echo           Reusing existing process on http://127.0.0.1:3000.
    echo.
) else (
    echo [STARTING] Launching World Monitor local server on http://127.0.0.1:3000...
    start "SIH26163 - Local World Monitor Target (Port 3000)" /d "%PROJECT_ROOT%" cmd /k "title SIH26163 - Local World Monitor Target (Port 3000) && "%PYTHON_EXE%" research\run_local_worldmonitor.py 3000"
    echo [SUCCESS] Local World Monitor target started in a separate window.
    echo.
)

:: 5. Service 2: Controlled Demonstration Target (Port 9000)
echo ------------------------------------------------------------------------
echo [2/3] Controlled Security Demo Target (Port 9000)
echo       Target: http://127.0.0.1:9000
echo ------------------------------------------------------------------------
(netstat -ano -p tcp | findstr :9000 | findstr LISTENING) >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 9000 is already in use by an active listener.
    echo           Reusing existing process on http://127.0.0.1:9000.
    echo.
) else (
    echo [STARTING] Launching Controlled Demo Target on http://127.0.0.1:9000...
    start "SIH26163 - Controlled Demo Target (Port 9000)" /d "%PROJECT_ROOT%" cmd /k "title SIH26163 - Controlled Demo Target (Port 9000) && "%UVICORN_EXE%" main:app --app-dir demo-target --host 127.0.0.1 --port 9000"
    echo [SUCCESS] Controlled demo target started in a separate window.
    echo.
)

:: 6. Service 3: Security Assessment Platform Backend + UI (Port 8000)
echo ------------------------------------------------------------------------
echo [3/3] Security Assessment Platform (Port 8000)
echo       Platform URL: http://127.0.0.1:8000
echo ------------------------------------------------------------------------
(netstat -ano -p tcp | findstr :8000 | findstr LISTENING) >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 8000 is already in use by an active listener.
    echo Opening browser to http://127.0.0.1:8000...
    start http://127.0.0.1:8000
    echo.
    echo If the existing server is not responding, terminate the process on port 8000 and restart this script.
    echo.
    pause
    exit /b 0
)

:: Launch Browser Helper in Background after server starts
start /b "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000"

echo [STARTING] Launching unified FastAPI server on http://127.0.0.1:8000...
echo [INFO] Serving REST API (/api) and React Frontend SPA from single service.
echo.
"%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend

pause
