import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from yt_dlp import YoutubeDL
from pydub import AudioSegment

# Load environment variables from .env file
load_dotenv()
client = OpenAI()

# Whisper API has a 25MB file size limit. At 192kbps MP3, ~10 min is safe.
# We use 10 minutes (600 seconds) as chunk duration to stay well under limit.
CHUNK_DURATION_MS = 10 * 60 * 1000  # 10 minutes in milliseconds

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

def _split_audio_into_chunks(audio_path: str) -> list[str]:
    """
    Splits an audio file into chunks of CHUNK_DURATION_MS milliseconds.
    Returns a list of paths to temporary chunk files.
    """
    audio = AudioSegment.from_mp3(audio_path)
    duration_ms = len(audio)
    
    # If audio is short enough, no need to split
    if duration_ms <= CHUNK_DURATION_MS:
        return [audio_path]
    
    chunks = []
    temp_dir = tempfile.gettempdir()
    num_chunks = (duration_ms // CHUNK_DURATION_MS) + 1
    
    print(f"-> Audio is {duration_ms // 1000 // 60} minutes. Splitting into {num_chunks} chunks...")
    
    for i in range(num_chunks):
        start_ms = i * CHUNK_DURATION_MS
        end_ms = min((i + 1) * CHUNK_DURATION_MS, duration_ms)
        
        if start_ms >= duration_ms:
            break
            
        chunk = audio[start_ms:end_ms]
        chunk_path = os.path.join(temp_dir, f"transcription_chunk_{i}.mp3")
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)
    
    return chunks


def transcribe_youtube_audio(youtube_url: str, output_transcript_path: str):
    """
    Downloads audio from a YouTube URL, transcribes it, and saves the transcript
    to the specified path.

    Args:
        youtube_url (str): The URL of the YouTube video.
        output_transcript_path (str): The absolute path to save the transcript file.
    """
    print(f"-> Starting transcription for URL: {youtube_url}")
    
    # 1. Download audio to a temporary file
    print("-> Downloading audio...")
    temp_audio_path = _download_audio_to_temp(youtube_url)

    # 2. Split audio into chunks if needed (Whisper API has 25MB limit)
    chunk_paths = _split_audio_into_chunks(temp_audio_path)
    
    # 3. Transcribe each chunk and combine results
    print("-> Transcribing audio with Whisper API...")
    transcript_parts = []
    
    for i, chunk_path in enumerate(chunk_paths):
        if len(chunk_paths) > 1:
            print(f"   - Transcribing chunk {i + 1}/{len(chunk_paths)}...")
        
        with open(chunk_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file, 
                response_format="text"
            )
        transcript_parts.append(transcript)
        
        # Clean up chunk file (but not the original if it wasn't split)
        if chunk_path != temp_audio_path:
            os.remove(chunk_path)
    
    # Combine all transcript parts
    full_transcript = " ".join(transcript_parts)

    # 4. Save the transcript to the specified output file
    # Ensure the directory exists
    output_dir = os.path.dirname(output_transcript_path)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_transcript_path, "w", encoding='utf-8') as f:
        f.write(full_transcript)

    # 5. Clean up the original temporary audio file
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)

    print(f"✅ Transcription complete. Saved to: {output_transcript_path}")
    return output_transcript_path
