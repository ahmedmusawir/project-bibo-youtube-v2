# Bibo YouTube Video Generator

**Automated YouTube video creation pipeline powered by Google Cloud AI**

Transform YouTube videos into new content automatically: transcribe → summarize → generate voiceover → create images → compose final video.

## 🎯 What It Does

Takes a YouTube URL and produces a complete video with:
- AI-generated script (summarized from original)
- Professional voiceover (Google Cloud TTS)
- AI-generated images (Vertex AI Imagen)
- Metadata (title, description, hashtags)
- Final composed video ready for upload

## ⚡ Quick Start

```bash
# 1. Clone and install
git clone <repo-url>
cd project-bibo-youtube-v1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure (see SETUP.md for details)
cp .env.example .env
# Add your Google Cloud credentials

# 3. Run
python main.py
```

## 🏗️ Tech Stack

**All Google Cloud/Gemini** (no OpenAI or Anthropic):
- **Transcription**: Google Cloud Speech-to-Text
- **Summarization**: Google Gemini Flash
- **Text-to-Speech**: Google Cloud TTS (Studio voices)
- **Image Generation**: Vertex AI Imagen
- **Metadata**: Google Gemini
- **Video Composition**: MoviePy 2.x

## 📋 Pipeline Stages

```
YouTube URL
    ↓
[1] Transcription (Speech-to-Text) → 0_transcript.txt
    ↓
[2] Summarization (Gemini) → 1_summary.txt
    ↓
[3] Text-to-Speech (Google TTS) → 2_audio.mp3
    ↓
[4] Image Prompting (Gemini) → 3_image_prompts.json
    ↓
[5] Image Generation (Vertex AI) → 5_images/*.png
    ↓
[6] Metadata Generation (Gemini) → 4_metadata.json
    ↓
[7] Video Composition (MoviePy) → 6_final_video.mp4
```

## 💰 Cost Per Video (~30 min video)

| Service | Cost |
|---------|------|
| Speech-to-Text | $0.024 |
| Gemini (3 calls) | $0.003 |
| TTS | $0.072 |
| Imagen (5 images) | $0.100 |
| **Total** | **~$0.20** |

## 🚀 Features

- ✅ Handles videos up to 2 hours
- ✅ Automatic GCS upload for large files
- ✅ High-quality Studio voices
- ✅ JSON metadata output
- ✅ Automatic punctuation
- ✅ Configurable voice/language
- ✅ File-based pipeline (resume from any stage)
- ✅ Unit tests with mocks (offline testing)

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Installation and configuration
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical design and flow
- **[API.md](API.md)** - Module and function reference
- **[session-2026-02-04.md](session-2026-02-04.md)** - Latest development notes

## 🧪 Testing

```bash
# Unit tests (offline, mocked)
pytest tests/unit/ -v

# Integration tests (requires credentials)
pytest tests/integration/ -m integration -v

# Test individual stages
python -c "from src.transcription import transcribe_youtube_audio; transcribe_youtube_audio('URL', 'output.txt')"
```

## 🔧 Configuration

Key environment variables:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_API_KEY=your-gemini-api-key
GOOGLE_STT_BUCKET=your-gcs-bucket-name
GOOGLE_TTS_VOICE=en-US-Studio-O  # Optional
```

See [SETUP.md](SETUP.md) for complete configuration guide.

## 📁 Project Structure

```
project-bibo-youtube-v1/
├── src/                      # Core pipeline modules
│   ├── transcription.py      # Speech-to-Text
│   ├── summarization.py      # Gemini summarization
│   ├── text_to_speech.py     # Google TTS
│   ├── image_prompting.py    # Gemini image prompts
│   ├── image_creation.py     # Vertex AI Imagen
│   ├── metadata_generation.py # Gemini metadata
│   └── video_composition.py  # MoviePy composition
├── tests/
│   ├── unit/                 # Mocked unit tests
│   └── integration/          # Real API tests
├── projects/                 # Output directory
│   └── <project_name>/       # Per-project files
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
└── .env                      # Configuration (not in git)
```

## 🐛 Troubleshooting

**"Request payload size exceeds 10MB"**
- Set `GOOGLE_STT_BUCKET` in `.env`
- Large files auto-upload to GCS

**"TimeoutError after 600 seconds"**
- Fixed in latest version (60-min timeout)
- Long videos may take 15-30 minutes

**"No JavaScript runtime" warning**
- Non-blocking, downloads still work
- Optional: Install `deno` for yt-dlp

See [SETUP.md](SETUP.md) for more troubleshooting.

## 📝 License

MIT

## 🤝 Contributing

This is a personal project. Feel free to fork and adapt for your needs.

## 📧 Contact

For questions or issues, see session logs in repository root.
