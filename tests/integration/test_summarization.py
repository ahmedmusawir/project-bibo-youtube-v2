import os
import pytest

from src.summarization import summarize_transcript

# --- Test Setup ---
# The dedicated directory for our "golden file" integration test run
INTEGRATION_PROJECT_PATH = os.path.abspath("projects/integration_test_run")
INPUT_TRANSCRIPT_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "0_transcript.txt")
OUTPUT_SUMMARY_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "1_summary.txt")

# We depend on the transcription integration test having run first.
@pytest.mark.dependency(depends=["tests/integration/test_transcription.py::test_transcribe_youtube_audio_integration"])
@pytest.mark.integration
def test_summarize_transcript_integration():
    """
    An integration test that performs a real summarization.
    It reads the transcript from the integration directory, calls the live Anthropic API,
    and saves the output back to the same directory.
    """
    print(f"\nRunning integration test: Summarizing {INPUT_TRANSCRIPT_PATH}")
    print(f"Output will be saved to: {OUTPUT_SUMMARY_PATH}")

    # Pre-condition check: Ensure the input transcript exists
    assert os.path.exists(INPUT_TRANSCRIPT_PATH), \
        f"Input transcript not found. Run the transcription integration test first."
    assert os.path.getsize(INPUT_TRANSCRIPT_PATH) > 0

    # Execution: Call the function with the real input and output paths
    result_path = summarize_transcript(INPUT_TRANSCRIPT_PATH, OUTPUT_SUMMARY_PATH)

    # Verification
    # Check that the function returns the correct path
    assert result_path == OUTPUT_SUMMARY_PATH
    
    # Check that the summary file was created and is not empty
    assert os.path.exists(OUTPUT_SUMMARY_PATH)
    assert os.path.getsize(OUTPUT_SUMMARY_PATH) > 0

    print(f"\n✅ Integration test for summarization successful.")
