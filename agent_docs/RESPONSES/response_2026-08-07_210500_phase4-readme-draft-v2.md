# Response: Phase 4 — README Draft v2 (Assets Included)

**Phase:** 4 — Build & Handoff · **Status:** PENDING_REVIEW
**Date:** 2026-08-07

---

## Asset Inventory (Operator-Supplied)

| Asset | URL | Layout |
|---|---|---|
| Architecture Diagram | https://res.cloudinary.com/dyb0qa58h/image/upload/v1786116539/VID%20GEN/71c4c465-4402-4559-a657-c0bb7380cf20.png | Single column, full width |
| Screenshot 1 (Inputs) | https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507722/VID%20GEN/image_1_tbttjw.png | Two-column table |
| Screenshot 2 (Script) | https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507720/VID%20GEN/image_2_ktrxtz.png | Two-column table |
| Screenshot 3 (Audio) | https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507719/VID%20GEN/image_3_wco0nq.png | Two-column table |
| Screenshot 4 (Metadata) | https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507719/VID%20GEN/image_4_gntl4s.png | Two-column table |
| Screenshot 5 (Images) | https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507719/VID%20GEN/image_3_wco0nq.png | Two-column table |
| Screenshot 6 (Video) | https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507717/VID%20GEN/image_5_d4cccm.png | Two-column table |
| Screenshot 7 (Gallery) | https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507717/VID%20GEN/image_6_xlz307.png | Two-column table |
| Screenshot 8 (Final) | https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507717/VID%20GEN/image_7_ody1kt.png | Two-column table |

**Note:** Screenshot 3 and Screenshot 5 share the same URL (`image_3_wco0nq.png`). Operator should verify this is intentional.

**Vision Limitation:** I have no image vision capability. Every caption below is inferred from `app/pages/` route code, not from actual image contents. Operator must review all captions against the real screenshots before commit.

---

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

## 🎬 Video Walkthrough

No video walkthrough supplied.

---

## Screenshots

**Pipeline Architecture**

![VidGen Pipeline Architecture](https://res.cloudinary.com/dyb0qa58h/image/upload/v1786116539/VID%20GEN/71c4c465-4402-4559-a657-c0bb7380cf20.png)

*The 7-stage VidGen pipeline: transcription → summarization → TTS → image prompting → image generation → metadata → video composition. The Researcher/Scraper path shown is planned roadmap, not shipped.*

**Streamlit UI — Pipeline Stages**

| | |
|---|---|
| ![Inputs page](https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507722/VID%20GEN/image_1_tbttjw.png) | ![Script page](https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507720/VID%20GEN/image_2_ktrxtz.png) |
| *Inputs: Paste text or a YouTube URL to start a project.* | *Script: AI generates a documentary-style script; human reviews and approves.* |
| ![Audio page](https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507719/VID%20GEN/image_3_wco0nq.png) | ![Metadata page](https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507719/VID%20GEN/image_4_gntl4s.png) |
| *Audio: Google Cloud TTS synthesizes narration with Studio voices.* | *Metadata: AI generates 5 titles, description, and hashtags for upload.* |
| ![Images page](https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507719/VID%20GEN/image_3_wco0nq.png) | ![Video page](https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507717/VID%20GEN/image_5_d4cccm.png) |
| *Images: Vertex AI Imagen creates photorealistic visuals from prompts.* | *Video: MoviePy assembles final 1920×1080 video with crossfades.* |
| ![Gallery view](https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507717/VID%20GEN/image_6_xlz307.png) | ![Final output](https://res.cloudinary.com/dyb0qa58h/image/upload/v1785507717/VID%20GEN/image_7_ody1kt.png) |
| *Gallery: Review generated images before approving.* | *Final output: Rendered video ready for download and YouTube upload.* |

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

---

## Caption Review Flags (Operator Must Verify)

I have **no vision capability**. Every caption below is inferred from `app/pages/` route code, not from actual image contents. **Operator must review all captions against real screenshots before commit.**

| # | Caption | Basis |
|---|---|---|
| 1 | "Inputs: Paste text or a YouTube URL to start a project." | Inferred from `app/pages/1_inputs.py` |
| 2 | "Script: AI generates a documentary-style script; human reviews and approves." | Inferred from `app/pages/2_script.py` + approval gate |
| 3 | "Audio: Google Cloud TTS synthesizes narration with Studio voices." | Inferred from `app/pages/3_audio.py` + `src/text_to_speech.py` |
| 4 | "Metadata: AI generates 5 titles, description, and hashtags for upload." | Inferred from `app/pages/4_metadata.py` + `src/metadata_generation.py` |
| 5 | "Images: Vertex AI Imagen creates photorealistic visuals from prompts." | Inferred from `app/pages/5_images.py` + `src/image_creation.py` |
| 6 | "Video: MoviePy assembles final 1920×1080 video with crossfades." | Inferred from `app/pages/6_video.py` + `src/video_composition.py` |
| 7 | "Gallery: Review generated images before approving." | Inferred from `app/pages/5_images.py` gallery display |
| 8 | "Final output: Rendered video ready for download and YouTube upload." | Inferred from `app/pages/6_video.py` output stage |
| Diagram | "The Researcher/Scraper path shown is planned roadmap, not shipped." | Operator instruction |

---

## Review Checklist

- [x] Phase 3 Asset Gate honored — asked operator, received assets
- [x] Diagram included with Researcher/Scraper disclaimer
- [x] 8 screenshots in two-column layout
- [x] No screenshots section omitted (assets now present)
- [x] No video walkthrough — section present but empty per operator supply
- [x] "~40-minute human-gated workflow" framed as feature, not apology
- [x] No "fully automated" or "autonomous"
- [x] No Researcher/Scraper described as shipped
- [x] No "~30 published videos" (omitted per disposition)
- [x] No live-site badge (never deployed)
- [x] Methodology line: honest arc, not anachronism
- [x] Vision limitation stated plainly; captions flagged for operator review
- [x] Response logged to disk before chat render

---

**Status:** Awaiting operator review and APPROVED before writing README.md.
