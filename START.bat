@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   VidGen - Starting Application
echo ============================================================
echo.

:: Get the directory where this script lives
set "APP_DIR=%~dp0"
cd /d "%APP_DIR%"

:: -----------------------------------------------------------
:: Pre-flight checks
:: -----------------------------------------------------------

:: Check venv exists
if not exist "venv\Scripts\activate.bat" (
    echo   ERROR: Virtual environment not found.
    echo   Please run INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

:: Check .env exists
if not exist ".env" (
    echo   ERROR: .env file not found.
    echo   Please run INSTALL.bat first, then edit .env with your API keys.
    echo.
    pause
    exit /b 1
)

:: -----------------------------------------------------------
:: Set up environment
:: -----------------------------------------------------------

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Add ffmpeg to PATH
set "PATH=%APP_DIR%tools\ffmpeg;%PATH%"

:: Set PYTHONPATH so src/ and app/ imports work
set "PYTHONPATH=%APP_DIR%"

:: Set credentials path (resolve relative path from .env to absolute)
:: This ensures GOOGLE_APPLICATION_CREDENTIALS works from any CWD
for /f "tokens=1,2 delims==" %%a in ('findstr /b "GOOGLE_APPLICATION_CREDENTIALS" .env') do (
    set "CRED_PATH=%%b"
)
if defined CRED_PATH (
    :: Trim spaces
    set "CRED_PATH=!CRED_PATH: =!"
    :: Convert to absolute path if relative
    if not "!CRED_PATH:~1,1!"==":" (
        set "GOOGLE_APPLICATION_CREDENTIALS=%APP_DIR%!CRED_PATH!"
    )
)

:: -----------------------------------------------------------
:: Launch Streamlit
:: -----------------------------------------------------------
echo   Starting VidGen...
echo   The app will open in your browser automatically.
echo.
echo   To stop the app, close this window or press Ctrl+C.
echo ============================================================
echo.

streamlit run app/main.py --server.port 8501 --browser.gatherUsageStats false

pause
