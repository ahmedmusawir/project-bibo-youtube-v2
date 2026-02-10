# img_prompt_generator.py (Version 2.0 - With Sync-Chunking Logic)

from pathlib import Path
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import math

# === Load .env ===
load_dotenv()

# === Primary Configuration ===
# This is now the main control for your video's pacing.
# Change this one value to adjust how many images are generated for the video.
SECONDS_PER_IMAGE = 20 

# === Paths and Model Setup ===
SUMMARY_PATH = Path("text/summary.txt")
PROMPT_OUTPUT_PATH = Path("stark_vision_tools/scene_sequence/output/scene_prompts.txt")
AUDIO_FILE_PATH = "audio/output.mp3"
# llm = ChatOpenAI(model="o1") 
llm = ChatOpenAI(model="gpt-4.1", temperature=0.8) 

# === Prompt Template for Text Chunks ===
# This template is designed to create one specific prompt from one small piece of text.
prompt_template = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a visual scene director. Your job is to create a single, vivid visual prompt for an AI image generator. You must include these words (and more like them) in every prompt: [photorealistic] [high-resolution] [realistic lighting]\n Because, the Image model needs to know what to focus on while generating images\n"
        "The prompt should be a cinematic, highly-detailed description of the key idea in the following text chunk. Make sure the most important parts are visible to the audience because these images will be used for video creation\n"
        "Focus on one clear moment. Keep the prompt under 200 words.\n"
        "Output only the prompt itself — no extra text, no numbering, no explanations."
        "Focus on the information. For example: if it says Claude 4, Gemini 2.5, ChatGPT, Poe, Perplexity, Apple, OpenAI, Anthropic, Gork, Mistral, Ollama, Meta, or any other brand or industry terms etc. try to include those words into your prompt and make sure those are reflected on the images. This is why, since we are using auto generated images, those words will be used a the visual queues for our viewers while audio is playing. It's always better when the user sees the text written clearly while the words are being said. This anchors the viewer with the audio to the visuals. So this is very important that the images we create reflect what is being said ... if possible, let's push for making visuals as realistic as possible ... like taken images from the real world. Try to make it look like the real thing. For example, when we talk about ChatGPT, try to show screens from ChatGPT with openai logos etc. When Poe is being talked about ... let's show Poe.com logo ... same way anthropic logo etc. so that the viewer can identify with what they know about with what is being said in the audio."
    )),
    ("user", "Text Chunk: \"{text_chunk}\"")
])

# === Helper Function to Split Summary ===
def split_summary_into_chunks(summary: str, num_chunks: int) -> list[str]:
    """
    Splits the summary text into a specified number of roughly equal chunks based on word count.
    This is the core of the audio-visual sync logic.
    """
    words = summary.split()
    total_words = len(words)
    if total_words == 0:
        return []
        
    words_per_chunk = math.ceil(total_words / num_chunks)
    
    text_chunks = []
    for i in range(0, total_words, words_per_chunk):
        chunk = " ".join(words[i:i + words_per_chunk])
        text_chunks.append(chunk)
    return text_chunks

# === Function to Generate a Single Prompt ===
def generate_prompt_for_chunk(text_chunk: str) -> str:
    """Invokes the LLM chain to generate one prompt for one text chunk."""
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"text_chunk": text_chunk})


# === Main Execution Block ===
if __name__ == "__main__":
    try:
        # Import the function from your other script to calculate the needed image count
        from sequence_image_creator import calculate_num_images

        # 1. Calculate the total number of images needed based on the master setting
        print(f"⚙️ Master setting: {SECONDS_PER_IMAGE} seconds per image.")
        num_images = calculate_num_images(AUDIO_FILE_PATH, SECONDS_PER_IMAGE)

        # 2. Read and split the summary text into chunks
        summary_text = SUMMARY_PATH.read_text(encoding="utf-8").strip()
        print(f"🔪 Splitting summary into {num_images} chunks to match audio timing...")
        text_chunks = split_summary_into_chunks(summary_text, num_images)

        all_prompts = []
        print(f"📜 Generating {num_images} prompts, one for each text chunk (this may take a moment)...")

        # 3. Loop through each text chunk and generate a corresponding prompt
        for i, chunk in enumerate(text_chunks):
            print(f"  -> Processing chunk {i+1}/{len(text_chunks)}...")
            prompt = generate_prompt_for_chunk(chunk)
            # We add the numbering back in here for the final output file
            all_prompts.append(f"{i+1}. {prompt.strip()}")
        
        # 4. Write the final, numbered list of prompts to the output file
        output_string = "\n".join(all_prompts)
        PROMPT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        PROMPT_OUTPUT_PATH.write_text(output_string, encoding="utf-8")
        
        print("\n" + "="*50)
        print(f"✅ Success! scene_prompts.txt created with {num_images} perfectly synchronized prompts.")
        print("="*50)

    except FileNotFoundError as e:
        print(f"❌ ERROR: A required file was not found. Please check the path: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")