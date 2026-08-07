# Response: Phase 4 — README Draft (Review Before Write)

**Phase:** 4 — Build & Handoff · **Status:** PENDING_REVIEW
**Date:** 2026-08-07

---

## Authorized Write Surface

`README.md` only. No `.gitignore` or `.env.example` edits per operator disposition.

## Assets

No screenshots, diagrams, or video walkthroughs supplied by operator. Screenshots and Video Walkthrough sections are **omitted** entirely.

## Proposed README

```markdown
# VidGen

**A human-gated AI pipeline that turns a YouTube URL or article text into a narrated documentary video with AI-generated visuals.**

[![Python](https://img.shields.io/badge/Python-3.12.3-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-%E2%89%A51.31.0-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

---

## Why This Exists

Creating a professional documentary-style YouTube video from raw content traditionally takes days: transcribing audio, writing a tight script, recording narration, sourcing or generating visuals, editing everything together, and writing metadata and thumbnails. Each step requires a different tool and a different skill set.

VidGen collapses that into a ~40-minute human-gated workflow. AI executes each stage — transcription, summarization, narration, image generation, and video assembly — but a human reviews the result and explicitly approves it before the pipeline advances. This is not "fully automated"; the gate is the feature. File-based state keeps the system lightweight (no database), and a config-driven model layer lets you swap LLMs, voices, and image generators without touching core logic. Hand-built end to end; later brought under the App Factory, an AI-augmented delivery methodology.

---

## What's Inside

- **YouTube-to-Transcript** — Downloads audio via yt-dlp and transcribes with Google Cloud Speech-to-Text, with automatic GCS fallback for files over 10 MB (`src/transcription.py`)
- **Script Summarization** — Converts raw transcripts into 920–950 word documentary scripts using Google Gemini, with config-driven model selection (`src/summarization.py`, `config/config.json`)
- **Text-to-Speech** — Synthesizes narration with Google Cloud TTS (Neural2 / Studio voices), chunked for long scripts, with voice selection from config (`src/text_to_speech.py`)
- **Image Prompting + Style Bible** — Generates contextual image prompts and a unified visual style guide timed to audio duration (`src/image_prompting.py`)
- **AI Image Generation** — Creates photorealistic visuals via Vertex AI Imagen with config-driven model switching (`src/image_creation.py`)
- **Metadata Generation** — Produces 5 SEO titles, description, and hashtags via Google Gemini (`src/metadata_generation.py`)
- **Thumbnail Generation** — Generates catchy one-liner overlays for video thumbnails (`src/thumbnail_generation.py`)
- **Video Composition** — Assembles final 1920×1080 video with crossfades and audio sync using MoviePy 2.x (`src/video_composition.py`)

---

## Documentation

| Document | Contents |
|---|---|
| [API.md](API.md) | Module and function reference |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture and design decisions |
| [SETUP.md](SETUP.md) | Linux / macOS development setup |
| [WINDOWS_SETUP.md](WINDOWS_SETUP.md) | Windows deployment with bundled ffmpeg and embeddable Python |

---

## Quickstart

Requires **Python 3.12.3**, **FFmpeg**, and a **Google Cloud Platform** account.

```bash
git clone https://github.com/ahmedmusawir/project-bibo-youtube-v2.git
cd project-bibo-youtube-v2

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your GOOGLE_API_KEY, GOOGLE_APPLICATION_CREDENTIALS,
# GOOGLE_CLOUD_PROJECT, and GOOGLE_STT_BUCKET
```

Run the Streamlit UI:

```bash
streamlit run app/main.py
```

Or run the CLI pipeline:

```bash
python main.py
```

### Verify the build

```bash
pytest tests/unit/ -v        # → 18 unit tests
pytest tests/integration/ -m integration -v  # → 7 integration tests (requires credentials)
```

> **Note:** Integration tests call live Google Cloud APIs and require valid credentials.

---

Built by **[Ahmed Musawir](https://github.com/ahmedmusawir)** — Software Architect & AI Engineer.  
Hand-built end to end; later brought under the App Factory, an AI-augmented delivery methodology.
```

## Review Checklist

- [x] No screenshots section (no assets supplied)
- [x] No video walkthrough (no assets supplied)
- [x] "~40-minute human-gated workflow" framed as feature, not apology
- [x] No "fully automated" or "autonomous"
- [x] No Researcher/Scraper mention
- [x] No "~30 published videos" (omitted per disposition)
- [x] No live-site badge (never deployed)
- [x] Methodology line: honest arc, not anachronism
- [x] Quickstart test counts: 18 unit + 7 integration, counted by grep this session
- [x] Integration tests flagged as requiring credentials

---

**Status:** Awaiting operator review and APPROVED before writing README.md.
