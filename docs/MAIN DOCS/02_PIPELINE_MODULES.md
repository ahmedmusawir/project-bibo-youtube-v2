# 02 — Pipeline Modules

Deep-dive reference for every module in `src/`. Intended for Engineer Agents building on or modifying VidGen.

---

## Module Map

```
src/
├── transcription.py          # Stage 0: YouTube audio download + Google STT
├── summarization.py          # Stage 1: Script generation via Gemini LLM
├── text_to_speech.py         # Stage 2: Audio synthesis via Google Cloud TTS
├── metadata_generation.py    # Stage 3: YouTube metadata via Gemini LLM
├── image_prompting.py        # Stage 4a: Image prompt generation via Gemini LLM
├── image_creation.py         # Stage 4b: Image generation via Vertex AI Imagen
├── video_composition.py      # Stage 5: Video assembly via MoviePy
├── logger.py                 # Utility: file + console logging
└── utils/
    ├── config.py             # Config read/write for model/voice selection
    ├── check_script.py       # Dev utility: script quality checker
    ├── check_transcript.py   # Dev utility: transcript quality checker
    └── utils.py              # Misc helpers
```

---

## `src/transcription.py`

**Purpose:** Downloads audio from a YouTube URL and transcribes it using Google Cloud Speech-to-Text.

**Active module** — this is the canonical transcription path. `src/transcription_openai.py` exists as an alternate route but is NOT used in the active pipeline.

### Key Constants
```python
DEFAULT_LANGUAGE = "en-US"
MAX_INLINE_AUDIO_SIZE = 10 * 1024 * 1024  # 10MB
```

### Internal Functions

| Function | Description |
|---|---|
| `_download_audio_to_temp(url)` | Downloads YouTube audio to a temp MP3 file via `yt-dlp`. Uses `bestaudio/best` format, 192kbps MP3. |
| `_get_speech_client()` | Returns a `google.cloud.speech.SpeechClient` using ADC. |
| `_convert_to_flac(mp3_path)` | Converts MP3 → FLAC (mono, 16kHz) using `pydub`. FLAC is required for Google STT long-running recognition. |
| `_upload_to_gcs(file_path)` | Uploads FLAC file to GCS bucket (`GOOGLE_STT_BUCKET` env var). Returns `(gcs_uri, blob)`. Raises `ValueError` if bucket not set. |
| `_delete_from_gcs(blob)` | Cleans up the temporary GCS blob after transcription. |

### Public Function

```python
def transcribe_youtube_audio(youtube_url: str, output_transcript_path: str) -> str
```

**Full execution flow:**
1. Download audio → temp MP3 via `yt-dlp`
2. Convert MP3 → FLAC (mono, 16kHz) via `pydub`
3. Upload FLAC → GCS bucket (always uses GCS, even for small files, because `long_running_recognize` is required for YouTube-length content)
4. Configure STT: `FLAC` encoding, `16000Hz`, `enable_automatic_punctuation=True`, `model="latest_long"`
5. Call `client.long_running_recognize()` — async operation with 60-minute timeout
6. Concatenate all result alternatives into `full_transcript`
7. Write to `output_transcript_path`
8. Clean up: delete temp MP3, temp FLAC, GCS blob

**Why always GCS?** Google STT's inline audio limit is ~1 minute. YouTube videos are always longer, so GCS upload is mandatory.

**Dependencies:** `yt-dlp`, `google-cloud-speech`, `google-cloud-storage`, `pydub`, `python-dotenv`

**Environment variables used:**
- `GOOGLE_APPLICATION_CREDENTIALS` (via ADC)
- `GOOGLE_STT_BUCKET` — GCS bucket name (required)
- `GOOGLE_STT_LANG` — language code (default: `en-US`)

---

## `src/summarization.py`

**Purpose:** Transforms a raw transcript into a polished 900-950 word YouTube narration script using a Gemini LLM via LangChain.

