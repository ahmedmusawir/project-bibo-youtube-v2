# API Reference

Complete module and function reference for Bibo YouTube Video Generator.

---

## Table of Contents
1. [Transcription Module](#transcription-module)
2. [Summarization Module](#summarization-module)
3. [Text-to-Speech Module](#text-to-speech-module)
4. [Image Prompting Module](#image-prompting-module)
5. [Image Creation Module](#image-creation-module)
6. [Metadata Generation Module](#metadata-generation-module)
7. [Video Composition Module](#video-composition-module)

---

## Transcription Module

**File:** `src/transcription.py`

### `transcribe_youtube_audio(youtube_url, output_transcript_path)`

Downloads audio from YouTube and transcribes it using Google Cloud Speech-to-Text.

**Parameters:**
- `youtube_url` (str): YouTube video URL
- `output_transcript_path` (str): Absolute path to save transcript file

**Returns:**
- `str`: Path to saved transcript file

**Raises:**
- `ValueError`: If `GOOGLE_STT_BUCKET` not set for large files (>10MB)
- `TimeoutError`: If transcription exceeds 60 minutes
- `google.api_core.exceptions.*`: Various API errors

**Example:**
```python
from src.transcription import transcribe_youtube_audio

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
output = "projects/MyProject/0_transcript.txt"
result = transcribe_youtube_audio(url, output)
print(f"Transcript saved to: {result}")
```

**Environment Variables:**
- `GOOGLE_STT_LANG` (optional): Language code (default: `en-US`)
- `GOOGLE_STT_BUCKET` (required for >10MB files): GCS bucket name

**Notes:**
- Automatically detects file size and uses GCS for files >10MB
- Uses long-running recognition (up to 480 minutes)
- Converts audio to FLAC (mono, 16kHz) for optimal quality
- Cleans up temporary files automatically

---

### `_download_audio_to_temp(url)`

Downloads audio from YouTube URL to temporary file.

**Parameters:**
- `url` (str): YouTube video URL

**Returns:**
- `str`: Path to downloaded MP3 file

**Notes:**
- Uses yt-dlp with best audio quality
- Saves to system temp directory
- Overwrites existing files

---

### `_convert_to_flac(mp3_path)`

Converts MP3 to FLAC format optimized for Speech-to-Text.

**Parameters:**
- `mp3_path` (str): Path to MP3 file

**Returns:**
- `str`: Path to converted FLAC file

**Notes:**
- Converts to mono (1 channel)
- Sets sample rate to 16kHz
- Uses pydub for conversion

---

### `_upload_to_gcs(file_path)`

Uploads file to Google Cloud Storage.

**Parameters:**
- `file_path` (str): Path to file to upload

**Returns:**
- `tuple`: (gcs_uri, blob) - GCS URI and blob object

**Raises:**
- `ValueError`: If `GOOGLE_STT_BUCKET` not set

**Notes:**
- Generates unique blob name with UUID
- Uploads to `transcription-temp/` prefix
- Returns blob for later cleanup

---

### `_delete_from_gcs(blob)`

Deletes blob from Google Cloud Storage.

**Parameters:**
- `blob`: GCS blob object from `_upload_to_gcs()`

**Notes:**
- Handles errors gracefully (prints warning)
- Called automatically after transcription

---

### `_get_speech_client()`

Creates Google Cloud Speech-to-Text client.

**Returns:**
- `speech.SpeechClient`: Configured client instance

**Notes:**
- Uses Application Default Credentials (ADC)
- Caches client instance

---

## Summarization Module

**File:** `src/summarization.py`

### `summarize_transcript(transcript_path, summary_path)`

Summarizes transcript using Google Gemini.

**Parameters:**
- `transcript_path` (str): Path to transcript file
- `summary_path` (str): Path to save summary file

**Returns:**
- `str`: Path to saved summary file

**Example:**
```python
from src.summarization import summarize_transcript

transcript = "projects/MyProject/0_transcript.txt"
summary = "projects/MyProject/1_summary.txt"
result = summarize_transcript(transcript, summary)
```

**Environment Variables:**
- `GOOGLE_API_KEY` (required): Gemini API key

**Notes:**
- Uses `gemini-1.5-flash` model
- Prompt-engineered for engaging YouTube-style content
- Handles long transcripts (up to model limit)

---

## Text-to-Speech Module

**File:** `src/text_to_speech.py`

### `synthesize_speech(summary_path, audio_path)`

Converts text to speech using Google Cloud TTS.

**Parameters:**
- `summary_path` (str): Path to summary text file
- `audio_path` (str): Path to save audio file (MP3)

**Returns:**
- `str`: Path to saved audio file

**Example:**
```python
from src.text_to_speech import synthesize_speech

summary = "projects/MyProject/1_summary.txt"
audio = "projects/MyProject/2_audio.mp3"
result = synthesize_speech(summary, audio)
```

**Environment Variables:**
- `GOOGLE_TTS_VOICE` (optional): Voice name (default: `en-US-Studio-O`)
- `GOOGLE_TTS_LANG` (optional): Language code (default: `en-US`)

**Notes:**
- Automatically chunks text at 4500 characters
- Respects paragraph boundaries
- Combines chunks into single MP3
- Uses Studio voices for best quality

---

### `split_text(text, limit)`

Splits text into chunks respecting paragraph boundaries.

**Parameters:**
- `text` (str): Text to split
- `limit` (int): Maximum characters per chunk

**Returns:**
- `list[str]`: List of text chunks

**Example:**
```python
from src.text_to_speech import split_text

text = "Long text here..."
chunks = split_text(text, 4500)
print(f"Split into {len(chunks)} chunks")
```

---

### `list_voices(language_code=None)`

Lists available Google Cloud TTS voices.

**Parameters:**
- `language_code` (str, optional): Filter by language (e.g., `en-US`)

**Returns:**
- `list[dict]`: List of voice info dicts with keys:
  - `name` (str): Voice name
  - `language_codes` (list): Supported languages
  - `gender` (str): Voice gender
  - `natural_sample_rate` (int): Sample rate in Hz

**Example:**
```python
from src.text_to_speech import list_voices

voices = list_voices("en-US")
for voice in voices:
    print(f"{voice['name']} - {voice['gender']}")
```

---

### `print_voices(language_code=None)`

Prints available voices in formatted table.

**Parameters:**
- `language_code` (str, optional): Filter by language

**Example:**
```python
from src.text_to_speech import print_voices

print_voices("en-US")
```

**CLI Usage:**
```bash
python -m src.text_to_speech --list-voices en-US
```

---

## Image Prompting Module

**File:** `src/image_prompting.py`

### `generate_image_prompts(summary_path, audio_path, output_path)`

Generates image prompts based on summary and audio duration.

**Parameters:**
- `summary_path` (str): Path to summary file
- `audio_path` (str): Path to audio file (for duration calculation)
- `output_path` (str): Path to save prompts JSON

**Returns:**
- `str`: Path to saved prompts file

**Example:**
```python
from src.image_prompting import generate_image_prompts

summary = "projects/MyProject/1_summary.txt"
audio = "projects/MyProject/2_audio.mp3"
prompts = "projects/MyProject/3_image_prompts.json"
result = generate_image_prompts(summary, audio, prompts)
```

**Output Format:**
```json
[
  "A futuristic cityscape at sunset",
  "Close-up of advanced technology",
  "People collaborating in modern office"
]
```

**Environment Variables:**
- `GOOGLE_API_KEY` (required): Gemini API key

**Notes:**
- Calculates image count: 1 image per 10 seconds of audio
- Uses Gemini Flash for prompt generation
- Outputs JSON array of strings

---

## Image Creation Module

**File:** `src/image_creation.py`

### `create_images_from_prompts(prompts_path, output_dir)`

Generates images from prompts using Vertex AI Imagen.

**Parameters:**
- `prompts_path` (str): Path to prompts JSON file
- `output_dir` (str): Directory to save generated images

**Returns:**
- `str`: Path to output directory

**Example:**
```python
from src.image_creation import create_images_from_prompts

prompts = "projects/MyProject/3_image_prompts.json"
images_dir = "projects/MyProject/5_images"
result = create_images_from_prompts(prompts, images_dir)
```

**Output:**
- Creates directory if not exists
- Saves images as `image_0.png`, `image_1.png`, etc.
- PNG format, base64-decoded from API

**Environment Variables:**
- `GOOGLE_APPLICATION_CREDENTIALS` (required): Service account JSON path
- `VERTEX_AI_PROJECT` (optional): GCP project ID
- `VERTEX_AI_LOCATION` (optional): Region (default: `us-central1`)

**Notes:**
- Sequential generation (one at a time)
- Each image takes ~5-10 seconds
- Uses Vertex AI Imagen model

---

## Metadata Generation Module

**File:** `src/metadata_generation.py`

### `generate_metadata(summary_path, output_path)`

Generates video metadata (title, description, hashtags) using Gemini.

**Parameters:**
- `summary_path` (str): Path to summary file
- `output_path` (str): Path to save metadata JSON

**Returns:**
- `str`: Path to saved metadata file

**Example:**
```python
from src.metadata_generation import generate_metadata

summary = "projects/MyProject/1_summary.txt"
metadata = "projects/MyProject/4_metadata.json"
result = generate_metadata(summary, metadata)
```

**Output Format:**
```json
{
  "title": "Amazing Discovery in AI Research",
  "description": "Detailed description of the video content...",
  "hashtags": ["#AI", "#Technology", "#Innovation"]
}
```

**Environment Variables:**
- `GOOGLE_API_KEY` (required): Gemini API key

**Notes:**
- Uses Gemini Flash for generation
- Outputs structured JSON
- Optimized for YouTube metadata

---

## Video Composition Module

**File:** `src/video_composition.py`

### `compose_video_from_assets(audio_path, images_dir, output_path)`

Composes final video from audio and images using MoviePy.

**Parameters:**
- `audio_path` (str): Path to audio file (MP3)
- `images_dir` (str): Directory containing images
- `output_path` (str): Path to save final video (MP4)

**Returns:**
- `str`: Path to saved video file

**Example:**
```python
from src.video_composition import compose_video_from_assets

audio = "projects/MyProject/2_audio.mp3"
images = "projects/MyProject/5_images"
video = "projects/MyProject/6_final_video.mp4"
result = compose_video_from_assets(audio, images, video)
```

**Video Specifications:**
- Resolution: 1080p (1920x1080)
- Format: MP4
- Codec: libx264
- Audio: AAC
- Transitions: Crossfade between images

**Notes:**
- Images timed evenly across audio duration
- Automatic crossfade transitions
- Requires FFmpeg installed
- Uses MoviePy 2.x API

---

## Common Patterns

### Error Handling

All functions follow this pattern:
```python
try:
    result = some_function(input_path, output_path)
    print(f"✅ Success: {result}")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    raise
```

### File Path Validation

Functions expect absolute paths:
```python
import os

# Good
path = "/home/user/projects/MyProject/0_transcript.txt"

# Bad (relative)
path = "0_transcript.txt"

# Convert relative to absolute
path = os.path.abspath("0_transcript.txt")
```

### Environment Variables

Load at module level:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
```

---

## Testing

### Unit Test Example

```python
from unittest.mock import patch, MagicMock
from src.transcription import transcribe_youtube_audio

@patch('src.transcription._get_speech_client')
@patch('src.transcription._convert_to_flac')
@patch('src.transcription._download_audio_to_temp')
def test_transcribe(mock_download, mock_convert, mock_client):
    # Setup mocks
    mock_download.return_value = "/tmp/audio.mp3"
    mock_convert.return_value = "/tmp/audio.flac"
    
    mock_client_instance = MagicMock()
    mock_client.return_value = mock_client_instance
    
    # Mock operation result
    mock_operation = MagicMock()
    mock_client_instance.long_running_recognize.return_value = mock_operation
    
    mock_response = MagicMock()
    mock_result = MagicMock()
    mock_alternative = MagicMock()
    mock_alternative.transcript = "Test transcript"
    mock_result.alternatives = [mock_alternative]
    mock_response.results = [mock_result]
    mock_operation.result.return_value = mock_response
    
    # Test
    result = transcribe_youtube_audio("https://youtube.com/...", "/tmp/output.txt")
    
    # Verify
    assert os.path.exists(result)
    with open(result) as f:
        assert f.read() == "Test transcript"
```

### Integration Test Example

```python
import pytest
from src.text_to_speech import synthesize_speech

@pytest.mark.integration
def test_tts_integration(tmp_path):
    # Requires valid credentials
    summary_path = tmp_path / "summary.txt"
    summary_path.write_text("This is a test summary.")
    
    audio_path = tmp_path / "audio.mp3"
    
    result = synthesize_speech(str(summary_path), str(audio_path))
    
    assert os.path.exists(result)
    assert os.path.getsize(result) > 0
```

---

## CLI Usage

### Run Individual Stages

```bash
# Transcription
python -c "from src.transcription import transcribe_youtube_audio; transcribe_youtube_audio('URL', 'output.txt')"

# Summarization
python -c "from src.summarization import summarize_transcript; summarize_transcript('transcript.txt', 'summary.txt')"

# TTS
python -c "from src.text_to_speech import synthesize_speech; synthesize_speech('summary.txt', 'audio.mp3')"

# List voices
python -m src.text_to_speech --list-voices en-US
```

---

## Constants

### `src/transcription.py`
- `DEFAULT_LANGUAGE = "en-US"` - Default STT language
- `MAX_INLINE_AUDIO_SIZE = 10 * 1024 * 1024` - 10MB limit for inline audio

### `src/text_to_speech.py`
- `CHUNK_LIMIT = 4500` - Max characters per TTS chunk
- `DEFAULT_VOICE = "en-US-Studio-O"` - Default voice
- `DEFAULT_LANG = "en-US"` - Default language

---

## Dependencies

### Core Libraries
- `google-cloud-speech` - Speech-to-Text
- `google-cloud-texttospeech` - Text-to-Speech
- `google-cloud-storage` - Cloud Storage
- `langchain-google-genai` - Gemini integration
- `vertexai` - Vertex AI Imagen
- `moviepy` - Video composition
- `pydub` - Audio processing
- `yt-dlp` - YouTube downloads
- `python-dotenv` - Environment variables

### System Requirements
- FFmpeg (for audio/video processing)
- Python 3.8+

---

## Version History

**Current Version:** 1.0.0 (Feb 2026)

**Changes:**
- Migrated from OpenAI/Anthropic to Google Cloud/Gemini
- Added GCS support for large audio files
- Increased timeout to 60 minutes
- Updated to MoviePy 2.x
- Added JSON metadata output
- Improved error handling and logging

---

## Support

For issues or questions:
- Check [SETUP.md](SETUP.md) for configuration help
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for design details
- See session logs for development history
- Test with unit tests first (`pytest tests/unit/ -v`)
