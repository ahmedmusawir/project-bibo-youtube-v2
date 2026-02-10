import os
import pytest
import math
import re
from pydub import AudioSegment

from src.image_prompting import generate_image_prompts

# --- Test Setup ---
INTEGRATION_PROJECT_PATH = os.path.abspath("projects/integration_test_run")
INPUT_SUMMARY_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "1_summary.txt")
INPUT_AUDIO_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "2_audio.mp3")
OUTPUT_PROMPTS_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "4_image_prompts.txt")
# This is the crucial setting you identified. Setting it back to 20s.
SECONDS_PER_IMAGE = 20

@pytest.mark.dependency(depends=["tests/integration/test_text_to_speech.py::test_synthesize_speech_integration"])
@pytest.mark.integration
def test_generate_image_prompts_integration():
    """
    An integration test that performs real image prompt generation.
    """
    print(f"\nRunning integration test: Generating image prompts for {INPUT_SUMMARY_PATH}")
    print(f"Output will be saved to: {OUTPUT_PROMPTS_PATH}")

    # Pre-condition checks
    assert os.path.exists(INPUT_SUMMARY_PATH), f"Input summary not found: {INPUT_SUMMARY_PATH}"
    assert os.path.exists(INPUT_AUDIO_PATH), f"Input audio not found: {INPUT_AUDIO_PATH}"

    # Execution
    result_path = generate_image_prompts(INPUT_SUMMARY_PATH, INPUT_AUDIO_PATH, OUTPUT_PROMPTS_PATH)

    # Verification
    assert result_path == OUTPUT_PROMPTS_PATH
    assert os.path.exists(OUTPUT_PROMPTS_PATH)
    assert os.path.getsize(OUTPUT_PROMPTS_PATH) > 0

    # Verify the number of prompts matches the audio length
    audio = AudioSegment.from_mp3(INPUT_AUDIO_PATH)
    expected_num_prompts = math.ceil((len(audio) / 1000) / SECONDS_PER_IMAGE)

    with open(result_path, "r") as f:
        # Correctly count lines that start with a number and a period
        prompts = [line for line in f.readlines() if re.match(r"^\d+\.", line.strip())]
    
    assert len(prompts) == expected_num_prompts
    assert prompts[0].strip().startswith("1.")

    print(f"\n✅ Integration test for image prompting successful. Generated {len(prompts)} prompts.")