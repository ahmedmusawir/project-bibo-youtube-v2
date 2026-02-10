import os
import tempfile
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define a constant for the API character limit
CHUNK_LIMIT = 4096 # OpenAI TTS API has a 4096 character limit per request

def split_text(text: str, limit: int) -> list[str]:
    """Splits text into chunks based on a character limit, respecting paragraphs."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= limit:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def synthesize_speech(summary_path: str, audio_path: str) -> str:
    """
    Synthesizes speech from a summary file and saves it to an audio file.

    Args:
        summary_path (str): The absolute path to the input summary file.
        audio_path (str): The absolute path to save the output audio file.

    Returns:
        str: The path to the saved audio file.
    """
    print(f"\n-> Reading summary from: {summary_path}")
    with open(summary_path, "r", encoding="utf-8") as f:
        text = f.read()

    print("-> Splitting text into manageable chunks...")
    chunks = split_text(text, CHUNK_LIMIT)
    print(f"-> Text split into {len(chunks)} chunks.")

    combined_audio = AudioSegment.empty()
    temp_files = []

    print("-> Starting synthesis for each chunk...")
    for i, chunk in enumerate(chunks):
        # Create a temporary file for each chunk
        temp_fd, temp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(temp_fd)
        temp_files.append(temp_path)
        
        print(f"   - Synthesizing chunk {i+1}/{len(chunks)}...")
        with client.audio.speech.with_streaming_response.create(
            model="tts-1-hd",
            voice="onyx",
            input=chunk
        ) as response:
            response.stream_to_file(temp_path)
        
        # Load the synthesized chunk and append it to the combined audio
        combined_audio += AudioSegment.from_mp3(temp_path)

    # Ensure the output directory exists
    output_dir = os.path.dirname(audio_path)
    os.makedirs(output_dir, exist_ok=True)

    print(f"-> Exporting combined audio to: {audio_path}")
    combined_audio.export(audio_path, format="mp3")

    # Clean up temporary files
    for temp_file in temp_files:
        os.remove(temp_file)

    print(f"✅ Final audio saved to {audio_path}")
    return audio_path
