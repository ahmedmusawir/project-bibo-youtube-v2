import os
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from src.utils.config import get_prompting_llm, get_image_gen_model

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

def generate_thumbnail_text(metadata: dict) -> str:
    """
    Generates a catchy one-liner for thumbnail text overlay using LLM.
    
    Args:
        metadata (dict): Metadata dict with titles, description, hashtags
        
    Returns:
        str: A short, punchy one-liner (3-7 words) for the thumbnail
    """
    print("-> Generating thumbnail text overlay...")
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model=get_prompting_llm(),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.9,  # Higher temp for creative text
    )
    
    # Build context from metadata
    titles = metadata.get("titles", [])
    description = metadata.get("description", "")
    
    context = f"Video Titles:\n" + "\n".join(f"- {t}" for t in titles[:3])
    context += f"\n\nDescription:\n{description[:300]}"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a YouTube thumbnail text expert. Create a SHORT, PUNCHY text overlay for a YouTube thumbnail.\n\n"
            "Requirements:\n"
            "- 3-7 words MAXIMUM\n"
            "- ALL CAPS for impact\n"
            "- Must be attention-grabbing and click-worthy\n"
            "- Should capture the core hook or benefit\n"
            "- Use power words like: REVEALED, SECRET, ULTIMATE, SHOCKING, etc.\n"
            "- Avoid generic phrases\n\n"
            "Examples of GOOD thumbnail text:\n"
            "- AI JUST CHANGED EVERYTHING\n"
            "- THE SECRET THEY DON'T TELL YOU\n"
            "- THIS WILL BLOW YOUR MIND\n"
            "- REVEALED: THE ULTIMATE HACK\n\n"
            "Output ONLY the text overlay, nothing else."
        )),
        ("user", "{context}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    thumbnail_text = chain.invoke({"context": context})
    
    # Clean up the output
    thumbnail_text = thumbnail_text.strip().strip('"').strip("'")
    
    print(f"✅ Generated thumbnail text: {thumbnail_text}")
    return thumbnail_text

def generate_thumbnail_prompt(metadata: dict, thumbnail_text: str) -> str:
    """
    Generates a detailed image prompt for thumbnail creation using LLM.
    
    Args:
        metadata (dict): Metadata dict with titles, description, hashtags
        thumbnail_text (str): The text overlay to be embedded in the thumbnail
        
    Returns:
        str: A detailed image generation prompt with text embedding instruction
    """
    print("-> Generating thumbnail image prompt...")
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model=get_prompting_llm(),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.8,
    )
    
    # Build context from metadata
    titles = metadata.get("titles", [])
    description = metadata.get("description", "")
    
    context = f"Video Titles:\n" + "\n".join(f"- {t}" for t in titles[:3])
    context += f"\n\nDescription:\n{description[:400]}"
    context += f"\n\nText to embed on thumbnail: {thumbnail_text}"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a YouTube thumbnail design expert. Create a DETAILED image generation prompt for a YouTube thumbnail.\n\n"
            "The thumbnail must be:\n"
            "- Eye-catching and professional\n"
            "- High contrast with bold colors\n"
            "- Photorealistic or cinematic style\n"
            "- 16:9 aspect ratio optimized\n"
            "- Designed to stand out in YouTube search results\n\n"
            "CRITICAL REQUIREMENT: The user will provide text that MUST be embedded directly on the image.\n"
            "You MUST include an instruction in your prompt to render this text on the image.\n\n"
            "Text embedding guidelines:\n"
            "- Specify the EXACT text to be rendered (use the text provided by the user)\n"
            "- Specify text placement (top, bottom, center, left, right)\n"
            "- Specify text style: bold, large, high-contrast, readable font\n"
            "- Specify text color that contrasts with background (white with black outline, or black with white outline)\n"
            "- Text should be prominent and eye-catching\n\n"
            "Include in your prompt:\n"
            "- Main visual subject (person, object, scene) that complements the text\n"
            "- Color scheme (vibrant, high contrast)\n"
            "- Lighting (dramatic, professional)\n"
            "- Composition that works with the text placement\n"
            "- TEXT INSTRUCTION: 'Bold text at [position] that says \"[exact text]\" in large white letters with black outline'\n"
            "- Style keywords: [photorealistic], [cinematic], [professional], [high-resolution], [text overlay]\n\n"
            "Keep prompt under 250 words. Be specific and visual.\n"
            "Output ONLY the image prompt, nothing else."
        )),
        ("user", "{context}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    image_prompt = chain.invoke({"context": context})
    
    print(f"✅ Generated image prompt ({len(image_prompt)} chars)")
    return image_prompt.strip()

def create_thumbnail(metadata_path: str, output_path: str) -> dict:
    """
    Generates a YouTube thumbnail from metadata.
    
    Args:
        metadata_path (str): Path to the metadata JSON file
        output_path (str): Path to save the thumbnail PNG
        
    Returns:
        dict: Contains thumbnail_path, thumbnail_text, and image_prompt
    """
    print(f"-> Loading metadata from: {metadata_path}")
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Step 1: Generate thumbnail text overlay
    thumbnail_text = generate_thumbnail_text(metadata)
    
    # Step 2: Generate detailed image prompt
    image_prompt = generate_thumbnail_prompt(metadata, thumbnail_text)
    
    # Step 3: Generate thumbnail image with Vertex AI
    _initialize_vertex_ai()
    
    model_name = get_image_gen_model()
    print(f"-> Loading Imagen model: {model_name}...")
    generation_model = ImageGenerationModel.from_pretrained(model_name)
    
    print(f"-> Generating thumbnail image...")
    print(f"   Prompt: {image_prompt[:100]}...")
    
    response = generation_model.generate_images(
        prompt=image_prompt,
        number_of_images=1,
        aspect_ratio="16:9",
        add_watermark=False
    )
    
    image = response.images[0]
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the thumbnail
    image.save(location=output_path)
    print(f"✅ Thumbnail saved: {output_path}")
    
    # Return metadata about the generation
    result = {
        "thumbnail_path": output_path,
        "thumbnail_text": thumbnail_text,
        "image_prompt": image_prompt
    }
    
    # Save generation metadata alongside the thumbnail
    metadata_output = output_path.replace(".png", "_metadata.json")
    with open(metadata_output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Thumbnail metadata saved: {metadata_output}")
    print("🎉 Thumbnail generation complete!")
    
    return result
