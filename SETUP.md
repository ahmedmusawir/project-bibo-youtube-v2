# Setup Guide

Complete installation and configuration guide for Bibo YouTube Video Generator.

---

## Prerequisites

- Python 3.8+
- Google Cloud Platform account
- FFmpeg (for audio/video processing)

---

## 1. Installation

### Clone Repository
```bash
git clone <repo-url>
cd project-bibo-youtube-v1
```

### Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Install FFmpeg
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

---

## 2. Google Cloud Setup

### 2.1 Create GCP Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Note your Project ID

### 2.2 Enable Required APIs
Enable these APIs in your project:
- Cloud Speech-to-Text API
- Cloud Text-to-Speech API
- Vertex AI API
- Cloud Storage API
- Generative Language API (for Gemini)

```bash
gcloud services enable speech.googleapis.com
gcloud services enable texttospeech.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable generativelanguage.googleapis.com
```

### 2.3 Create Service Account
1. Go to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Name: `bibo-video-generator`
4. Grant roles:
   - **Speech-to-Text Admin**
   - **Text-to-Speech Admin**
   - **Vertex AI User**
   - **Storage Object Admin**
5. Click **Create Key** → JSON
6. Save the JSON file securely

### 2.4 Get Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **Get API Key**
3. Create new key or use existing
4. Copy the API key

### 2.5 Create GCS Bucket
For large audio file transcription (>10MB):

```bash
# Replace with your project ID and preferred bucket name
gsutil mb -p YOUR_PROJECT_ID gs://bibo-transcription-temp

# Grant service account access
gsutil iam ch serviceAccount:YOUR_SA_EMAIL:roles/storage.objectAdmin \
  gs://bibo-transcription-temp
```

Or via Console:
1. Go to **Cloud Storage > Buckets**
2. Click **Create Bucket**
3. Name: `bibo-transcription-temp` (or your choice)
4. Region: Choose closest to you
5. Grant your service account **Storage Object Admin** role

---

## 3. Configuration

### 3.1 Create `.env` File
```bash
cp .env.example .env
```

### 3.2 Edit `.env`
```bash
# Required - Authentication
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service-account.json
GOOGLE_API_KEY=your-gemini-api-key-here

# Required - GCS bucket for large audio files
GOOGLE_STT_BUCKET=bibo-transcription-temp

# Optional - Voice Configuration (defaults shown)
GOOGLE_TTS_VOICE=en-US-Studio-O
GOOGLE_TTS_LANG=en-US
GOOGLE_STT_LANG=en-US

# Optional - Vertex AI Configuration
VERTEX_AI_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
```

### 3.3 Verify Configuration
```bash
# Test authentication
python -c "from google.cloud import speech; client = speech.SpeechClient(); print('✅ Speech-to-Text OK')"

python -c "from google.cloud import texttospeech; client = texttospeech.TextToSpeechClient(); print('✅ Text-to-Speech OK')"

python -c "from google.cloud import storage; client = storage.Client(); print('✅ Storage OK')"

# Test Gemini API
python -c "from langchain_google_genai import ChatGoogleGenerativeAI; llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash'); print('✅ Gemini OK')"
```

---

## 4. Voice Configuration

### List Available Voices
```bash
python -m src.text_to_speech --list-voices en-US
```

### Popular Voice Options

**Female Voices:**
- `en-US-Studio-O` (default) - Natural, professional
- `en-US-Neural2-F` - Clear, slightly robotic
- `en-GB-Studio-B` - British English

**Male Voices:**
- `en-US-Studio-M` - Natural, professional
- `en-US-Neural2-D` - Deep voice
- `en-GB-Studio-C` - British English

**Other Languages:**
- `es-ES-Studio-B` - Spanish (Spain)
- `fr-FR-Studio-A` - French
- `de-DE-Studio-B` - German
- `ja-JP-Studio-B` - Japanese

Set in `.env`:
```bash
GOOGLE_TTS_VOICE=en-US-Studio-M
GOOGLE_TTS_LANG=en-US
```

---

## 5. Testing

### Run Unit Tests
```bash
pytest tests/unit/ -v
```

