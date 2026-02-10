import os
import pytest
import tempfile

from src.image_creation import create_images_from_prompts

# --- Test Setup ---
INTEGRATION_PROJECT_PATH = os.path.abspath("projects/integration_test_run")
OUTPUT_IMAGE_DIR = os.path.join(INTEGRATION_PROJECT_PATH, "5_images")

# A small, representative set of prompts for an efficient integration test
TEST_PROMPTS = """
1. A photorealistic, high-resolution image of a world map showing glowing data connections between continents, representing the global reach of AI.
2. A photorealistic, high-resolution image of a diverse team of engineers collaborating in a modern office, with code on screens and a whiteboard filled with diagrams.
3. A photorealistic, high-resolution image of a sleek, autonomous electric car driving through a futuristic city at night, with neon lights reflecting on its surface.
"""

@pytest.mark.dependency(depends=["tests/integration/test_image_prompting.py::test_generate_image_prompts_integration"])
@pytest.mark.integration
def test_create_images_from_prompts_integration():
    """
    An integration test that performs real image generation for a small set of prompts.
    """
    # Create a temporary file for our 3 test prompts
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as temp_prompt_file:
        temp_prompt_file.write(TEST_PROMPTS)
        temp_prompts_path = temp_prompt_file.name

    print(f"\nRunning integration test: Generating 3 images from {temp_prompts_path}")
    print(f"Output will be saved to: {OUTPUT_IMAGE_DIR}")

    try:
        # Execution: Call the function with the temporary prompts file
        result_dir = create_images_from_prompts(temp_prompts_path, OUTPUT_IMAGE_DIR)

        # Verification
        assert result_dir == OUTPUT_IMAGE_DIR
        assert os.path.isdir(OUTPUT_IMAGE_DIR)
        
        # Check that 3 images were created
        generated_files = os.listdir(OUTPUT_IMAGE_DIR)
        # Filter for image files and exclude the log file
        image_files = [f for f in generated_files if f.endswith(".png")]
        assert len(image_files) == 3

        # Check that the log file was also created
        assert "_image_log.json" in generated_files

        print(f"\n✅ Integration test for image creation successful. Generated {len(image_files)} images.")

    finally:
        # Clean up the temporary prompt file
        os.remove(temp_prompts_path)
