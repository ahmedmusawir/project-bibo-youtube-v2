import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from pydub import AudioSegment
from google.cloud import texttospeech

# Load environment variables
load_dotenv()

# Google Cloud TTS has a 5000 byte limit per request (roughly 5000 chars for ASCII)
# We use 4500 to be safe with multi-byte characters
CHUNK_LIMIT = 4500

# Voice configuration from environment variables
DEFAULT_VOICE = "en-US-Studio-O"  # A high-quality Studio voice
DEFAULT_LANG = "en-US"


def _get_tts_client():
    """Returns a Google Cloud TTS client. Uses ADC for authentication."""
    return texttospeech.TextToSpeechClient()


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


def list_voices(language_code: str = None) -> list[dict]:
    """
    Lists available Google Cloud TTS voices.
    
    Args:
        language_code: Optional filter by language (e.g., "en-US", "en-GB").
                      If None, lists all voices.
    
    Returns:
        List of dicts with voice info: name, language_codes, ssml_gender.
    """
    client = _get_tts_client()
    response = client.list_voices(language_code=language_code)
    
    voices = []
    for voice in response.voices:
        gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
        voices.append({
            "name": voice.name,
            "language_codes": list(voice.language_codes),
            "gender": gender,
            "natural_sample_rate": voice.natural_sample_rate_hertz,
        })
    return voices


def print_voices(language_code: str = None):
    """Prints available voices in a readable format."""
    voices = list_voices(language_code)
    print(f"\n{'Voice Name':<30} {'Gender':<10} {'Languages':<20} {'Sample Rate'}")
    print("-" * 80)
    for v in sorted(voices, key=lambda x: x["name"]):
        langs = ", ".join(v["language_codes"])
        print(f"{v['name']:<30} {v['gender']:<10} {langs:<20} {v['natural_sample_rate']}")
    print(f"\nTotal: {len(voices)} voices")


def synthesize_speech(summary_path: str, audio_path: str) -> str:
    """
    Synthesizes speech from a summary file and saves it to an audio file.

    Args:
        summary_path (str): The absolute path to the input summary file.
        audio_path (str): The absolute path to save the output audio file.

    Returns:
        str: The path to the saved audio file.
    """
    # Get voice config from environment
    voice_name = os.getenv("GOOGLE_TTS_VOICE", DEFAULT_VOICE)
    language_code = os.getenv("GOOGLE_TTS_LANG", DEFAULT_LANG)
    
    print(f"\n-> Reading summary from: {summary_path}")
    with open(summary_path, "r", encoding="utf-8") as f:
        text = f.read()

    print("-> Splitting text into manageable chunks...")
    chunks = split_text(text, CHUNK_LIMIT)
    print(f"-> Text split into {len(chunks)} chunks.")
    print(f"-> Using voice: {voice_name} ({language_code})")

    client = _get_tts_client()
    
    # Configure voice
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
    )
    
    # Configure audio output as MP3
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
    )

    combined_audio = AudioSegment.empty()
    temp_files = []

    print("-> Starting synthesis for each chunk...")
    for i, chunk in enumerate(chunks):
        print(f"   - Synthesizing chunk {i+1}/{len(chunks)}...")
        
        synthesis_input = texttospeech.SynthesisInput(text=chunk)
        
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )
        
        # Write to temp file
        temp_fd, temp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(temp_fd)
        temp_files.append(temp_path)
        
        with open(temp_path, "wb") as out:
            out.write(response.audio_content)
        
        # Load and append to combined audio
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


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--list-voices":
        lang = sys.argv[2] if len(sys.argv) > 2 else None
        print_voices(lang)
    else:
        print("Usage:")
        print("  python -m src.text_to_speech --list-voices [language_code]")
        print("  Example: python -m src.text_to_speech --list-voices en-US")