### Run Integration Tests
Requires valid credentials:
```bash
pytest tests/integration/ -m integration -v
```

### Test Individual Stages
```bash
# Transcription
python -c "from src.transcription import transcribe_youtube_audio; transcribe_youtube_audio('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'test_output.txt')"

# List voices
python -m src.text_to_speech --list-voices
```

---

## 6. Running the Pipeline

### Interactive Mode
```bash
python main.py
```

Follow the prompts:
1. Create or select project
2. Choose input source (YouTube URL)
3. Enter YouTube URL
4. Pipeline runs automatically

### Command-Line Mode
Run individual stages:
```bash
# Full pipeline example
python -c "from src.transcription import transcribe_youtube_audio; transcribe_youtube_audio('URL', 'projects/Test/0_transcript.txt')"

python -c "from src.summarization import summarize_transcript; summarize_transcript('projects/Test/0_transcript.txt', 'projects/Test/1_summary.txt')"

python -c "from src.text_to_speech import synthesize_speech; synthesize_speech('projects/Test/1_summary.txt', 'projects/Test/2_audio.mp3')"

# ... continue with other stages
```

---

## 7. Troubleshooting

### "ModuleNotFoundError: No module named 'google'"
```bash
pip install --upgrade google-cloud-speech google-cloud-texttospeech google-cloud-storage
```

### "DefaultCredentialsError"
Check:
1. `GOOGLE_APPLICATION_CREDENTIALS` path is correct
2. Service account JSON file exists
3. File has correct permissions (readable)

```bash
# Verify file exists
ls -l $GOOGLE_APPLICATION_CREDENTIALS

# Test authentication
gcloud auth application-default print-access-token
```

### "Request payload size exceeds 10MB"
Set `GOOGLE_STT_BUCKET` in `.env`:
```bash
GOOGLE_STT_BUCKET=your-bucket-name
```

### "Permission denied" on GCS
Grant service account access:
```bash
gsutil iam ch serviceAccount:YOUR_SA_EMAIL:roles/storage.objectAdmin \
  gs://your-bucket-name
```

### "API not enabled"
Enable required APIs:
```bash
gcloud services enable speech.googleapis.com texttospeech.googleapis.com aiplatform.googleapis.com storage.googleapis.com
```

### "TimeoutError after 600 seconds"
Fixed in latest version. Update code:
```bash
git pull origin main
```

### "No JavaScript runtime" warning (yt-dlp)
Non-blocking warning. To fix:
```bash
# Install deno
curl -fsSL https://deno.land/install.sh | sh
```

### FFmpeg not found
```bash
# Verify installation
ffmpeg -version

# If not installed, see Installation section
```

---

## 8. Cost Management

### Monitor Usage
- [Google Cloud Console - Billing](https://console.cloud.google.com/billing)
- Set up budget alerts
- Enable billing export to BigQuery

### Estimated Costs (per 30-min video)
- Speech-to-Text: $0.024
- Gemini API: $0.003
- Text-to-Speech: $0.072
- Imagen: $0.100
- **Total: ~$0.20**

### Cost Optimization
1. Use Gemini Flash (not Pro) for summarization
2. Use Studio voices (same price as Neural2, better quality)
3. Set up GCS lifecycle rules to auto-delete temp files
4. Use regional endpoints closest to you

---

## 9. Security Best Practices

### Protect Credentials
```bash
# Never commit .env or service account JSON
echo ".env" >> .gitignore
echo "*.json" >> .gitignore

# Set restrictive permissions
chmod 600 service-account.json
chmod 600 .env
```

### Service Account Permissions
Use principle of least privilege:
- Only grant required roles
- Use separate service accounts for dev/prod
- Rotate keys regularly

### API Key Security
- Don't hardcode API keys
- Use environment variables only
- Restrict API key usage in GCP Console
- Regenerate if exposed

---

## 10. Next Steps

1. ✅ Complete setup above
2. ✅ Run `python main.py` to test
3. ✅ Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
4. ✅ Check [API.md](API.md) for module reference
5. ✅ Read session logs for development history

---

## Support

For issues or questions:
- Check session logs in repository root
- Review error messages carefully
- Verify all prerequisites are met
- Test authentication separately
