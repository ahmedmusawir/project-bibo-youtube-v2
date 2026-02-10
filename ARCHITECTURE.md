# Architecture Documentation

Technical architecture and design decisions for Bibo YouTube Video Generator.

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [Data Flow](#data-flow)
4. [Module Design](#module-design)
5. [Authentication & Security](#authentication--security)
6. [Error Handling](#error-handling)
7. [Testing Strategy](#testing-strategy)
8. [Design Decisions](#design-decisions)

---

## System Overview

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (CLI)                     │
│                        main.py                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Pipeline Orchestrator                      │
│              (File-based state management)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌────────┐      ┌────────┐     ┌────────┐
    │ Google │      │ Google │     │ Vertex │
    │  STT   │      │ Gemini │     │   AI   │
    │  TTS   │      │  API   │     │ Imagen │
    └────────┘      └────────┘     └────────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
                  ┌──────────────┐
                  │ Google Cloud │
                  │   Storage    │
                  └──────────────┘
```

### Technology Stack
- **Language**: Python 3.8+
- **AI Services**: Google Cloud (Speech-to-Text, TTS, Gemini, Vertex AI)
- **Video Processing**: MoviePy 2.x
- **Audio Processing**: pydub, FFmpeg
- **HTTP Client**: yt-dlp (YouTube downloads)
- **Testing**: pytest with mocking
- **Configuration**: python-dotenv

---

## Pipeline Architecture

### File-Based State Management

Each project maintains state through files:
```
projects/<project_name>/
├── 0_transcript.txt       # Stage 1 output
├── 1_summary.txt          # Stage 2 output
├── 2_audio.mp3            # Stage 3 output
├── 3_image_prompts.json   # Stage 4 output
├── 4_metadata.json        # Stage 6 output
├── 5_images/              # Stage 5 output
│   ├── image_0.png
│   ├── image_1.png
│   └── ...
└── 6_final_video.mp4      # Stage 7 output
```

**Benefits:**
- Resume from any stage
- Easy debugging (inspect intermediate outputs)
- No database required
- Simple backup/restore
- Parallel processing possible

### Pipeline Stages

```
┌──────────────────────────────────────────────────────────────┐
│ Stage 1: Transcription                                       │
│ Input:  YouTube URL                                          │
│ Output: 0_transcript.txt                                     │
│ API:    Google Cloud Speech-to-Text (long-running)          │
│ Notes:  Auto-detects file size, uses GCS for >10MB          │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│ Stage 2: Summarization                                       │
│ Input:  0_transcript.txt                                     │
│ Output: 1_summary.txt                                        │
│ API:    Google Gemini Flash                                  │
│ Notes:  Prompt-engineered for engaging YouTube scripts      │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│ Stage 3: Text-to-Speech                                      │
│ Input:  1_summary.txt                                        │
│ Output: 2_audio.mp3                                          │
│ API:    Google Cloud TTS (Studio voices)                    │
│ Notes:  Chunking for long text, MP3 output                  │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│ Stage 4: Image Prompting                                     │
│ Input:  1_summary.txt, 2_audio.mp3 (for duration)           │
│ Output: 3_image_prompts.json                                 │
│ API:    Google Gemini Flash                                  │
│ Notes:  Calculates image count based on audio length        │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│ Stage 5: Image Generation                                    │
│ Input:  3_image_prompts.json                                 │
│ Output: 5_images/*.png                                       │
│ API:    Vertex AI Imagen                                     │
│ Notes:  Sequential generation, PNG format                    │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│ Stage 6: Metadata Generation                                 │
│ Input:  1_summary.txt                                        │
│ Output: 4_metadata.json                                      │
│ API:    Google Gemini Flash                                  │
│ Notes:  JSON output (title, description, hashtags)          │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│ Stage 7: Video Composition                                   │
│ Input:  2_audio.mp3, 5_images/*.png                          │
│ Output: 6_final_video.mp4                                    │
│ Library: MoviePy 2.x                                         │
│ Notes:  Images timed to audio duration, crossfades          │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Transcription Flow (Stage 1)

```
YouTube URL
    ↓
[yt-dlp] Download audio → temp_audio.mp3
    ↓
[pydub] Convert to FLAC (mono, 16kHz) → temp_audio.flac
    ↓
[Check file size]
    ↓
    ├─ < 10MB → [Inline] → Speech-to-Text API
    │                           ↓
    └─ > 10MB → [Upload to GCS] → gs://bucket/temp.flac
                                    ↓
                            Speech-to-Text API (URI mode)
                                    ↓
                            [Delete GCS blob]
    ↓
[Long-running recognition] Poll for completion (up to 60 min)
    ↓
Extract transcript text
    ↓
Save to 0_transcript.txt
    ↓
Cleanup temp files
```

### TTS Flow (Stage 3)

```
1_summary.txt
    ↓
Read text content
    ↓
[Split into chunks] (4500 chars each, respect paragraphs)
    ↓
For each chunk:
    ↓
    [Google Cloud TTS] synthesize_speech()
    ↓
    Save to temp MP3 file
    ↓
    [pydub] Load MP3 segment
    ↓
    Append to combined audio
    ↓
[Export combined audio] → 2_audio.mp3
    ↓
Cleanup temp files
```

### Image Generation Flow (Stage 5)

```
3_image_prompts.json
    ↓
Parse JSON array of prompts
    ↓
For each prompt (sequential):
    ↓
    [Vertex AI Imagen] generate_images()
    ↓
    Receive base64-encoded PNG
    ↓
    Decode and save → 5_images/image_N.png
    ↓
    Print progress
```

---

## Module Design

### Core Modules

#### `src/transcription.py`
**Purpose:** YouTube audio → text transcript

**Key Functions:**
- `transcribe_youtube_audio(url, output_path)` - Main entry point
- `_download_audio_to_temp(url)` - yt-dlp wrapper
- `_convert_to_flac(mp3_path)` - Audio format conversion
- `_upload_to_gcs(file_path)` - GCS upload for large files
- `_get_speech_client()` - Client factory

**Design Decisions:**
- Long-running recognition for videos up to 480 minutes
- Automatic GCS fallback for files >10MB
- FLAC format for optimal STT quality (mono, 16kHz)
- 60-minute timeout to handle long videos

#### `src/summarization.py`
**Purpose:** Transcript → engaging summary

**Key Functions:**
- `summarize_transcript(input_path, output_path)` - Main entry point

**Design Decisions:**
- Gemini Flash for cost efficiency
- Prompt engineering for YouTube-style content
- LangChain integration for structured prompts

#### `src/text_to_speech.py`
**Purpose:** Summary → audio narration

**Key Functions:**
- `synthesize_speech(summary_path, audio_path)` - Main entry point
- `split_text(text, limit)` - Text chunking
- `list_voices(language_code)` - Voice discovery
- `print_voices(language_code)` - CLI helper

**Design Decisions:**
- Studio voices (highest quality, same price as Neural2)
- Chunking at 4500 chars (safe for 5000 byte limit)
- Paragraph-aware splitting
- Environment variable configuration

#### `src/image_prompting.py`
**Purpose:** Summary → image generation prompts

**Key Functions:**
- `generate_image_prompts(summary_path, audio_path, output_path)` - Main entry point

**Design Decisions:**
- Dynamic image count based on audio duration (1 image per 10 seconds)
- JSON output for structured data
- Gemini Flash for prompt generation

#### `src/image_creation.py`
**Purpose:** Prompts → generated images

**Key Functions:**
- `create_images_from_prompts(prompts_path, output_dir)` - Main entry point

**Design Decisions:**
- Vertex AI Imagen for quality
- Sequential generation (avoid rate limits)
- PNG format for quality
- Base64 decoding from API response

#### `src/metadata_generation.py`
**Purpose:** Summary → video metadata

**Key Functions:**
- `generate_metadata(summary_path, output_path)` - Main entry point

**Design Decisions:**
- JSON output (title, description, hashtags)
- Gemini Flash for generation
- Structured parsing from LLM response

#### `src/video_composition.py`
**Purpose:** Audio + Images → final video

**Key Functions:**
- `compose_video_from_assets(audio_path, images_dir, output_path)` - Main entry point

**Design Decisions:**
- MoviePy 2.x API
- Images timed to audio duration
- Crossfade transitions
- 1080p output resolution

---

## Authentication & Security

### Authentication Flow

```
Application Start
    ↓
Load .env file
    ↓
    ├─ GOOGLE_APPLICATION_CREDENTIALS → Service Account JSON
    │                                        ↓
    │                              [ADC - Application Default Credentials]
    │                                        ↓
    │                              Used by: STT, TTS, Storage, Vertex AI
    │
    └─ GOOGLE_API_KEY → Gemini API Key
                            ↓
                    Used by: Gemini (via LangChain)
```

### Security Considerations

**Service Account Permissions:**
- Speech-to-Text Admin (transcription)
- Text-to-Speech Admin (TTS)
- Vertex AI User (Imagen)
- Storage Object Admin (GCS uploads)

**API Key Restrictions:**
- Restrict to Generative Language API only
- Set usage quotas
- Rotate regularly

**Secrets Management:**
- Never commit `.env` or service account JSON
- Use environment variables only
- Set restrictive file permissions (chmod 600)

---

## Error Handling

### Retry Strategy

**Transient Errors:**
- Network timeouts → Retry with exponential backoff
- Rate limits → Handled by Google client libraries
- Temporary API failures → Retry up to 3 times

**Permanent Errors:**
- Invalid credentials → Fail fast with clear message
- Missing files → Validate before API calls
- Quota exceeded → Report to user

### Graceful Degradation

**File Size Handling:**
```python
if file_size > MAX_INLINE_AUDIO_SIZE:
    if not GOOGLE_STT_BUCKET:
        raise ValueError("Set GOOGLE_STT_BUCKET for large files")
    # Upload to GCS
else:
    # Use inline audio
```

**Timeout Handling:**
```python
try:
    response = operation.result(timeout=3600)
except TimeoutError:
    print("Transcription taking longer than expected...")
    # Could implement polling status check here
```

---

## Testing Strategy

### Unit Tests (`tests/unit/`)

**Approach:** Mock all external dependencies

**Coverage:**
- All core functions
- Edge cases (empty input, large files, etc.)
- Error conditions

**Example:**
```python
@patch('src.transcription._get_speech_client')
@patch('src.transcription._convert_to_flac')
def test_transcribe(mock_convert, mock_client):
    # Mock returns
    mock_client.return_value = MagicMock()
    # Test logic
    result = transcribe_youtube_audio(url, output)
    # Assertions
    assert os.path.exists(output)
```

### Integration Tests (`tests/integration/`)

**Approach:** Real API calls (opt-in)

**Requirements:**
- Valid credentials
- Run with `-m integration` flag
- May incur costs

**Purpose:**
- Verify API compatibility
- Test authentication
- Validate end-to-end flow

---

## Design Decisions

### Why Google Cloud Only?

**Before:** OpenAI (Whisper, TTS) + Anthropic (Claude)
**After:** Google Cloud (STT, TTS, Gemini, Vertex AI)

**Reasons:**
1. **Cost:** 38% cheaper per video
2. **Quality:** Studio voices superior to OpenAI TTS
3. **Integration:** Single authentication (ADC)
4. **Scalability:** Better handling of long videos
5. **Ecosystem:** Unified billing and monitoring

### Why File-Based State?

**Alternatives considered:**
- Database (PostgreSQL, SQLite)
- In-memory state
- Message queue (Celery, RabbitMQ)

**Chosen: File-based**

**Reasons:**
1. **Simplicity:** No database setup required
2. **Debugging:** Easy to inspect intermediate outputs
3. **Resume:** Can restart from any stage
4. **Portability:** Easy to backup/share projects
5. **Transparency:** Users can see exactly what's generated

### Why Long-Running Recognition?

**Alternatives:**
- Synchronous recognition (60-second limit)
- Chunking audio manually

**Chosen: Long-running**

**Reasons:**
1. **Duration:** Handles up to 480 minutes
2. **Quality:** Better accuracy for long-form content
3. **Simplicity:** No manual chunking required
4. **Model:** Access to `latest_long` optimized model

### Why MoviePy 2.x?

**Alternatives:**
- FFmpeg directly
- OpenCV
- MoviePy 1.x

**Chosen: MoviePy 2.x**

**Reasons:**
1. **Pythonic:** Clean API, easy to use
2. **Features:** Built-in transitions, effects
3. **Maintained:** Active development
4. **Documentation:** Good examples and community

---

## Performance Considerations

### Bottlenecks

1. **Transcription:** 10-30 minutes for long videos (API processing time)
2. **Image Generation:** Sequential, ~5-10 seconds per image
3. **Video Composition:** CPU-intensive, scales with video length

### Optimization Opportunities

**Parallelization:**
- Image generation could be parallelized (with rate limit handling)
- Multiple projects could run concurrently

**Caching:**
- Cache voice lists (rarely change)
- Reuse transcripts for same video

**Streaming:**
- Stream audio download instead of full download first
- Progressive video composition

---

## Future Enhancements

### Planned Features
- Progress bars for long operations
- Web UI for pipeline management
- Batch processing
- Retry logic for transient failures
- Video preview/thumbnail generation
- Multi-language support
- Custom prompt templates

### Scalability
- Kubernetes deployment
- Cloud Run for serverless execution
- Pub/Sub for async processing
- Cloud Storage for project state
- BigQuery for analytics

---

## References

- [Google Cloud Speech-to-Text Docs](https://cloud.google.com/speech-to-text/docs)
- [Google Cloud TTS Docs](https://cloud.google.com/text-to-speech/docs)
- [Vertex AI Imagen Docs](https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview)
- [Gemini API Docs](https://ai.google.dev/docs)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)
