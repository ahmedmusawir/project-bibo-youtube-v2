import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import PromptTemplate

# NEW: Unified ChatGoogleGenerativeAI (4.0.0+) supports both Gemini API and Vertex AI
# Passing 'project' parameter triggers Vertex AI backend (uses ADC for auth)
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_classic.chains.summarize import load_summarize_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.utils.config import get_summarization_llm

# Load environment variables
load_dotenv()


def summarize_transcript(transcript_path: str, summary_path: str) -> str:
    """
    Summarizes a transcript using map-reduce strategy for reliable output.

    Args:
        transcript_path (str): The absolute path to the input transcript file.
        summary_path (str): The absolute path to save the output summary file.

    Returns:
        str: The path to the saved summary file.
    """
    # Set up verbose logging to file
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"summarization_verbose_{timestamp}.log"
    log_handle = open(log_file, 'w', encoding='utf-8')

    # Tee output to both console and log file
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
    print(f"-> Loading transcript from: {transcript_path}")

    try:
        loader = TextLoader(transcript_path)
        docs = loader.load()

        print("-> Splitting transcript into chunks for map-reduce processing...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,  # Each chunk ~500-700 words
            chunk_overlap=200,  # Small overlap for context continuity
        )
        split_docs = text_splitter.split_documents(docs)
        print(f"   Split into {len(split_docs)} chunks")

        # MAP PROMPT: Summarize each chunk concisely
        map_template = """You are summarizing a section of a YouTube video transcript.

Your task: Extract the key information from this section in 200-300 words. Focus on:
- Main topics and themes
- Important facts, stats, or examples
- Key quotes or insights

Remove ads, sponsorship mentions, and filler content. Be dense and informative.

SECTION:
{text}

CONCISE SUMMARY (200-300 words):"""

        map_prompt = PromptTemplate(template=map_template, input_variables=["text"])

        # COMBINE PROMPT: Turn summaries into final polished script
        combine_template = """You are an expert YouTube script editor creating a documentary-style narration script.

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
{text}

FINAL SCRIPT (920-950 words, ending with "Thanks for watching"):"""

        combine_prompt = PromptTemplate(template=combine_template, input_variables=["text"])

        print("-> Initializing LLM...")
        # Use Pro for quality (user wants to test Pro vs Flash)
        model_name = get_summarization_llm()  # From config: gemini-2.5-pro
        print(f"   Using model: {model_name}")

        # Unified ChatGoogleGenerativeAI - passing 'project' triggers Vertex AI backend
        # Uses GOOGLE_APPLICATION_CREDENTIALS for auth (ADC pattern)
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),  # Triggers Vertex AI!
            location=os.getenv("GOOGLE_CLOUD_REGION", "us-east1"),
            temperature=0.8,
            max_output_tokens=8192,
        )

        print("-> Creating map-reduce summarization chain...")
        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            verbose=True,  # Always verbose for debugging
        )

        print("-> Running map-reduce chain...")
        result = chain.invoke(split_docs)

        print(f"   Result type: {type(result)}")

        # Extract the output (it's in a dict)
        if isinstance(result, dict):
            final_text = result.get("output_text", "")
            if not final_text:
                print(f"   ⚠️  Warning: 'output_text' key not found in result. Keys: {result.keys()}")
                final_text = result.get("text", "") or result.get("result", "") or str(result)
        else:
            final_text = str(result)

        word_count = len(final_text.split())
        char_count = len(final_text)

        print(f"   Extracted text length: {len(final_text)} characters")
        print(f"-> Final script generated ({char_count} characters, {word_count} words)")

        # Validate output
        if word_count < 800:
            print(f"   ⚠️  WARNING: Output is shorter than target ({word_count} words, target 900)")
            print(f"   Saving anyway for inspection...")
        elif word_count > 950:
            print(f"   ⚠️  Warning: Output is longer than expected ({word_count} words)")
        else:
            print(f"   ✅ Word count looks good ({word_count} words)")

        # Ensure the output directory exists
        output_dir = os.path.dirname(summary_path)
        os.makedirs(output_dir, exist_ok=True)

        Path(summary_path).write_text(final_text, encoding='utf-8')
        print(f"✅ Summary saved to {summary_path}")

        return summary_path

    finally:
        # Restore stdout and close log file
        sys.stdout = original_stdout
        log_handle.close()
        print(f"📝 Verbose log saved to: {log_file}")
