@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   VidGen - One-Time Installation
echo ============================================================
echo.

:: Get the directory where this script lives
set "APP_DIR=%~dp0"
cd /d "%APP_DIR%"

:: -----------------------------------------------------------
:: Step 1: Check for Embeddable Python in tools/python/
:: -----------------------------------------------------------
echo [1/5] Checking for Python...

if exist "tools\python\python.exe" (
    echo   Found embeddable Python at tools\python\python.exe
    set "PYTHON_EXE=%APP_DIR%tools\python\python.exe"
) else (
    echo   ERROR: Embeddable Python not found at tools\python\python.exe
    echo.
    echo   Please download Python 3.12 embeddable package from:
    echo   https://www.python.org/ftp/python/3.12.3/python-3.12.3-embed-amd64.zip
    echo.
    echo   Extract the contents into the tools\python\ folder so that
    echo   tools\python\python.exe exists.
    echo.
    pause
    exit /b 1
)

:: -----------------------------------------------------------
:: Step 2: Check for ffmpeg in tools/ffmpeg/
:: -----------------------------------------------------------
echo [2/5] Checking for ffmpeg...

if exist "tools\ffmpeg\ffmpeg.exe" (
    echo   Found ffmpeg at tools\ffmpeg\ffmpeg.exe
) else (
    echo   ERROR: ffmpeg.exe not found at tools\ffmpeg\ffmpeg.exe
    echo.
    echo   Please copy ffmpeg.exe, ffplay.exe, and ffprobe.exe
    echo   from C:\ffmpeg\bin\ into the tools\ffmpeg\ folder.
    echo.
    pause
    exit /b 1
)

:: -----------------------------------------------------------
:: Step 3: Enable pip in embeddable Python
:: -----------------------------------------------------------
echo [3/5] Setting up pip for embeddable Python...

:: The embeddable Python ships with a ._pth file that blocks pip.
:: We need to uncomment "import site" in it to enable pip/venv.
set "PTH_FILE="
for %%f in (tools\python\python*._pth) do set "PTH_FILE=%%f"

if defined PTH_FILE (
    :: Check if "import site" is already uncommented
    findstr /b /c:"import site" "!PTH_FILE!" >nul 2>&1
    if errorlevel 1 (
        echo   Enabling site-packages in !PTH_FILE!...
        :: Replace "#import site" with "import site"
        powershell -Command "(Get-Content '!PTH_FILE!') -replace '#import site','import site' | Set-Content '!PTH_FILE!'"
    ) else (
        echo   site-packages already enabled.
    )
) else (
    echo   WARNING: Could not find ._pth file. Pip may not work correctly.
)

:: Install pip if not present
if not exist "tools\python\Scripts\pip.exe" (
    echo   Installing pip...
    :: Download get-pip.py
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'tools\python\get-pip.py'"
    "!PYTHON_EXE!" "tools\python\get-pip.py" --no-warn-script-location
    if errorlevel 1 (
        echo   ERROR: Failed to install pip.
        pause
        exit /b 1
    )
    del "tools\python\get-pip.py" 2>nul
) else (
    echo   pip already installed.
)

:: -----------------------------------------------------------
:: Step 4: Create virtual environment
:: -----------------------------------------------------------
echo [4/5] Creating virtual environment...

set "PIP_EXE=%APP_DIR%tools\python\Scripts\pip.exe"

if not exist "venv" (
    :: Install virtualenv using embeddable Python's pip
    "!PIP_EXE!" install virtualenv --no-warn-script-location >nul 2>&1
    "!PYTHON_EXE!" -m virtualenv venv
    if errorlevel 1 (
        echo   ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo   Virtual environment created.
) else (
    echo   Virtual environment already exists.
)

:: -----------------------------------------------------------
:: Step 5: Install dependencies
:: -----------------------------------------------------------
echo [5/5] Installing Python dependencies (this may take a few minutes)...

call venv\Scripts\activate.bat

pip install -r requirements.txt --no-warn-script-location
if errorlevel 1 (
    echo.
    echo   ERROR: Failed to install some dependencies.
    echo   Check the output above for details.
    pause
    exit /b 1
)

:: -----------------------------------------------------------
:: Step 6: Set up .env if not present
:: -----------------------------------------------------------
if not exist ".env" (
    echo.
    echo   Creating .env from .env.example...
    copy .env.example .env >nul
    echo.
    echo   *** IMPORTANT: Edit the .env file with your actual API keys ***
    echo   Open .env in Notepad and fill in your values.
    echo.
)

:: -----------------------------------------------------------
:: Step 7: Check for credentials
:: -----------------------------------------------------------
if not exist "credentials\cyberize-vertex-api.json" (
    echo.
    echo   *** IMPORTANT: Service account key not found ***
    echo   Place your cyberize-vertex-api.json file in the credentials\ folder.
    echo.
)

:: -----------------------------------------------------------
:: Done!
:: -----------------------------------------------------------
echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo   Next steps:
echo   1. Make sure .env has your API keys filled in
echo   2. Make sure credentials\cyberize-vertex-api.json exists
echo   3. Double-click START.bat to launch VidGen
echo.
pause
