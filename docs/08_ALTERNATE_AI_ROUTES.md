# 08 — Alternate AI Routes

VidGen was built with multiple AI provider routes implemented in parallel. The **active pipeline** uses Google Cloud services exclusively. The alternate routes (OpenAI and Anthropic) are fully implemented, tested, and kept in the codebase as ready-to-activate fallbacks.

This document covers what each alternate route does, how it differs from the active route, and exactly what to change to activate it.

---

## Why Alternate Routes Exist

1. **Provider redundancy** — if Google services have an outage or pricing change, a switch can be made quickly
2. **Quality comparison** — different models produce different script/image quality; alternates allow A/B testing
3. **Feature differences** — some providers have capabilities the primary doesn't (e.g., Whisper handles audio differently than Google STT)
4. **Future-proofing** — the AI landscape changes rapidly; keeping routes open avoids re-engineering from scratch

---

## Route Status Summary

| Stage | Active Route | Alternate Route(s) | Status |
|---|---|---|---|
| Transcription (STT) | Google Cloud STT | OpenAI Whisper | Inactive — file present, not imported |
| Script Generation | Google Gemini | Anthropic Claude | Inactive — file present, not imported |
| Audio Synthesis (TTS) | Google Cloud TTS | OpenAI TTS | Inactive — file present, not imported |
| Image Prompts | Google Gemini | Anthropic Claude | Inactive — file present, not imported |
| Image Generation | Vertex AI Imagen | *(none currently)* | N/A |
| Video Composition | MoviePy | *(none currently)* | N/A |

---

## Alternate Route 1: OpenAI Whisper — Transcription

**File:** `src/transcription_openai.py`

**Model:** `whisper-1` (OpenAI Whisper API)

**Auth:** `OPENAI_API_KEY`

### How It Differs from Active Route

| Aspect | Active (Google STT) | Alternate (OpenAI Whisper) |
|---|---|---|
| API type | Async long-running | Synchronous per-chunk |
| File size limit | Unlimited (via GCS) | 25MB per request |
| Chunking strategy | None (GCS handles it) | 10-minute chunks (600,000ms) |
| Audio format | FLAC (converted from MP3) | MP3 (no conversion needed) |
| GCS dependency | Required | None |
| Language detection | Manual (`GOOGLE_STT_LANG`) | Auto-detect |
| Punctuation | `enable_automatic_punctuation=True` | Built into Whisper |

### Key Implementation Details

```python
CHUNK_DURATION_MS = 10 * 60 * 1000  # 10 minutes per chunk

def _split_audio_into_chunks(audio_path: str) -> list[str]:
    # Splits MP3 into 10-minute chunks using pydub
    # Returns list of temp file paths
    # If audio <= 10 min, returns [original_path] (no split)

def transcribe_youtube_audio(youtube_url: str, output_transcript_path: str):
    # 1. Download audio via yt-dlp (same as active route)
    # 2. Split into 10-min chunks if needed
    # 3. For each chunk: client.audio.transcriptions.create(model="whisper-1")
    # 4. Concatenate all transcript parts
    # 5. Write to output_transcript_path
    # 6. Clean up temp files
```

### How to Activate

In `app/pages/1_inputs.py`, change the import:
```python
# Current (active):
from src.transcription import transcribe_youtube_audio

# Switch to OpenAI Whisper:
from src.transcription_openai import transcribe_youtube_audio
```

Ensure `OPENAI_API_KEY` is set in `.env`.

### Trade-offs

- **Pro:** No GCS bucket required — simpler setup for new deployments
- **Pro:** No FLAC conversion step — faster start
- **Con:** 25MB limit per chunk — very long videos may have quality issues at chunk boundaries
- **Con:** Synchronous — no progress feedback during transcription of long videos
- **Con:** OpenAI API cost vs. Google STT cost

---

## Alternate Route 2: Anthropic Claude — Script Generation

**File:** `src/summarization-anthropic.py`

**Model:** `claude-3-5-sonnet-20240620`

**Auth:** `ANTHROPIC_API_KEY`

**Library:** `langchain-anthropic` → `ChatAnthropic`

### How It Differs from Active Route

| Aspect | Active (Google Gemini) | Alternate (Anthropic Claude) |
|---|---|---|
| Model | `gemini-3-flash-preview` (configurable) | `claude-3-5-sonnet-20240620` (hardcoded) |
| Temperature | `0.5` | `0.8` |
| max_tokens | Not set (model default) | `4096` (explicitly set) |
| Retries | Not configured | `max_retries=3` |
| Timeout | Not configured | `timeout=None` |
| Config-driven | Yes (via `config.json`) | No (hardcoded model) |

### Key Implementation Details

```python
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.8,
    max_tokens=4096,
    timeout=None,
    max_retries=3,
)
```

**Prompt differences:** The Anthropic version of the prompt includes a "Key Takeaways" section structure that was later removed from the active Gemini prompt. If activating, update the prompt to match the current active version (no Key Takeaways, no special characters, must end with "Thanks for watching").

### How to Activate

In `app/pages/2_script.py`, change the import:
```python
# Current (active):
from src.summarization import summarize_transcript

# Switch to Anthropic Claude:
from src.summarization_anthropic import summarize_transcript
```

Note: The filename uses a hyphen (`summarization-anthropic.py`) which is not a valid Python module name for direct import. Rename to `summarization_anthropic.py` before activating.

Ensure `ANTHROPIC_API_KEY` is set in `.env`.

### Trade-offs

