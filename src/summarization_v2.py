"""
Clean summarization using google.genai SDK directly with Vertex AI.
No LangChain - just simple map-reduce with direct API calls.
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.oauth2 import service_account

load_dotenv()


def split_into_chunks(text: str, chunk_size: int = 3000, overlap: int = 200) -> list[str]:
    """
    Simple text chunking - split into fixed-size chunks with overlap.

    Args:
        text: Full transcript text
        chunk_size: Max characters per chunk
        overlap: Characters of overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        # Extract chunk
        end = start + chunk_size

        # If not the last chunk, try to find a good break point (period, newline)
        if end < text_len:
            # Look for sentence end within last 200 chars of chunk
            search_start = max(start, end - 200)
            # Try to find ". " or ".\n"
            last_period = max(text.rfind('. ', search_start, end), text.rfind('.\n', search_start, end))
            if last_period > start:
                end = last_period + 1  # Include the period

        chunks.append(text[start:end].strip())

        # Move start forward, accounting for overlap
        start = end - overlap if end < text_len else text_len

    return chunks


def generate_chunk_summary(client: genai.Client, model: str, chunk: str) -> str:
    """
    Call Gemini to summarize a single chunk (200-300 words).

    Args:
        client: Initialized genai.Client
        model: Model name (e.g., "gemini-3-flash-preview")
        chunk: Text chunk to summarize

    Returns:
        Summary text (200-300 words)
    """
    prompt = f"""You are summarizing a section of a YouTube video transcript.

Your task: Extract the key information from this section in 200-300 words. Focus on:
- Main topics and themes
- Important facts, stats, or examples
- Key quotes or insights

Remove ads, sponsorship mentions, and filler content. Be dense and informative.

SECTION:
{chunk}

CONCISE SUMMARY (200-300 words):"""

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]

    config = types.GenerateContentConfig(
        temperature=0.8,
        max_output_tokens=8192,
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    return response.text


def generate_final_script(client: genai.Client, model: str, summaries: list[str]) -> str:
    """
    Call Gemini to combine chunk summaries into final 900-word script.

    Args:
        client: Initialized genai.Client
        model: Model name
        summaries: List of chunk summaries (200-300 words each)

    Returns:
        Final 900-word script
    """
    summaries_text = "\n\n".join(summaries)

    prompt = f"""You are an expert YouTube script editor creating a documentary-style narration script.

You've been given summaries of different sections of a video. Your task is to combine them into ONE cohesive, compelling 900-word script.

🔒 HARD CONSTRAINTS (obey 100%):
1. Final script length = 920-950 words (aim ~900). **IF draft > 950 words, TRIM until ≤920.**
2. No ads, sponsorships, or meta commentary
3. No framing language (e.g., "This video covers...")
4. MUST finish with "Thanks for watching"

📑 STRUCTURE:
- 1-sentence HOOK that sparks curiosity
- 2-3 flowing narrative paragraphs (each ≤150 words) explaining the story
- "Key Takeaways" section with 3-5 numbered points (1., 2., 3.) NOT bullets, ≤40 words each
- 1-sentence CLOSING that wraps it up

🎯 STYLE: Concise, vivid, accessible—think "mini-documentary for busy professionals"
- Use active voice and concrete examples
- Avoid jargon unless explained
- Create narrative flow between paragraphs

⚠️ AUDIO-FRIENDLY FORMATTING:
- NO asterisks (*) for emphasis—audio will read them as "asterisk"
- NO markdown formatting like **bold** or _italic_
- Use dashes (-) NOT asterisks (*) if you must use bullets (but prefer numbered lists)
- Clean plain text only

SECTION SUMMARIES:
{summaries_text}

FINAL SCRIPT (920-950 words, ending with "Thanks for watching"):"""

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]

    config = types.GenerateContentConfig(
        temperature=0.8,
        max_output_tokens=8192,
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    return response.text


def summarize_transcript(
    transcript_path: str,
    summary_path: str,
    model: str = "gemini-3-flash-preview",
    location: str = "global"
) -> str:
    """
    Summarize transcript using google.genai SDK with Vertex AI authentication.
    Uses map-reduce pattern: split → summarize chunks → combine into final script.

    Args:
        transcript_path: Path to input transcript file
        summary_path: Path to save output summary
        model: Gemini model name (default: gemini-3-flash-preview)
        location: Vertex AI location (default: global for preview models)

    Returns:
        Path to saved summary file
    """
    # Set up verbose logging
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"summarization_v2_{timestamp}.log"
    log_handle = open(log_file, 'w', encoding='utf-8')

    # Tee output to console and log
    original_stdout = sys.stdout
    class TeeOutput:
        def __init__(self, *files):
            self.files = files
        def write(self, data):
            for f in self.files:
                f.write(data)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()

    sys.stdout = TeeOutput(original_stdout, log_handle)

    print(f"📝 Logging to: {log_file}")
    print(f"🚀 Starting summarization with model: {model}")

    try:
        # 1. Initialize Vertex AI client with service account
        print("-> Setting up Vertex AI authentication...")
        creds = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        client = genai.Client(
            vertexai=True,
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=location,
            credentials=creds
        )
        print(f"   ✅ Connected to Vertex AI (project: {os.getenv('GOOGLE_CLOUD_PROJECT')}, location: {location})")

        # 2. Load transcript
        print(f"-> Loading transcript from: {transcript_path}")
        transcript = Path(transcript_path).read_text(encoding='utf-8')
        print(f"   Transcript length: {len(transcript)} characters")

        # 3. Split into chunks
        print("-> Splitting transcript into chunks...")
        chunks = split_into_chunks(transcript, chunk_size=3000, overlap=200)
        print(f"   Split into {len(chunks)} chunks")

        # 4. MAP PHASE: Summarize each chunk
        print("-> MAP PHASE: Summarizing each chunk...")
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            print(f"   Processing chunk {i}/{len(chunks)}...")
            summary = generate_chunk_summary(client, model, chunk)
            chunk_summaries.append(summary)
            word_count = len(summary.split())
            print(f"   ✅ Chunk {i} summary: {word_count} words")

        # 5. REDUCE PHASE: Combine into final script
        print("-> REDUCE PHASE: Combining summaries into final script...")
        final_script = generate_final_script(client, model, chunk_summaries)

        # 6. Validate output
        word_count = len(final_script.split())
        char_count = len(final_script)
        print(f"-> Final script generated: {char_count} characters, {word_count} words")

        if word_count < 800:
            print(f"   ⚠️  WARNING: Output is shorter than target ({word_count} words, target 900)")
        elif word_count > 950:
            print(f"   ⚠️  Warning: Output is longer than expected ({word_count} words)")
        else:
            print(f"   ✅ Word count looks good ({word_count} words)")

        # 7. Save output
        output_dir = os.path.dirname(summary_path)
        os.makedirs(output_dir, exist_ok=True)
        Path(summary_path).write_text(final_script, encoding='utf-8')
        print(f"✅ Summary saved to {summary_path}")

        return summary_path

    except Exception as e:
        print(f"❌ ERROR: {e}")
        raise

    finally:
        sys.stdout = original_stdout
        log_handle.close()
        print(f"📝 Verbose log saved to: {log_file}")


if __name__ == "__main__":
    # Quick test
    result = summarize_transcript(
        "projects/BBC_Robots/0_transcript.txt",
        "projects/BBC_Robots/1_summary_v2.txt",
        model="gemini-3-flash-preview",
        location="global"
    )
    print(f"\n✅ Done! Check: {result}")
