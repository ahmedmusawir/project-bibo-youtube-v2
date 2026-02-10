# APP BRIEF: AI Video Generation Pipeline

## High-Level Purpose

A **CLI-driven, modular Python pipeline** that automates YouTube video creation from source content (YouTube URLs or scripts). Successfully generated ~30 published videos. The system transforms raw content into polished documentary-style videos with narration, synchronized visuals, and metadata.

---

## End-to-End Pipeline Flow

```
YouTube URL
    ↓
[1] Transcription → 0_transcript.txt
    ↓
[2] Summarization → 1_summary.txt (900-word documentary script)
    ├→ [3A] Text-to-Speech → 2_audio.mp3
    ├→ [3B] Metadata Generation → 3_metadata.txt (titles/description/hashtags)
    └→ [4] Image Prompt Generation → 4_image_prompts.txt
           ↓
       [5] Image Creation → 5_images/ (001.png, 002.png, ...)
           ↓
       [6] Video Composition → 6_final_video.mp4
              (combines images + 2_audio.mp3)
```

**Key Timing Control:** `SECONDS_PER_IMAGE = 20` determines image count and video pacing.

---

## Module Responsibilities

### **1. transcription.py**
- **Input:** YouTube URL
- **Process:** Download audio via `yt-dlp` → Transcribe via OpenAI Whisper
- **Output:** `0_transcript.txt` (raw transcript)
- **Dependencies:** OpenAI Whisper API, yt-dlp

### **2. summarization.py**
- **Input:** `0_transcript.txt`
- **Process:** Claude 3.5 Sonnet summarizes into 920-950 word documentary script
- **Output:** `1_summary.txt` (structured: HOOK → Context → Takeaways → CLOSING)
- **Constraints:** No ads, no meta-chatter, optimized for audio narration
- **Dependencies:** Anthropic Claude API, LangChain

### **3A. text_to_speech.py**
- **Input:** `1_summary.txt`
- **Process:** Split text into <4096 char chunks → Synthesize each → Combine MP3s
- **Output:** `2_audio.mp3` (narration)
- **Configuration:** Model `tts-1-hd`, voice `onyx`
- **Dependencies:** OpenAI TTS API, pydub

### **3B. metadata_generation.py**
- **Input:** `1_summary.txt`
- **Process:** Generate 5 SEO titles + description + hashtags via Claude
- **Output:** `3_metadata.txt` (YouTube upload metadata)
- **Dependencies:** Anthropic Claude API

### **4. image_prompting.py**
- **Input:** `1_summary.txt` + `2_audio.mp3` (for duration calculation)
- **Process:**
  - Calculate `num_images = ceil(audio_duration / SECONDS_PER_IMAGE)`
  - Split summary into N chunks
  - Generate vivid photorealistic prompts for each chunk
- **Output:** `4_image_prompts.txt` (numbered prompts)
- **Dependencies:** Anthropic Claude API, mutagen (audio duration)

### **5. image_creation.py**
- **Input:** `4_image_prompts.txt`
- **Process:** Parse prompts → Generate images via Google Vertex AI Imagen 4.0
- **Output:** `5_images/` directory (001.png, 002.png, ...) + `_image_log.json`
- **Configuration:** 16:9 aspect ratio, no watermark
- **Dependencies:** Google Vertex AI, Imagen 4.0

### **6. video_composition.py**
- **Input:** `5_images/` + `2_audio.mp3`
- **Process:**
  - Resize images to 1920x1080
  - Calculate duration per image: `total_audio_seconds / num_images`
  - Apply: FadeIn/Out (1.5s), Ken Burns zoom (5% per sec)
  - Concatenate clips → Attach audio → Render MP4
- **Output:** `6_final_video.mp4`
- **Configuration:** 24 FPS, HD resolution
- **Dependencies:** moviepy, Pillow

### **utils/utils.py**
- Token counting (OpenAI), word counting, text analysis

---

## External Dependencies

### **AI APIs:**
| Provider | Model | Usage |
|----------|-------|-------|
| OpenAI | whisper-1 | Transcription |
| OpenAI | tts-1-hd | Narration |
| Anthropic | claude-3-5-sonnet-20240620 | Summarization, metadata, prompts |
| Google Vertex AI | imagen-4.0 | Image generation |

### **Core Libraries:**
- **yt-dlp** (YouTube download)
- **moviepy** (video rendering)
- **pydub** (audio processing)
- **LangChain** (LLM orchestration)
- **Pillow** (image processing)
- **pytest** (testing)

### **Credentials (.env):**
```
OPENAI_API_KEY
ANTHROPIC_API_KEY
GOOGLE_APPLICATION_CREDENTIALS (points to cyberize-vertex-api.json)
GOOGLE_CLOUD_PROJECT=ninth-potion-455712-g9
GOOGLE_CLOUD_REGION=us-central1
```

---

## CLI Workflow (Intended Design)

### **Entry Point: main.py**
1. User runs `python main.py`
2. Prompted for project name → Creates `projects/{name}/` directory
3. Main menu:
   - **[1] Transcribe from YouTube URL** → Calls `transcription.transcribe_youtube_audio()`
   - **[2] Scrape Article URL** → Not implemented
   - **[3] Use Ready-Made Script** → User places script at `1_summary.txt`

