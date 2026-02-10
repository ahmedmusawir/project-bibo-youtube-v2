import os
import math
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import StrOutputParser
from pydub import AudioSegment

# Load environment variables
load_dotenv()

# === Primary Configuration ===
# This is now the main control for your video's pacing.
# Change this one value to adjust how many images are generated for the video.
SECONDS_PER_IMAGE = 20

# Initialize the language model
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.8,
    max_output_tokens=1024,
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

def generate_image_prompts(summary_path: str, audio_path: str, prompts_path: str, seconds_per_image: int = 20) -> str:
    """
    Generates a synchronized list of image prompts based on a summary and an audio file.

    Args:
        summary_path (str): Path to the summary text file.
        audio_path (str): Path to the audio file for timing.
        prompts_path (str): Path to save the output prompts text file.

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

    # 3. Generate a prompt for each text chunk
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a visual scene director. Your job is to create a single, vivid visual prompt for an AI image generator. You must include these words (and more like them) in every prompt: [photorealistic] [high-resolution] [realistic lighting].\n"
            "The prompt should be a cinematic, highly-detailed description of the key idea in the following text chunk. Focus on one clear moment. Keep the prompt under 200 words.\n"
            "Output only the prompt itself — no extra text, no numbering, no explanations.\n"
            "Focus on the information. For example: if it says Claude 4, Gemini 2.5, ChatGPT, Poe, Perplexity, Apple, OpenAI, Anthropic, Gork, Mistral, Ollama, Meta, or any other brand or industry terms etc. try to include those words into your prompt and make sure those are reflected on the images. This is why, since we are using auto generated images, those words will be used a the visual queues for our viewers while audio is playing. It's always better when the user sees the text written clearly while the words are being said. This anchors the viewer with the audio to the visuals. So this is very important that the images we create reflect what is being said ... if possible, let's push for making visuals as realistic as possible ... like taken images from the real world. Try to make it look like the real thing. For example, when we talk about ChatGPT, try to show screens from ChatGPT with openai logos etc. When Poe is being talked about ... let's show Poe.com logo ... same way anthropic logo etc. so that the viewer can identify with what they know about with what is being said in the audio."
        )),
        ("user", "Text Chunk: \"{text_chunk}\"")
    ])
    chain = prompt_template | llm | StrOutputParser()

    all_prompts = []
    print(f"-> Generating {len(text_chunks)} prompts...")
    for i, chunk in enumerate(text_chunks):
        print(f"   - Processing chunk {i+1}/{len(text_chunks)}...")
        prompt = chain.invoke({"text_chunk": chunk})
        all_prompts.append(f"{i+1}. {prompt.strip()}")

    # 4. Write the final list of prompts to the output file
    output_string = "\n".join(all_prompts)
    output_dir = os.path.dirname(prompts_path)
    os.makedirs(output_dir, exist_ok=True)
    Path(prompts_path).write_text(output_string, encoding="utf-8")

    print(f"✅ Image prompts generation complete. Saved to: {prompts_path}")
    return prompts_path
