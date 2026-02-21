# 01 — System Overview

## What Is VidGen?

VidGen is an internal AI-powered YouTube video production pipeline. It takes raw source material (a YouTube URL or pasted text) and produces a fully composed MP4 video with AI-generated narration, AI-generated visuals, and YouTube-ready metadata — all from a single Streamlit web interface.

It is an **internal company tool** used exclusively by authorized staff. It is not a public SaaS product.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Web UI                        │
│  app/main.py + app/pages/[1-6]_*.py                     │
│  Sidebar: project selector, pipeline nav, model config   │
└────────────────────┬────────────────────────────────────┘
                     │ calls
┌────────────────────▼────────────────────────────────────┐
│                  src/ Pipeline Modules                   │
│  transcription.py → summarization.py → text_to_speech.py│
│  metadata_generation.py → image_prompting.py             │
│  image_creation.py → video_composition.py                │
└────────────────────┬────────────────────────────────────┘
                     │ calls
┌────────────────────▼────────────────────────────────────┐
│               External AI Services                       │
│  Google Cloud Speech-to-Text (STT)                       │
│  Google Cloud Text-to-Speech (TTS)                       │
│  Google Gemini (LLM via langchain-google-genai)          │
│  Google Vertex AI Imagen 4 (image generation)            │
└─────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages

Each stage reads from and writes to a project folder under `projects/<project_name>/`.

| Stage | Page | Module | Input File | Output File |
|---|---|---|---|---|
| 0 — Transcript | `1_inputs.py` | `transcription.py` | YouTube URL or pasted text | `0_transcript.txt` |
| 1 — Script | `2_script.py` | `summarization.py` | `0_transcript.txt` | `1_summary.txt` |
| 2 — Audio | `3_audio.py` | `text_to_speech.py` | `1_summary.txt` | `2_audio.mp3` |
| 3 — Metadata | `4_metadata.py` | `metadata_generation.py` | `1_summary.txt` | `4_metadata.json` |
| 4 — Image Prompts | `5_images.py` | `image_prompting.py` | `1_summary.txt` + `2_audio.mp3` | `3_image_prompts.json` + `3a_style_bible.txt` |
| 5 — Images | `5_images.py` | `image_creation.py` | `3_image_prompts.json` | `5_images/*.png` |
| 6 — Video | `6_video.py` | `video_composition.py` | `5_images/` + `2_audio.mp3` | `6_final_video.mp4` |

> **Note:** Metadata (stage 3) and Image Prompts (stage 4) can be run in parallel after script approval. They both depend only on `1_summary.txt`.

---

## Approval Gate System

Every stage has an **approval gate** before the next stage can proceed. Approvals are stored in `projects/<project_name>/config.json` under the `approvals` key.

```json
{
  "project_name": "MyProject",
  "approvals": {
    "script": true,
    "audio": false,
    "metadata": false,
    "images": false,
    "video": false
  }
}
```

The UI enforces this: each page checks that the previous stage is both **generated** (file exists) and **approved** before showing the action button for the next stage.

---

## Data Flow Diagram

```
[User] → paste text OR YouTube URL
           │
           ▼
    0_transcript.txt
           │
           ▼ (Gemini LLM)
    1_summary.txt  ──────────────────────────────────────┐
           │                                              │
           ▼ (Google TTS)              ▼ (Gemini LLM)   ▼ (Gemini LLM)
    2_audio.mp3                 4_metadata.json    3_image_prompts.json
           │                                        3a_style_bible.txt
           │                                              │
           └──────────────────────────────────────────────┤
                                                          ▼ (Vertex AI Imagen)
                                                    5_images/*.png
                                                          │
           ┌───────────────────────────────────────────────┘
           ▼
    6_final_video.mp4  (MoviePy: images + audio → MP4)
```

---

## Project Isolation

Every video production run is a **project**. Projects are fully isolated:

- Each project lives in `projects/<project_name>/`
- All pipeline files are scoped to that directory
- Switching projects in the UI immediately switches all pages to that project's data
- Projects can be in any stage of completion simultaneously

---

## Authentication Model

All Google Cloud services authenticate via **Application Default Credentials (ADC)**. The service account JSON path is set in the environment variable `GOOGLE_APPLICATION_CREDENTIALS`. This is set in `.env` and loaded by `python-dotenv` at module import time in each `src/` module.

For Windows deployment, `START.bat` resolves the absolute path to the JSON file and sets `GOOGLE_APPLICATION_CREDENTIALS` before launching Streamlit.

---

## Runtime Environment

| Environment | Details |
|---|---|
| **Linux (dev)** | Ubuntu VM, Python 3.12.3 via pyenv, `.venv/` virtualenv, run via `run_app.sh` |
| **Windows (production)** | Windows 10, Embeddable Python 3.12.3 in `tools/python/`, `venv/` created by `INSTALL.bat`, launched via `START.bat` |
| **ffmpeg** | Bundled in `tools/ffmpeg/` for Windows; system-installed on Linux |
