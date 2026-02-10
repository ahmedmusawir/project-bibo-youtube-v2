import os
import tempfile
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from google.cloud import speech
from google.cloud import storage

# Load environment variables from .env file
load_dotenv()

# Default language for transcription
DEFAULT_LANGUAGE = "en-US"

# Google Cloud Speech-to-Text has a 10MB limit for inline audio
# For larger files, we must upload to GCS
MAX_INLINE_AUDIO_SIZE = 10 * 1024 * 1024  # 10MB in bytes

def _download_audio_to_temp(url: str) -> str:
    """Downloads audio to a temporary file and returns the path."""
    temp_dir = tempfile.gettempdir()
    temp_audio_path = os.path.join(temp_dir, "temp_audio_for_transcription.mp3")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        # Use a fixed name in a temp directory
        'outtmpl': os.path.join(temp_dir, "temp_audio_for_transcription"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'overwrite': True, # Overwrite if the file exists
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return temp_audio_path

def _get_speech_client():
    """Returns a Google Cloud Speech client. Uses ADC for authentication."""
    return speech.SpeechClient()


def _convert_to_flac(mp3_path: str) -> str:
    """Converts MP3 to FLAC for better Speech-to-Text compatibility."""
    from pydub import AudioSegment
    
    flac_path = mp3_path.replace(".mp3", ".flac")
    audio = AudioSegment.from_mp3(mp3_path)
    
    # Convert to mono and 16kHz sample rate (optimal for Speech-to-Text)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    
    audio.export(flac_path, format="flac")
    return flac_path


def _upload_to_gcs(file_path: str) -> str:
    """
    Uploads a file to Google Cloud Storage and returns the GCS URI.
    Uses a temporary bucket or the bucket specified in GOOGLE_STT_BUCKET env var.
    """
    bucket_name = os.getenv("GOOGLE_STT_BUCKET")
    
    if not bucket_name:
        raise ValueError(
            "Large audio file detected (>10MB). "
            "Please set GOOGLE_STT_BUCKET environment variable to a GCS bucket name. "
            "Example: GOOGLE_STT_BUCKET=my-transcription-bucket"
        )
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # Generate unique blob name
    blob_name = f"transcription-temp/{uuid.uuid4()}.flac"
    blob = bucket.blob(blob_name)
    
    print(f"   - Uploading to GCS: gs://{bucket_name}/{blob_name}")
    blob.upload_from_filename(file_path)
    
    gcs_uri = f"gs://{bucket_name}/{blob_name}"
    return gcs_uri, blob


def _delete_from_gcs(blob):
    """Deletes a blob from GCS."""
    try:
        blob.delete()
        print(f"   - Cleaned up GCS file: {blob.name}")
    except Exception as e:
        print(f"   - Warning: Could not delete GCS file {blob.name}: {e}")


def transcribe_youtube_audio(youtube_url: str, output_transcript_path: str):
    """
    Downloads audio from a YouTube URL, transcribes it using Google Cloud Speech-to-Text,
    and saves the transcript to the specified path.

    Args:
        youtube_url (str): The URL of the YouTube video.
        output_transcript_path (str): The absolute path to save the transcript file.
    """
    print(f"-> Starting transcription for URL: {youtube_url}")
    
    # Get language from env or use default
    language_code = os.getenv("GOOGLE_STT_LANG", DEFAULT_LANGUAGE)
    
    # 1. Download audio to a temporary file
    print("-> Downloading audio...")
    temp_audio_path = _download_audio_to_temp(youtube_url)

    # 2. Convert to FLAC for better compatibility
    print("-> Converting audio to FLAC...")
    flac_path = _convert_to_flac(temp_audio_path)
    
    # 3. Upload to GCS for long-running recognition
    # Note: long_running_recognize has a ~1 minute duration limit for inline audio,
    # so we always use GCS for YouTube videos (which are typically longer)
    file_size = os.path.getsize(flac_path)
    print(f"   - Audio file is {file_size / 1024 / 1024:.1f}MB")
    print("   - Uploading to Google Cloud Storage for long-running recognition...")
    gcs_uri, gcs_blob = _upload_to_gcs(flac_path)
    audio = speech.RecognitionAudio(uri=gcs_uri)
    
    # 4. Configure recognition request
    print(f"-> Transcribing audio with Google Cloud Speech-to-Text ({language_code})...")
    client = _get_speech_client()
    
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code=language_code,
        enable_automatic_punctuation=True,
        model="latest_long",  # Optimized for long-form content like videos
    )
    
    # 5. Perform transcription using long-running recognition
    print("   - Starting long-running recognition (this may take a few minutes)...")
    operation = client.long_running_recognize(config=config, audio=audio)
    
    print("   - Waiting for transcription to complete...")
    print("   - Note: Large files may take 10-30 minutes depending on audio length")
    response = operation.result(timeout=3600)  # 60 minute timeout for very long videos
    
    # 6. Extract transcript from response
    transcript_parts = []
    for result in response.results:
        # Get the highest confidence alternative
        if result.alternatives:
            transcript_parts.append(result.alternatives[0].transcript)
    
    full_transcript = " ".join(transcript_parts)

    # 7. Save the transcript to the specified output file
    output_dir = os.path.dirname(output_transcript_path)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_transcript_path, "w", encoding='utf-8') as f:
        f.write(full_transcript)

    # 8. Clean up temporary files and GCS blob
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)
    if os.path.exists(flac_path):
        os.remove(flac_path)
    if gcs_blob:
        _delete_from_gcs(gcs_blob)

    print(f"✅ Transcription complete. Saved to: {output_transcript_path}")
    return output_transcript_path
