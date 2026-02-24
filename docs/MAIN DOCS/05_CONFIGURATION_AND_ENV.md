# 05 — Configuration and Environment

Complete reference for all environment variables, the `config/config.json` model configuration system, and how to manage settings at runtime.

---

## Environment Variables (`.env`)

All environment variables are loaded via `python-dotenv` (`load_dotenv()`) at module import time in each `src/` module. The `.env` file lives at the project root.

### Required Variables

| Variable | Description | Example |
|---|---|---|
| `GOOGLE_APPLICATION_CREDENTIALS` | Absolute path to Google Cloud service account JSON | `/home/user/app/credentials/cyberize-vertex-api.json` |
| `GOOGLE_API_KEY` | Gemini API key for LLM calls (script, metadata, image prompts) | `AIzaSy...` |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID for Vertex AI (Imagen) | `cyberize-prod` |
| `GOOGLE_STT_BUCKET` | GCS bucket name for Speech-to-Text audio staging | `my-stt-staging-bucket` |

### Optional Variables

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_CLOUD_REGION` | `us-central1` | Vertex AI region for Imagen |
| `GOOGLE_STT_LANG` | `en-US` | Language code for Speech-to-Text |
| `GOOGLE_TTS_VOICE` | `en-US-Studio-O` | Fallback TTS voice (if config.json unavailable) |
| `GOOGLE_TTS_LANG` | `en-US` | Fallback TTS language (if config.json unavailable) |

### Inactive / Optional API Keys

These are only needed if switching to alternate AI routes (see `docs/08_ALTERNATE_AI_ROUTES.md`):

| Variable | Used By |
|---|---|
| `OPENAI_API_KEY` | `src/transcription_openai.py`, `src/text_to_speech_openai.py` |
| `ANTHROPIC_API_KEY` | `src/summarization-anthropic.py`, `src/image_prompting-anthropic.py` |

### `.env.example`

A template file `.env.example` is included in the repository. Copy it to `.env` and fill in values:

```bash
cp .env.example .env
```

Contents of `.env.example`:
```
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
GOOGLE_STT_BUCKET=your_gcs_bucket_name
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_STT_LANG=en-US
GOOGLE_TTS_VOICE=en-US-Studio-O
GOOGLE_TTS_LANG=en-US
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

---

## `config/config.json` — Runtime Model Configuration

This file controls which AI models are used for each pipeline stage. It is read at runtime by `src/utils/config.py` and can be modified via the Streamlit UI without restarting the server.

### Full Schema

```json
{
  "llm_summarization": {
    "current": "gemini-3-flash-preview",
    "available": [
      "gemini-3-flash-preview",
      "gemini-3-pro-preview",
      "gemini-2.5-pro",
      "gemini-2.5-flash"
    ]
  },
  "llm_prompting": {
    "current": "gemini-2.5-flash",
    "available": [
      "gemini-3-flash-preview",
      "gemini-2.5-pro",
      "gemini-2.5-flash"
    ]
  },
  "tts": {
    "current_voice": "en-US-Neural2-D",
    "current_lang": "en-US",
    "available": [
      {"id": "en-US-Studio-O",  "label": "Female (Studio-O)", "lang": "en-US"},
      {"id": "en-US-Studio-M",  "label": "Male (Studio-M)",   "lang": "en-US"},
      {"id": "en-US-Neural2-D", "label": "Male (Neural2-D)",  "lang": "en-US"},
      {"id": "en-US-Neural2-F", "label": "Female (Neural2-F)","lang": "en-US"}
    ]
  },
  "image_gen": {
    "current": "imagen-4.0-ultra-generate-001",
    "available": [
      "imagen-4.0-ultra-generate-001",
      "imagen-4.0-generate-001",
      "imagen-4.0-fast-generate-001"
    ]
  }
}
```

### Configuration Keys

| Key | Controls | Changed By |
|---|---|---|
| `llm_summarization.current` | Gemini model for script generation | Script page UI or direct JSON edit |
| `llm_prompting.current` | Gemini model for metadata + image prompts | Metadata/Images page UI or direct JSON edit |
| `tts.current_voice` | Google TTS voice ID | Audio page UI or direct JSON edit |
| `tts.current_lang` | Google TTS language code | Audio page UI or direct JSON edit |
| `image_gen.current` | Vertex AI Imagen model | Images page UI or direct JSON edit |

### Adding a New Model

To add a new model option (e.g., a new Gemini release):
1. Add the model name to the relevant `available` array in `config/config.json`
2. It will immediately appear in the Streamlit UI dropdown
3. Select it in the UI to set it as `current`

No code changes required.

---

## How `load_dotenv()` Works in This App

Each `src/` module calls `load_dotenv()` at the top level (module import time). This means:

- Variables are loaded when the module is first imported
- Subsequent calls to `load_dotenv()` are no-ops unless `override=True` is passed

**Special case in `text_to_speech.py`:**
```python
load_dotenv(override=True)  # Called inside synthesize_speech()
```
This ensures any `.env` changes made after server startup are picked up before audio synthesis.

**Special case in `1_inputs.py` (YouTube transcription):**
```python
load_dotenv(project_root / ".env", override=True)
```
This explicitly loads from the project root path (not CWD) and overrides any previously loaded values. This is important because Streamlit's CWD may differ from the project root.

---

## Streamlit Configuration — `.streamlit/config.toml`

```toml
[server]
scriptRunnerTimeout = 0    # 0 = disabled (no timeout)

[browser]
gatherUsageStats = false
```

**`scriptRunnerTimeout = 0`** is critical. Without this, Streamlit kills long-running scripts after a default timeout. YouTube transcription and video composition can take 10-30+ minutes.

---

## Project-Level Configuration — `projects/<name>/config.json`

Each project has its own `config.json` for approval state tracking:

```json
{
  "project_name": "MyProject",
  "approvals": {
    "script": false,
    "audio": false,
    "metadata": false,
    "images": false,
    "video": false
  }
}
```

This file is created by `app/state.py:create_project()` and updated by `set_approval()`. It is the only persistent state for the UI approval gates.

---

## Python Version and Dependencies

**Python version:** 3.12.3 (pinned in `.python-version`)

**Key dependency versions (from `requirements.txt`):**
```
streamlit>=1.31.0
langchain-core>=0.1.27
langchain-community>=0.0.24
langchain-google-genai>=0.0.8
moviepy>=2.2.1
google-cloud-speech
google-cloud-texttospeech
google-cloud-storage
vertexai
yt-dlp
pydub
Pillow
numpy
python-dotenv
```

**Full dependency list:** See `requirements.txt` in the project root.

---

## Adding New Environment Variables

When adding a new env var to the system:

1. Add it to `.env` (local, gitignored)
2. Add it to `.env.example` with a placeholder value
3. Add it to `WINDOWS_SETUP.md` checklist
4. Document it in this file
5. If it's a Google Cloud credential or API key, also update `START.bat` if it needs special handling on Windows
