import os
import math
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from pydub import AudioSegment
from src.utils.config import get_prompting_llm

# Load environment variables
load_dotenv()

# === Primary Configuration ===
# This is now the main control for your video's pacing.
# Change this one value to adjust how many images are generated for the video.
SECONDS_PER_IMAGE = 20

# Initialize the language model (using config-driven model selection)
llm = ChatGoogleGenerativeAI(
    model=get_prompting_llm(),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.8,
)

def _calculate_num_images(audio_path: str, seconds_per_image: int) -> int:
    """Calculates the number of images needed based on audio length."""
    audio = AudioSegment.from_mp3(audio_path)
    duration_seconds = len(audio) / 1000
    return math.ceil(duration_seconds / seconds_per_image)

def _split_summary_into_chunks(summary: str, num_chunks: int) -> list[str]:
    """Splits the summary text into a specified number of roughly equal chunks."""
    words = summary.split()
    if not words:
        return []
    words_per_chunk = math.ceil(len(words) / num_chunks)
    text_chunks = []
    for i in range(0, len(words), words_per_chunk):
        chunk = " ".join(words[i:i + words_per_chunk])
        text_chunks.append(chunk)
    return text_chunks

def _generate_style_bible(summary_text: str) -> str:
    """Generates a Visual Style Bible from the full script text in 1_summary.txt.

    Analyzes the complete script and produces a 3-5 sentence visual style description
    covering: color palette, lighting style, camera perspective, texture/material feel,
    and overall cinematic tone. Describes STYLE only — not content or subjects.

    Args:
        summary_text: The full script text from 1_summary.txt.

    Returns:
        The style bible string (3-5 sentences, ~60-80 words).
    """
    print("-> Generating Visual Style Bible from script...")

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a visual style director for documentary video production. "
            "Your job is to analyze a script and produce a Visual Style Bible — a short description of the video's overall visual language.\n\n"
            "Rules:\n"
            "- Output EXACTLY 3-5 sentences, no more than 80 words total\n"
            "- Describe ONLY visual style: color palette, lighting, camera perspective, texture/materials, cinematic tone\n"
            "- Be concrete and specific (e.g., 'cool blue-toned lighting, glass and steel surfaces') — NEVER abstract (e.g., 'feeling of innovation')\n"
            "- Do NOT describe content, subjects, or story — the scene chunks provide that\n"
            "- Include this exact phrase: 'No text overlays, no watermarks, no logos rendered in the image.'\n"
            "- Describe a consistent photographic or cinematic style (e.g., 'documentary photography, shallow depth of field')\n"
            "- Output only the style bible text — no titles, no labels, no explanations"
        )),
        ("user", "Script:\n\n{summary_text}")
    ])

    chain = prompt_template | llm | StrOutputParser()
    style_bible = chain.invoke({"summary_text": summary_text})
    style_bible = style_bible.strip()

    print(f"✅ Style Bible generated ({len(style_bible.split())} words)")
    return style_bible


def generate_image_prompts(summary_path: str, audio_path: str, prompts_path: str, seconds_per_image: int = 20, style_bible_path: str = None) -> str:
    """
    Generates a synchronized list of image prompts based on a summary and an audio file.

    Uses a two-step process: first generates (or loads) a Visual Style Bible from the
    full script, then uses it as Gemini context when generating each per-scene prompt
    for visual coherence across the video.

    Args:
        summary_path (str): Path to the summary text file (1_summary.txt).
        audio_path (str): Path to the audio file for timing.
        prompts_path (str): Path to save the output prompts text file.
        seconds_per_image (int): Seconds of audio per image. Defaults to 20.
        style_bible_path (str, optional): Path to an existing style bible file.
            If provided and the file exists, skips regeneration and loads from file.
            If None, auto-derives path as 3a_style_bible.txt in the project directory.

    Returns:
        str: The path to the saved prompts file.
    """
    print("\n-> Generating image prompts based on audio timing...")
    print(f"   - Summary: {summary_path}")
    print(f"   - Audio: {audio_path}")

    # 1. Calculate the number of images needed
    num_images = _calculate_num_images(audio_path, SECONDS_PER_IMAGE)
    print(f"-> Audio duration requires {num_images} images (at {SECONDS_PER_IMAGE}s/image).")

    # 2. Read and split the summary text
    summary_text = Path(summary_path).read_text(encoding="utf-8").strip()
    text_chunks = _split_summary_into_chunks(summary_text, num_images)
    print(f"-> Summary split into {len(text_chunks)} chunks to match images.")

    # 3. Generate or load Visual Style Bible
    project_dir = os.path.dirname(prompts_path)
    if style_bible_path is None:
        style_bible_path = os.path.join(project_dir, "3a_style_bible.txt")

    if os.path.exists(style_bible_path) and os.path.getsize(style_bible_path) > 0:
        print(f"-> Loading existing Style Bible from: {style_bible_path}")
        style_bible = Path(style_bible_path).read_text(encoding="utf-8").strip()
    else:
        style_bible = _generate_style_bible(summary_text)
        os.makedirs(project_dir, exist_ok=True)
        Path(style_bible_path).write_text(style_bible, encoding="utf-8")
        print(f"-> Style Bible saved to: {style_bible_path}")

    # 4. Generate a prompt for each text chunk
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a visual scene director. Your job is to create a single, vivid visual prompt for an AI image generator. You must include these words (and more like them) in every prompt: [photorealistic] [high-resolution] [realistic lighting].\n"
            "The prompt should be a cinematic, highly-detailed description of the key idea in the following text chunk. Focus on one clear moment. Keep the prompt under 200 words.\n"
            "Output only the prompt itself — no extra text, no numbering, no explanations.\n"
            "Focus on the information. For example: if it says Claude 4, Gemini 2.5, ChatGPT, Poe, Perplexity, Apple, OpenAI, Anthropic, Gork, Mistral, Ollama, Meta, or any other brand or industry terms etc. try to include those words into your prompt and make sure those are reflected on the images. This is why, since we are using auto generated images, those words will be used a the visual queues for our viewers while audio is playing. It's always better when the user sees the text written clearly while the words are being said. This anchors the viewer with the audio to the visuals. So this is very important that the images we create reflect what is being said ... if possible, let's push for making visuals as realistic as possible ... like taken images from the real world. Try to make it look like the real thing. For example, when we talk about ChatGPT, try to show screens from ChatGPT with openai logos etc. When Poe is being talked about ... let's show Poe.com logo ... same way anthropic logo etc. so that the viewer can identify with what they know about with what is being said in the audio.\n\n"
            "VISUAL STYLE BIBLE (apply this visual style consistently to your prompt — do NOT copy it verbatim into your output):\n"
            "{style_bible}"
        )),
        ("user", "Text Chunk: \"{text_chunk}\"")
    ])
    chain = prompt_template | llm | StrOutputParser()

    all_prompts = []
    print(f"-> Generating {len(text_chunks)} prompts...")
    for i, chunk in enumerate(text_chunks):
        print(f"   - Processing chunk {i+1}/{len(text_chunks)}...")
        prompt = chain.invoke({"text_chunk": chunk, "style_bible": style_bible})
        all_prompts.append(f"{i+1}. {prompt.strip()}")

    # 5. Write the final list of prompts to the output file
    output_string = "\n".join(all_prompts)
    output_dir = os.path.dirname(prompts_path)
    os.makedirs(output_dir, exist_ok=True)
    Path(prompts_path).write_text(output_string, encoding="utf-8")

    print(f"✅ Image prompts generation complete. Saved to: {prompts_path}")
    return prompts_path
