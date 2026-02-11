import os
import re
import json
from pathlib import Path
from dotenv import load_dotenv

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

# Load environment variables
load_dotenv()

# A global flag to ensure Vertex AI is initialized only once
_vertex_ai_initialized = False

def _initialize_vertex_ai():
    """Initializes the Vertex AI SDK if not already done."""
    global _vertex_ai_initialized
    if not _vertex_ai_initialized:
        try:
            PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
            REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
            vertexai.init(project=PROJECT_ID, location=REGION)
            print(f"✅ Vertex AI initialized for project: {PROJECT_ID}")
            _vertex_ai_initialized = True
        except Exception as e:
            print(f"❌ Error initializing Vertex AI: {e}")
            raise

def create_images_from_prompts(prompts_path: str, output_dir: str) -> str:
    """
    Generates images from a file of prompts using Vertex AI and saves them to a directory.

    Args:
        prompts_path (str): The absolute path to the text file containing numbered prompts.
        output_dir (str): The absolute path to the directory to save the generated images.

    Returns:
        str: The path to the directory containing the saved images.
    """
    _initialize_vertex_ai()

    print(f"-> Loading prompts from: {prompts_path}")
    prompts_text = Path(prompts_path).read_text(encoding="utf-8")
    # Use regex to find lines starting with a number and a period
    numbered_prompts = [line for line in prompts_text.strip().splitlines() if re.match(r"^\d+\.", line.strip())]
    print(f"-> Found {len(numbered_prompts)} prompts to process.")

    # Create the output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print("-> Loading Imagen model...")
    # generation_model = ImageGenerationModel.from_pretrained("imagen-4.0-fast-generate-001")
    # generation_model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-001")
    generation_model = ImageGenerationModel.from_pretrained("imagen-4.0-ultra-generate-001")
    print("✅ Model loaded successfully.")

    log_data = []
    for i, prompt in enumerate(numbered_prompts):
        try:
            prompt_text = prompt.split(".", 1)[-1].strip()
            print(f"\n🎨 Generating image {i+1:03} → {prompt_text[:80]}...")

            response = generation_model.generate_images(
                prompt=prompt_text,
                number_of_images=1,
                aspect_ratio="16:9",
                add_watermark=False
            )

            image = response.images[0]
            filename = f"{i+1:03}.png"
            filepath = os.path.join(output_dir, filename)
            image.save(location=filepath)

            log_data.append({"index": i+1, "prompt": prompt_text, "filepath": filepath})
            print(f"✅ Saved: {filepath}")

        except Exception as e:
            print(f"❌ Error generating image {i+1:03}: {e}")

    # Save a log file in the same directory
    log_path = os.path.join(output_dir, "_image_log.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)
    print(f"\n📝 Image generation log saved: {log_path}")

    print("🎉 All image generation tasks complete.")
    return output_dir
