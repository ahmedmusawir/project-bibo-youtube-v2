# VidGen Documentation Index

This documentation is structured for use by AI Software Factory agents:
**Architect Agents**, **Designer Agents**, **Engineer Agents**, and **Cloud Engineer Agents**.

---

## Documents

| File | Purpose | Primary Audience |
|---|---|---|
| [01_SYSTEM_OVERVIEW.md](./docs/01_SYSTEM_OVERVIEW.md) | High-level architecture, pipeline, data flow | Architect, Designer |
| [02_PIPELINE_MODULES.md](./docs/02_PIPELINE_MODULES.md) | Deep-dive into every `src/` module | Engineer |
| [03_AI_MODELS_AND_INTEGRATIONS.md](./docs/03_AI_MODELS_AND_INTEGRATIONS.md) | All AI model connections, APIs, alternate routes | Architect, Engineer, Cloud Engineer |
| [04_STREAMLIT_APP.md](./docs/04_STREAMLIT_APP.md) | Streamlit UI layer, pages, state, session management | Designer, Engineer |
| [05_CONFIGURATION_AND_ENV.md](./docs/05_CONFIGURATION_AND_ENV.md) | Environment variables, config.json, model switching | Engineer, Cloud Engineer |
| [06_PROJECT_DATA_MODEL.md](./docs/06_PROJECT_DATA_MODEL.md) | Project folder structure, file naming, approval state | Architect, Engineer |
| [07_DEPLOYMENT.md](./docs/07_DEPLOYMENT.md) | Linux dev setup, Windows deployment, batch scripts | Cloud Engineer |
| [08_ALTERNATE_AI_ROUTES.md](./docs/08_ALTERNATE_AI_ROUTES.md) | OpenAI and Anthropic fallback modules (kept open) | Architect, Engineer |

---

## Quick Reference: Pipeline Stages

```
Input (text/YouTube URL)
    ↓ 0_transcript.txt
Script Generation (Gemini LLM)
    ↓ 1_summary.txt
Audio Synthesis (Google Cloud TTS)
    ↓ 2_audio.mp3
Metadata Generation (Gemini LLM)
    ↓ 4_metadata.json
Image Prompt Generation (Gemini LLM)
    ↓ 3_image_prompts.json  +  3a_style_bible.txt
Image Creation (Vertex AI Imagen)
    ↓ 5_images/
Video Composition (MoviePy)
    ↓ 6_final_video.mp4
```

---

## Tech Stack Summary

- **Runtime:** Python 3.12.3
- **UI:** Streamlit 1.54+
- **LLM:** Google Gemini via `langchain-google-genai`
- **STT:** Google Cloud Speech-to-Text (long-running recognition)
- **TTS:** Google Cloud Text-to-Speech (Neural2 / Studio voices)
- **Image Gen:** Google Vertex AI Imagen 4
- **Video:** MoviePy 2.x + Pillow + NumPy
- **Audio Download:** yt-dlp + pydub + ffmpeg
- **Auth:** Google Application Default Credentials (ADC) via service account JSON
