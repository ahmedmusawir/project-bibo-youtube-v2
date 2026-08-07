# FACT SHEET — project-bibo-youtube-v2 (VidGen)

**Phase:** 2 — Facts · **Status:** Complete
**Date:** 2026-08-07

---

## Environment Note

Python 3.12.3 is required (`.python-version`) but **not installed in this environment**.
pytest is **not available**.
Consequently: build, typecheck, and test suite cannot be executed here. Figures below that
depend on runtime verification are marked `[VERIFY: claim]`.

---

## Versions (from requirements.txt — read this session)

| Dependency | Version |
|---|---|
| Python | 3.12.3 (`.python-version`) |
| streamlit | ≥1.31.0 |
| google-genai | 1.20.0 |
| google-cloud-aiplatform | 1.97.0 |
| google-cloud-texttospeech | unpinned |
| google-cloud-speech | unpinned |
| moviepy | ≥2.2.1 |
| langchain-google-genai | ≥0.0.8 |
| pydantic | 2.11.6 |
| pytest | 8.4.1 |
| openai | 1.95.1 (fallback route only) |
| yt-dlp | 2025.6.30 |
| pydub | 0.25.1 |
| Pillow / NumPy | via moviepy |

---

## Build

**Entry point:** `streamlit run app/main.py`
**7 Streamlit pages** in `app/pages/` (verified by `ls` this session):
1. `1_inputs.py` — Paste text or YouTube URL
2. `2_script.py` — Generate / review / approve script
3. `3_audio.py` — Text-to-speech generation
4. `4_metadata.py` — Titles, descriptions, hashtags
5. `5_images.py` — AI image generation
6. `6_video.py` — Final assembly

**Build result:** [VERIFY: claim] — Cannot execute; Python 3.12.3 not installed.

---

## Types

No typechecker configured. No `mypy.ini`, `pyproject.toml` typecheck section, or `.pyrightconfig.json` found.

---

## Tests

**15 test files** found (verified by `find` this session):
- **8 unit test files** in `tests/unit/` — 18 test functions (counted via `grep -c "def test_"`)
- **7 integration test files** in `tests/integration/` — 7 test functions

**Test result:** [VERIFY: claim] — Cannot run; pytest unavailable.

**Framework:** pytest (declared in requirements.txt)
**Markers:** `integration`, `dependency` (from `pyproject.toml` read this session)

---

## Audit

No dependency audit run. `pip audit` / `safety` not configured. No CI config found.

---

## Architecture Map (read from src/ this session — not from APP_BRIEF.md)

### Pipeline (6 stages, human-gated at each)

```
Input (text / YouTube URL)
    ↓ 0_transcript.txt
Stage 1: Transcription — yt-dlp → Google Cloud STT (long-running, GCS fallback for >10MB)
    ↓ 1_summary.txt
Stage 2: Summarization — Google Gemini (config-driven model, ~920-950 word script)
    ├→ Stage 3: Text-to-Speech — Google Cloud TTS (Neural2 / Studio voices, chunked)
    ├→ Stage 4: Metadata — Google Gemini (5 titles + description + hashtags)
    └→ Stage 5: Image Prompting — Google Gemini (prompts + style bible, timed to audio)
           ↓ 5_images/
       Stage 6: Image Creation — Vertex AI Imagen (config-driven model)
           ↓ 6_final_video.mp4
       Stage 7: Video Composition — MoviePy 2.x (crossfades, 1920×1080)
```

### Key Architecture Facts

**State management:** File-based JSON (`projects/{name}/config.json`)
- Approval gates: script → audio → metadata → images → video
- Each stage must be explicitly approved before advancing
- No database; project folders are the state

**Auth enforcement:**
- `GOOGLE_APPLICATION_CREDENTIALS` → service account JSON (ADC)
- `GOOGLE_API_KEY` → Gemini API key
- Both via `os.getenv()`; no hardcoded secrets in active modules (verified by grep this session)

**Config-driven model selection:**
- `config/config.json` declares available LLM, TTS voice, and image generation models
- `src/utils/config.py` reads/writes config; Streamlit UI populates dropdowns from it
- Current v2 primary: Google Gemini / Google Cloud TTS / Vertex AI Imagen

**Alternate routes (kept open, not active):**
- `src/summarization-anthropic.py` — Anthropic Claude fallback
- `src/text_to_speech_openai.py` — OpenAI TTS fallback
- `src/image_prompting-anthropic.py` — Anthropic image prompt fallback

**Archive (legacy v1):**
- `src/archive/` — 5 files: original summarizer, img prompt generator, OpenAI variants

**Code counts (verified this session):**
- 24 Python source files in `src/`
- 13 Python files in `app/` (7 pages + main + state + utils + sidebar + init)
- 15 test files in `tests/`

---

## Docs Inventory (verified by `ls` this session)

**Factory-style docs (not application docs — internal methodology):**
- `docs/architecture.md`
- `docs/decisions.md`
- `docs/patterns.md`
- `docs/testing_strategy.md`
- `docs/vertex_ai_integration.md`
- `docs/vertex_voice_list.txt`
- `docs/MAIN DOCS/01_SYSTEM_OVERVIEW.md` through `08_ALTERNATE_AI_ROUTES.md`
- `docs/MAIN DOCS/PROMPT_ENGINEERING_MANUAL.md`
- `docs/VIDGEN_PLANS/PLAN 1.txt`, `PLAN 2.txt`

**Application-facing docs:**
- `API.md` — Module function reference
- `ARCHITECTURE.md` — Technical architecture overview
- `SETUP.md` — Linux dev setup guide
- `WINDOWS_SETUP.md` — Windows deployment guide
- `INSTALL.bat` — Windows installer
- `credentials/README.md` — Credential placement instructions

---

## Unverifiable Claims

| Claim | Status |
|---|---|
| Build passes | [VERIFY: claim] — Python 3.12.3 not installed |
| Typecheck passes | [VERIFY: claim] — No typechecker configured |
| 18 unit + 7 integration tests pass | [VERIFY: claim] — pytest unavailable |
| ~30 published videos | OMIT per operator disposition |
| Live deployment | FALSE — operator confirmed never deployed |

---

## Next: Phase 3 — Assets

Ready to request operator-supplied screenshots, diagrams, and story context.