### LLM Initialization
```python
llm = ChatGoogleGenerativeAI(
    model=get_summarization_llm(),   # from config/config.json
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.5,
    # max_output_tokens intentionally NOT set — prevents truncation
)
```

**Critical design note:** `max_output_tokens` is explicitly omitted. Setting it caused output truncation in earlier versions. The model uses its default token limit.

### LangChain Chain
Uses `create_stuff_documents_chain` from `langchain_classic`:
1. `TextLoader` loads the transcript file as a LangChain `Document`
2. `ChatPromptTemplate` injects the document as `{context}`
3. Chain: `create_stuff_documents_chain(llm, prompt)` → invoked with `{"context": docs}`

### Prompt Engineering
The system prompt enforces:
- **Word count:** 920-950 words (hard constraint, trim if over)
- **No special characters** (`*`, `#`, etc.) — script goes to TTS audio
- **No "Key Takeaways" sections** — audio-unfriendly format
- **Must end with:** "Thanks for watching"
- **Style:** Documentary narration, dense 5-minute knowledge bite

### Public Function
```python
def summarize_transcript(transcript_path: str, summary_path: str) -> str
```

**Dependencies:** `langchain-community`, `langchain-core`, `langchain-google-genai`, `langchain-classic`, `python-dotenv`

**Environment variables used:**
- `GOOGLE_API_KEY`

---

## `src/text_to_speech.py`

**Purpose:** Converts the script text to MP3 audio using Google Cloud Text-to-Speech.

### Key Constants
```python
CHUNK_LIMIT = 4500   # Google TTS limit is ~5000 bytes; 4500 is safe margin
DEFAULT_VOICE = "en-US-Studio-O"
DEFAULT_LANG = "en-US"
```

### Internal Functions

| Function | Description |
|---|---|
| `_get_tts_client()` | Returns `texttospeech.TextToSpeechClient()` via ADC |
| `split_text(text, limit)` | Splits text into paragraph-respecting chunks under `limit` characters |
| `list_voices(language_code)` | Lists available Google TTS voices, optionally filtered by language |
| `print_voices(language_code)` | Dev utility: prints voice list to console |

### Public Function
```python
def synthesize_speech(summary_path: str, audio_path: str) -> str
```

**Full execution flow:**
1. Reload `.env` with `override=True` (picks up any runtime config changes)
2. Load voice/lang from `config/config.json` via `src.utils.config` (falls back to env vars)
3. Read script text from `summary_path`
4. Split into chunks via `split_text()` (respects paragraph boundaries)
5. For each chunk: call `client.synthesize_speech()` → write to temp MP3
6. Load all temp MP3s with `pydub.AudioSegment` → concatenate → export final MP3
7. Clean up temp files

**Voice configuration:** Voice is read from `config/config.json` → `tts.current_voice` and `tts.current_lang`. This allows voice switching from the Streamlit UI without code changes.

**Dependencies:** `google-cloud-texttospeech`, `pydub`, `python-dotenv`

**Environment variables used:**
- `GOOGLE_APPLICATION_CREDENTIALS` (via ADC)
- `GOOGLE_TTS_VOICE` (fallback if config.json unavailable)
- `GOOGLE_TTS_LANG` (fallback if config.json unavailable)

---

## `src/metadata_generation.py`

**Purpose:** Generates YouTube metadata (titles, description, hashtags) from the script using a Gemini LLM.

### LLM Initialization
```python
llm = ChatGoogleGenerativeAI(
    model=get_prompting_llm(),   # from config/config.json
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.8,
)
```

### LangChain Chain
Simple LCEL chain: `prompt | llm | StrOutputParser()`

The prompt requests a structured response in this exact format:
```
TITLES:
- Title 1
- Title 2
...

DESCRIPTION:
Your description here.

HASHTAGS:
#tag1 #tag2 #tag3
```