- **Pro:** Claude 3.5 Sonnet is highly capable for long-form writing
- **Pro:** `max_retries=3` built in — more resilient to transient API errors
- **Con:** `max_tokens=4096` may cause truncation for longer scripts (this was the bug fixed in the active route by removing the limit)
- **Con:** Not config-driven — model is hardcoded, requires code change to switch
- **Con:** Anthropic API cost

---

## Alternate Route 3: OpenAI TTS — Audio Synthesis

**File:** `src/text_to_speech_openai.py`

**Model:** `tts-1-hd`

**Voice:** `onyx` (hardcoded)

**Auth:** `OPENAI_API_KEY`

### How It Differs from Active Route

| Aspect | Active (Google TTS) | Alternate (OpenAI TTS) |
|---|---|---|
| Model | Neural2 / Studio voices | `tts-1-hd` |
| Voice selection | Config-driven (4 options) | Hardcoded (`onyx`) |
| Chunk limit | 4500 characters | 4096 characters |
| Streaming | No (batch) | Yes (`with_streaming_response`) |
| Output format | MP3 | MP3 |
| Voice quality | Studio-O/M: very natural | `onyx`: deep, authoritative |

### Key Implementation Details

```python
CHUNK_LIMIT = 4096  # OpenAI TTS API limit

with client.audio.speech.with_streaming_response.create(
    model="tts-1-hd",
    voice="onyx",
    input=chunk
) as response:
    response.stream_to_file(temp_path)
```

OpenAI's TTS uses streaming response — the audio is streamed directly to a temp file rather than loaded into memory. This is more memory-efficient for large chunks.

**Available OpenAI voices:** `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

### How to Activate

In `app/pages/3_audio.py`, change the import:
```python
# Current (active):
from src.text_to_speech import synthesize_speech

# Switch to OpenAI TTS:
from src.text_to_speech_openai import synthesize_speech
```

Note: The OpenAI version does not support voice selection from the UI — the voice is hardcoded. The Audio page's voice selector UI would need to be hidden or updated.

Ensure `OPENAI_API_KEY` is set in `.env`.

### Trade-offs

- **Pro:** `onyx` voice is very natural for documentary-style narration
- **Pro:** Streaming response — slightly more memory-efficient
- **Con:** Voice is hardcoded — no UI-based switching without code changes
- **Con:** Not config-driven
- **Con:** OpenAI API cost

---

## Alternate Route 4: Anthropic Claude — Image Prompts

**File:** `src/image_prompting-anthropic.py`

**Model:** `claude-3-5-sonnet-20240620`

**Auth:** `ANTHROPIC_API_KEY`

### How It Differs from Active Route

| Aspect | Active (Google Gemini) | Alternate (Anthropic Claude) |
|---|---|---|
| Model | `gemini-2.5-flash` (configurable) | `claude-3-5-sonnet-20240620` (hardcoded) |
| Visual Style Bible | Yes — generated and reused | No — not implemented |
| Config-driven | Yes | No |
| max_tokens | Not set | `1024` |

**Missing feature:** The Anthropic version does NOT implement the Visual Style Bible (`3a_style_bible.txt`). This means images generated via the Anthropic route will lack visual consistency across the video. If activating, the Style Bible feature should be ported from the active Gemini version.

### How to Activate

In `app/pages/5_images.py`, change the import:
```python
# Current (active):
from src.image_prompting import generate_image_prompts

# Switch to Anthropic Claude:
from src.image_prompting_anthropic import generate_image_prompts
```

Note: Rename `image_prompting-anthropic.py` → `image_prompting_anthropic.py` first (hyphen is not valid in Python module names).

---

## Archive Modules

The `src/archive/` directory contains earlier prototype implementations that predate the current architecture. These are kept for historical reference only and should not be used.

```
src/archive/
├── img_prompt_generator-openai.py   # Early OpenAI DALL-E image prompt generator
├── img_prompt_generator-org.py      # Original image prompt generator (pre-LangChain)
├── summarizer-openai.py             # Early OpenAI GPT-4 summarizer
├── summarizer-org.py                # Original summarizer (pre-LangChain)
└── title_desc_generator_openai.py   # Early OpenAI metadata generator
```

These files use older patterns (direct OpenAI API calls without LangChain, no config system, no project isolation) and are not compatible with the current pipeline architecture.

---

## Activating an Alternate Route — Checklist

When switching any pipeline stage to an alternate route:

1. **Rename the file** if it uses hyphens (e.g., `summarization-anthropic.py` → `summarization_anthropic.py`)
2. **Update the import** in the relevant page file (`app/pages/`)
3. **Set the required API key** in `.env`
4. **Update the prompt** if the alternate version has an outdated prompt
5. **Test the function signature** — all alternate routes implement the same public function signature as the active route, so the page code should not need changes beyond the import
6. **Update `requirements.txt`** if the alternate route needs a package not currently installed (e.g., `langchain-anthropic`)
7. **Document the change** — update this file to reflect the new active/inactive status

---

## Future Route Considerations

For AI Software Factory Architect Agents planning future expansions:

- **Google Gemini Native API** (without LangChain): Could replace `langchain-google-genai` for lower overhead
- **Vertex AI Gemini** (via `vertexai` SDK): Would use ADC instead of API key — consistent with other Vertex services
- **ElevenLabs TTS**: Higher quality voices for premium productions
- **Stable Diffusion / FLUX**: Local image generation option (no API cost, requires GPU)
- **Whisper Local**: Run Whisper locally via `openai-whisper` package (no API cost, requires GPU)
- **Azure OpenAI**: Enterprise OpenAI endpoint for organizations with Azure agreements