### **Full Pipeline Execution (Manual):**
```bash
# Currently requires manual orchestration or running integration tests

# Stage 1: Transcription
projects/{name}/0_transcript.txt created

# Stage 2: Summarization
projects/{name}/1_summary.txt created

# Stage 3 (parallel):
projects/{name}/2_audio.mp3 created
projects/{name}/3_metadata.txt created

# Stage 4: Image prompting
projects/{name}/4_image_prompts.txt created

# Stage 5: Image generation
projects/{name}/5_images/ populated

# Stage 6: Video composition
projects/{name}/6_final_video.mp4 → FINAL OUTPUT
```

**Current Status:** Only transcription integrated into `main.py`. Remaining stages run via tests or manual invocation.

---

## Test Structure

### **Unit Tests (`tests/unit/`)**
- **Approach:** Mock all external dependencies (APIs, file I/O)
- **Tools:** `unittest.mock.patch`, `pytest.fixtures` (`tmp_path`)
- **Coverage:** Individual function logic, no network calls
- **Examples:**
  - `test_transcription.py` → Mocks yt-dlp and OpenAI
  - `test_text_to_speech.py` → Uses `FakeAudioSegment` for complex state
  - `test_video_composition.py` → Mocks moviepy and image loading

### **Integration Tests (`tests/integration/`)**
- **Approach:** Real API calls with live credentials
- **Directory:** Uses `projects/integration_test_run/` as golden file store
- **Execution:** Sequential with `pytest.mark.dependency()` chaining
- **Marking:** `@pytest.mark.integration` (run separately from unit tests)
- **Dependency Chain:**
  ```
  test_transcribe_youtube_audio_integration
    → test_summarize_transcript_integration
       ├→ test_generate_metadata_integration (parallel)
       └→ test_synthesize_speech_integration
          → test_generate_image_prompts_integration
             → test_create_images_from_prompts_integration
                → test_compose_video_integration
  ```

### **Test Execution:**
```bash
# Run unit tests only
pytest tests/unit/

# Run integration tests (requires API keys)
pytest tests/integration/ -m integration

# Run specific stage test
pytest tests/integration/test_video_composition.py::test_compose_video_integration
```

---

## State & File Passing Between Stages

### **Storage Pattern: File-Based State**
- **No in-memory passing:** Each module reads/writes files independently
- **Project directory:** `projects/{project_name}/` contains all artifacts
- **Numbered prefixes:** Files named `0_`, `1_`, `2_`, ... indicate pipeline order

### **State Artifacts:**
```
projects/{project_name}/
├── 0_transcript.txt       # Raw transcript from YouTube
├── 1_summary.txt          # Documentary script (900 words)
├── 2_audio.mp3            # Narration audio
├── 3_metadata.txt         # YouTube titles/description/hashtags
├── 4_image_prompts.txt    # Numbered visual prompts
├── 5_images/              # Generated PNGs (001.png, 002.png, ...)
│   └── _image_log.json    # Generation metadata
└── 6_final_video.mp4      # FINAL OUTPUT
```

### **Data Dependencies:**
- **1_summary.txt** → Consumed by stages 3A, 3B, and 4
- **2_audio.mp3** → Consumed by stages 4 and 6 (duration + final audio track)
- **5_images/** → Consumed by stage 6
- **Parallel stages 3A/3B:** Both read `1_summary.txt`, no dependencies on each other

### **Resumability:**
- Any stage can restart from last successful output file
- Checkpointing implicit via file existence
- No database or persistent state store required

---

## Architecture Notes

### **Strengths:**
- **Modularity:** Each stage is independent, testable, swappable
- **Clear separation:** API integrations encapsulated per module
- **Testing discipline:** Comprehensive unit + integration coverage
- **Production-proven:** Successfully generated ~30 real YouTube videos

### **Current Gaps (from git history):**
- **main.py integration incomplete:** Stages 2-6 not wired to CLI
- **Video composition blocker:** Recent "stuck at video module integration" (commit 68e2a65)
- **Error handling:** No retry logic for API failures
- **Logging:** Minimal progress indicators

### **Design Decisions:**
- **Claude over OpenAI for LLMs:** Better long-form summarization
- **Vertex AI for images:** Google Imagen quality/cost balance
- **File-based state:** Simpler than database, human-inspectable
- **20-second pacing:** Default `SECONDS_PER_IMAGE` balances detail vs retention

---

## Summary

This is a **well-architected, production-tested pipeline** with 7 sequential stages, multi-vendor AI API orchestration, and comprehensive testing. The system is currently undergoing V2 refactoring on the `gemini-v3` branch to complete CLI integration and resolve video composition issues. The architecture supports multiple concurrent projects, checkpoint-based resumption, and individual stage testing.

**Next logical steps (for implementation, not this analysis):**
1. Fix video composition integration tests
2. Wire stages 2-6 into `main.py` menu
3. Add error handling and logging
4. Externalize configuration (YAML/JSON for model choices)