### Output Parser
`parse_metadata_output(raw_text)` is a custom line-by-line parser (not JSON from LLM). It:
- Detects `TITLES:`, `DESCRIPTION:`, `HASHTAGS:` section headers
- Extracts bullet-point titles (lines starting with `-`)
- Collects description lines
- Extracts hashtags (tokens starting with `#`)
- Returns a structured `dict`

### Public Function
```python
def generate_metadata(summary_path: str, output_path: str) -> str
```

Output is saved as JSON:
```json
{
  "titles": ["Title 1", "Title 2", ...],
  "description": "Full description text...",
  "hashtags": ["#tag1", "#tag2", ...]
}
```

**Dependencies:** `langchain-core`, `langchain-google-genai`, `python-dotenv`

**Environment variables used:**
- `GOOGLE_API_KEY`

---

## `src/image_prompting.py`

**Purpose:** Generates a synchronized list of AI image prompts from the script, timed to the audio duration. Also generates a Visual Style Bible for visual consistency.

### Key Constant
```python
SECONDS_PER_IMAGE = 20
```
This single value controls video pacing. At 20s/image, a 5-minute audio produces ~15 images.

### Internal Functions

| Function | Description |
|---|---|
| `_calculate_num_images(audio_path, seconds_per_image)` | Loads MP3 with `pydub`, computes `ceil(duration / seconds_per_image)` |
| `_split_summary_into_chunks(summary, num_chunks)` | Splits script text into N equal word-count chunks |
| `_generate_style_bible(summary_text)` | Calls Gemini to produce a 3-5 sentence visual style description (color palette, lighting, camera style, cinematic tone). Saved as `3a_style_bible.txt`. |

### Visual Style Bible
The Style Bible is generated **once per project** from the full script. It describes visual style only (not content). It is injected as context into every individual image prompt to ensure visual coherence across all images.

If `3a_style_bible.txt` already exists and is non-empty, it is reused (not regenerated). This allows manual editing of the style bible.

### Public Function
```python
def generate_image_prompts(
    summary_path: str,
    audio_path: str,
    prompts_path: str,
    seconds_per_image: int = 20,
    style_bible_path: str = None
) -> str
```

**Full execution flow:**
1. Calculate number of images needed from audio duration
2. Split script into N text chunks (one per image)
3. Generate or load Style Bible
4. For each chunk: call Gemini with `(chunk, style_bible)` → get one image prompt
5. Write numbered prompts to `prompts_path`

**Prompt engineering for images:**
- Forces `[photorealistic]`, `[high-resolution]`, `[realistic lighting]` in every prompt
- Instructs model to include brand names (ChatGPT, Anthropic, etc.) as visual anchors
- Keeps prompts under 200 words
- Style Bible is injected as context but not copied verbatim into output

**Dependencies:** `langchain-core`, `langchain-google-genai`, `pydub`, `python-dotenv`

**Environment variables used:**
- `GOOGLE_API_KEY`

---

## `src/image_creation.py`

**Purpose:** Generates PNG images from the numbered prompt list using Google Vertex AI Imagen.

### Vertex AI Initialization
```python
_vertex_ai_initialized = False

def _initialize_vertex_ai():
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
    REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
    vertexai.init(project=PROJECT_ID, location=REGION)
```

Initialization is guarded by a module-level flag to avoid re-initializing on every call.

### Public Function
```python
def create_images_from_prompts(prompts_path: str, output_dir: str) -> str
```

**Full execution flow:**
1. Initialize Vertex AI (once)
2. Read prompts file — extract lines matching `^\d+\.` (numbered prompts)
3. Load Imagen model from `config/config.json` → `image_gen.current`
4. For each prompt:
   - Call `generation_model.generate_images(prompt, number_of_images=1, aspect_ratio="16:9", add_watermark=False)`
   - Save as `{index:03}.png` (e.g., `001.png`, `002.png`)
5. Write `_image_log.json` to output directory with prompt/filepath mapping

**Image specs:** 16:9 aspect ratio, no watermark, PNG format.

