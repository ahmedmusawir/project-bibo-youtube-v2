# 07 — Deployment

Complete reference for deploying VidGen on both Linux (development) and Windows 10 (production).

---

## Linux — Development Environment

### Prerequisites
- Ubuntu (or compatible Linux distro)
- Python 3.12.3 (via pyenv recommended)
- ffmpeg installed system-wide (`sudo apt install ffmpeg`)
- Google Cloud SDK (for ADC setup)

### Setup

```bash
# Clone the repository
git clone <repo_url>
cd project-bibo-youtube-v2

# Create virtualenv
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your actual values

# Place service account JSON
# (already present at project root as cyberize-vertex-api.json)
```

### Running the App

```bash
# Option 1: Shell script
./run_app.sh

# Option 2: Direct
streamlit run app/main.py
```

`run_app.sh` contents:
```bash
#!/bin/bash
source .venv/bin/activate
streamlit run app/main.py
```

### Python Version Management
The `.python-version` file pins the Python version to `3.12.3`. If using pyenv:
```bash
pyenv install 3.12.3
pyenv local 3.12.3
```

---

## Windows 10 — Production Deployment

### Bundle Structure

The Windows deployment is a self-contained folder that includes all runtime dependencies. The user (Coach) only needs to run two batch scripts.

```
vidgen_1/                         # App root (can be anywhere on Windows)
├── app/                          # Streamlit UI
├── src/                          # Pipeline modules
├── config/
│   └── config.json
├── credentials/
│   └── cyberize-vertex-api.json  # Pre-bundled service account
├── tools/
│   ├── ffmpeg/
│   │   ├── ffmpeg.exe
│   │   ├── ffplay.exe
│   │   └── ffprobe.exe
│   └── python/                   # Embeddable Python 3.12.3 (unzipped)
│       ├── python.exe
│       ├── python312.dll
│       ├── python312._pth
│       └── ...
├── projects/                     # Created at runtime (gitignored)
├── venv/                         # Created by INSTALL.bat (gitignored)
├── .env                          # Pre-filled with production values
├── INSTALL.bat                   # One-time setup — run once
├── START.bat                     # Daily launcher — run every time
├── requirements.txt
└── WINDOWS_SETUP.md              # End-user guide
```

### Embeddable Python

VidGen uses the **Python 3.12.3 Embeddable Package** for Windows (64-bit). This is a minimal Python distribution that does not require a system-wide Python installation.

Download: `https://www.python.org/ftp/python/3.12.3/python-3.12.3-embed-amd64.zip`

Unzip contents into `tools/python/`. The key files are:
- `python.exe` — Python interpreter
- `python312.dll` — Python runtime DLL
- `python312._pth` — Path configuration file

### `INSTALL.bat` — One-Time Setup

Run once after unzipping the bundle. Does the following:

1. **Checks** that `tools/python/python.exe` exists
2. **Checks** that `tools/ffmpeg/ffmpeg.exe` exists
3. **Sets up pip** — runs `tools/python/python.exe get-pip.py` if pip is not present
4. **Creates `venv/`** — `tools/python/python.exe -m venv venv`
5. **Installs dependencies** — `venv\Scripts\pip install -r requirements.txt`
6. **Checks for `.env`** — warns if missing
7. **Checks for credentials JSON** — warns if missing

**Critical:** The `venv/` created by `INSTALL.bat` contains absolute paths to the installation directory. It is **not portable** — it must be created on the target machine. Never copy `venv/` between machines.

### `START.bat` — Daily Launcher

Run every time to start the app. Does the following:

1. **Checks** that `venv/` exists (prompts to run `INSTALL.bat` if not)
2. **Activates** `venv\Scripts\activate.bat`
3. **Adds ffmpeg to PATH** — `set PATH=%~dp0tools\ffmpeg;%PATH%`
4. **Sets PYTHONPATH** — `set PYTHONPATH=%~dp0`
5. **Resolves credentials path** — sets `GOOGLE_APPLICATION_CREDENTIALS` to absolute path of the JSON file
6. **Launches Streamlit** — `streamlit run app\main.py`

**`%~dp0`** is a Windows batch variable that expands to the directory containing the `.bat` file. This ensures all paths are absolute regardless of where the user double-clicks the script from.

### Deployment Checklist (for Coach)

```
[ ] 1. Unzip the bundle to a permanent location (e.g., C:\VidGen\)
[ ] 2. Unzip tools/python/ contents into tools/python/
[ ] 3. Place ffmpeg.exe, ffplay.exe, ffprobe.exe in tools/ffmpeg/
[ ] 4. Place cyberize-vertex-api.json in credentials/
[ ] 5. Edit .env with correct values (GOOGLE_API_KEY, GOOGLE_STT_BUCKET, etc.)
[ ] 6. Double-click INSTALL.bat — wait for "Installation complete"
[ ] 7. Double-click START.bat — browser opens at http://localhost:8501
```

### Creating the Bundle ZIP for Coach

From the developer's Windows machine, create the ZIP excluding `venv/` and `projects/`:

```powershell
Compress-Archive -Path vidgen_1\* `
  -ExcludePattern "vidgen_1\venv\*","vidgen_1\projects\*" `
  -DestinationPath vidgen_coach.zip
```

Coach unzips this, runs `INSTALL.bat` once, then `START.bat` daily.

---

## Troubleshooting

### `ModuleNotFoundError` after `INSTALL.bat`

The most common cause is pip installing to the wrong Python. Verify:

```powershell
# Check which Python venv is using
.\venv\Scripts\python.exe --version

# Check installed packages
.\venv\Scripts\pip list

# Manually install a missing package
.\venv\Scripts\pip install <package-name>
```

### App starts but pages show errors

Check that all required env vars are set in `.env`:
```powershell
.\venv\Scripts\python.exe -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GOOGLE_API_KEY'))"
```

### `GOOGLE_STT_BUCKET` error during transcription

The GCS bucket must exist and the service account must have access. Create it in Google Cloud Console and set the bucket name in `.env`.

### Video player shows black screen in browser

This is a known Streamlit limitation with large video files. Use the **Download Video** button to download and play the video locally. The download always works correctly.

### `venv/` is corrupted or wrong path

Delete `venv/` and re-run `INSTALL.bat`:
```powershell
Remove-Item -Recurse -Force venv
# Then double-click INSTALL.bat
```

---

## Port and Network

Streamlit runs on `http://localhost:8501` by default. This is a local-only server — it is not exposed to the network. Only the machine running `START.bat` can access it.

To change the port, edit `START.bat`:
```batch
streamlit run app\main.py --server.port 8502
```

---

## Updating the App

### Linux
```bash
git pull
pip install -r requirements.txt  # if dependencies changed
```

### Windows
1. Copy updated files from Linux to Windows (or use git if available)
2. If `requirements.txt` changed: run `INSTALL.bat` again (it will reinstall into existing `venv/`)
3. Restart `START.bat`

**Files that commonly change between updates:**
- `app/pages/*.py` — UI changes
- `src/*.py` — pipeline logic changes
- `config/config.json` — model updates
- `requirements.txt` — new dependencies
