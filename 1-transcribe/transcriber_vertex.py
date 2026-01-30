from pathlib import Path
from yt_dlp import YoutubeDL
from pydub import AudioSegment
from google.cloud import speech
import os
import re
from dotenv import load_dotenv
from datetime import datetime

# === Setup ===
load_dotenv()

def extract_video_id(url):
    # Handles standard and shortened URLs
    match = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})', url)
    return match.group(1) if match else None

def log(message, logfile):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {message}\n")
    print(message)

# === Step 1: User Input ===
youtube_url = input("Enter YouTube URL: ").strip()
video_id = extract_video_id(youtube_url)
if not video_id:
    print("❌ Invalid YouTube URL or ID not found.")
    exit(1)

# === Step 2: Prepare Output Folders ===
BASE = Path("output") / video_id
AUDIO_DIR = BASE / "audio"
TRANSCRIPT_DIR = BASE / "transcript"
LOG_DIR = BASE / "logs"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "transcriber_vertex.log"

log(f"Working with video ID: {video_id}", LOG_FILE)

# === Step 3: Download Audio ===
mp3_path = AUDIO_DIR / "original.mp3"
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': str(mp3_path.with_suffix('')),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': False
}
if not mp3_path.exists():
    try:
        log("Downloading audio...", LOG_FILE)
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        log("Audio download complete.", LOG_FILE)
    except Exception as e:
        log(f"❌ Error downloading audio: {e}", LOG_FILE)
        exit(1)
else:
    log("Audio already downloaded, skipping.", LOG_FILE)

# === Step 4: Convert MP3 to WAV ===
wav_path = AUDIO_DIR / "original.wav"
if not wav_path.exists():
    try:
        log("Converting mp3 to wav...", LOG_FILE)
        audio = AudioSegment.from_mp3(mp3_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(wav_path, format="wav")
        log("Audio conversion complete.", LOG_FILE)
    except Exception as e:
        log(f"❌ Error converting audio: {e}", LOG_FILE)
        exit(1)
else:
    log("WAV already exists, skipping conversion.", LOG_FILE)

# === Step 5: Split Audio if Needed ===
CHUNK_MS = 60_000  # 60 seconds
audio = AudioSegment.from_wav(wav_path)
chunks = []
if len(audio) > CHUNK_MS:
    log("Splitting audio into 60-second chunks...", LOG_FILE)
    for i in range(0, len(audio), CHUNK_MS):
        chunk = audio[i:i+CHUNK_MS]
        chunk_path = AUDIO_DIR / f"chunk_{i//CHUNK_MS+1}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    log(f"Audio split into {len(chunks)} chunks.", LOG_FILE)
else:
    chunks = [wav_path]
    log("Audio is under 60s, not splitting.", LOG_FILE)

# === Step 6: Transcribe Each Chunk ===
client = speech.SpeechClient()
transcript_path = TRANSCRIPT_DIR / "transcript.txt"

with open(transcript_path, "w", encoding="utf-8") as outfile:
    for idx, chunk_path in enumerate(chunks, 1):
        log(f"Transcribing chunk {idx}...", LOG_FILE)
        try:
            with open(chunk_path, "rb") as audio_file:
                content = audio_file.read()
            audio_google = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
                enable_automatic_punctuation=True,
            )
            response = client.recognize(config=config, audio=audio_google)
            chunk_text = ""
            for result in response.results:
                chunk_text += result.alternatives[0].transcript + " "
            outfile.write(f"[Chunk {idx}]\n{chunk_text.strip()}\n\n")
            log(f"Chunk {idx} transcription done.", LOG_FILE)
        except Exception as e:
            log(f"❌ Error transcribing chunk {idx}: {e}", LOG_FILE)
            outfile.write(f"[Chunk {idx}] -- ERROR\n\n")

log(f"Transcript saved: {transcript_path}", LOG_FILE)
print(f"\nAll done! Transcript ready at {transcript_path}\nSee log file: {LOG_FILE}")