**Error handling:** Individual image failures are caught and logged — the pipeline continues with remaining images.

**Dependencies:** `vertexai`, `google-cloud-aiplatform`, `python-dotenv`

**Environment variables used:**
- `GOOGLE_APPLICATION_CREDENTIALS` (via ADC)
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_REGION` (default: `us-central1`)

---

## `src/video_composition.py`

**Purpose:** Assembles the final MP4 video from a directory of PNG images and an MP3 audio file using MoviePy 2.x.

### Public Function
```python
def compose_video(
    images_dir: str,
    audio_path: str,
    output_path: str,
    video_size=(1920, 1080),
    fade_duration=1.5,
    fps=24
) -> str
```

**Full execution flow:**
1. Scan `images_dir` for `.png`, `.jpg`, `.jpeg` files (sorted alphabetically)
2. For each image:
   - Open with `PIL.Image`, convert to RGB
   - Apply EXIF transpose (fixes rotation issues)
   - Resize to `1920x1080` with LANCZOS resampling
   - Convert to NumPy array → `moviepy.ImageClip`
3. Load audio: `AudioFileClip(audio_path)`
4. Calculate `duration_per_image = audio.duration / len(image_clips)` — auto-distributes audio evenly
5. Apply effects to each clip:
   - `vfx.Resize(lambda t: 1 + 0.05 * t)` — slow Ken Burns zoom (5% over clip duration)
   - `vfx.FadeIn(1.5s)` + `vfx.FadeOut(1.5s)` — smooth transitions
6. `concatenate_videoclips(processed_clips, method="compose")`
7. Attach audio: `video.with_audio(audio)`
8. Render: `video.write_videofile(output_path, fps=24)`

**Output specs:** 1920x1080, 24fps, MP4 with H.264 video + AAC audio.

**Dependencies:** `moviepy>=2.x`, `Pillow`, `numpy`, `ffmpeg` (system or bundled)

---

## `src/logger.py`

**Purpose:** Dual-output logger (console + timestamped log file). Used by CLI/legacy paths.

**Note:** In the Streamlit UI, real-time logging is handled by `app/utils.py:capture_stdout_to_streamlit()` instead. `src/logger.py` is retained for CLI usage and future agent integrations.

### Classes

| Class | Description |
|---|---|
| `Logger` | Opens a timestamped `.log` file in `logs/`, writes with `[HH:MM:SS]` prefix |
| `TeeOutput` | Replaces `sys.stdout`/`sys.stderr` to write to both console and log file simultaneously |

### Public Functions
```python
init_logging(project_name=None, log_dir="logs") -> str   # returns log file path
stop_logging()                                            # restores stdout/stderr
get_log_path() -> str                                     # returns current log path
```

---

## `src/utils/config.py`

**Purpose:** Read/write interface for `config/config.json`. Provides typed getter/setter functions for all configurable model and voice parameters.

### Path Resolution
Uses upward directory traversal from `__file__` to find `main.py` — this makes it work regardless of CWD.

### Functions

| Function | Description |
|---|---|
| `load_config()` | Reads and returns `config/config.json` as dict |
| `save_config(config)` | Writes dict back to `config/config.json` |
| `get_summarization_llm()` | Returns `llm_summarization.current` |
| `set_summarization_llm(model)` | Validates against `available` list, then saves |
| `get_prompting_llm()` | Returns `llm_prompting.current` |
| `set_prompting_llm(model)` | Validates against `available` list, then saves |
| `get_tts_voice()` | Returns `tts.current_voice` |
| `get_tts_lang()` | Returns `tts.current_lang` |
| `set_tts_voice(voice_id, lang)` | Validates, auto-detects lang from voice if not provided |
| `get_image_gen_model()` | Returns `image_gen.current` |
| `set_image_gen_model(model)` | Validates against `available` list, then saves |
| `get_all_current_models()` | Returns all current selections as a single dict |
