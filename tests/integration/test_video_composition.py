import os
import pytest
from moviepy import AudioFileClip  

from src.video_composition import compose_video

# --- Test Setup ---
INTEGRATION_PROJECT_PATH = os.path.abspath("projects/integration_test_run")
INPUT_IMAGES_DIR = os.path.join(INTEGRATION_PROJECT_PATH, "5_images")
INPUT_AUDIO_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "2_audio.mp3")
OUTPUT_VIDEO_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "6_final_video.mp4")

@pytest.mark.dependency(depends=["tests/integration/test_image_creation.py::test_create_images_from_prompts_integration"])
@pytest.mark.integration
def test_compose_video_integration(tmp_path):
    """Integration test that performs real video composition."""
    print(f"\nRunning integration test: Composing video from {INPUT_IMAGES_DIR}")
    print(f"Output will be saved to: {OUTPUT_VIDEO_PATH}")

    # Pre-condition checks
    assert os.path.isdir(INPUT_IMAGES_DIR), f"Input image directory not found: {INPUT_IMAGES_DIR}"
    assert os.path.exists(INPUT_AUDIO_PATH), f"Input audio not found: {INPUT_AUDIO_PATH}"
    image_files = [f for f in os.listdir(INPUT_IMAGES_DIR) if f.endswith('.png')]
    assert len(image_files) > 0, "No images found in the input directory."

    # --- Truncate Audio for a Quick Test ---
    temp_audio_path = tmp_path / "temp_audio_45s.mp3"
    original_audio = AudioFileClip(INPUT_AUDIO_PATH)  # <-- Now works with 2.x
    truncated_audio = original_audio.subclipped(0, 45)  # <-- Note: subclipped, not subclip in 2.x
    truncated_audio.write_audiofile(str(temp_audio_path))
    
    # Clean up
    original_audio.close()
    truncated_audio.close()

    # Execution: Call the function
    result_path = compose_video(INPUT_IMAGES_DIR, str(temp_audio_path), OUTPUT_VIDEO_PATH)

    # Verification
    assert result_path == OUTPUT_VIDEO_PATH
    assert os.path.exists(OUTPUT_VIDEO_PATH)
    assert os.path.getsize(OUTPUT_VIDEO_PATH) > 1000

    print(f"\n✅ Integration test successful. Video saved to {OUTPUT_VIDEO_PATH}")