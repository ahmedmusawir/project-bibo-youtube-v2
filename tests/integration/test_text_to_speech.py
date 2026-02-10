import os
import pytest

from src.text_to_speech import synthesize_speech

# --- Test Setup ---
# The dedicated directory for our "golden file" integration test run
INTEGRATION_PROJECT_PATH = os.path.abspath("projects/integration_test_run")
INPUT_SUMMARY_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "1_summary.txt")
OUTPUT_AUDIO_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "2_audio.mp3")

# We depend on the summarization integration test having run first.
@pytest.mark.dependency(depends=["tests/integration/test_summarization.py::test_summarize_transcript_integration"])
@pytest.mark.integration
def test_synthesize_speech_integration():
    """
    An integration test that performs real text-to-speech synthesis.
    It reads the summary from the integration directory, calls the live OpenAI TTS API,
    and saves the resulting audio file back to the same directory.
    """
    print(f"\nRunning integration test: Synthesizing speech for {INPUT_SUMMARY_PATH}")
    print(f"Output will be saved to: {OUTPUT_AUDIO_PATH}")

    # Pre-condition check: Ensure the input summary exists
    assert os.path.exists(INPUT_SUMMARY_PATH), \
        f"Input summary not found. Run the summarization integration test first."
    assert os.path.getsize(INPUT_SUMMARY_PATH) > 0

    # Execution: Call the function with the real input and output paths
    result_path = synthesize_speech(INPUT_SUMMARY_PATH, OUTPUT_AUDIO_PATH)

    # Verification
    # Check that the function returns the correct path
    assert result_path == OUTPUT_AUDIO_PATH
    
    # Check that the audio file was created and is not empty
    assert os.path.exists(OUTPUT_AUDIO_PATH)
    assert os.path.getsize(OUTPUT_AUDIO_PATH) > 1000 # Check that it's a real audio file

    print(f"\n✅ Integration test for text-to-speech successful.")
