import os
import shutil
import pytest

from src.transcription import transcribe_youtube_audio

# --- Test Setup ---
# A short, public domain YouTube video for a reliable live test
TEST_YOUTUBE_URL = "https://www.youtube.com/watch?v=VuV-LZUkRJs"

# The dedicated directory for our "golden file" integration test run
INTEGRATION_PROJECT_PATH = os.path.abspath("projects/integration_test_run")
OUTPUT_TRANSCRIPT_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "0_transcript.txt")

@pytest.fixture(scope="module")
def setup_teardown_integration_dir():
    """Create the integration test directory before any tests run, and clean up after."""
    # Setup: Ensure the directory is clean before the test
    if os.path.exists(INTEGRATION_PROJECT_PATH):
        shutil.rmtree(INTEGRATION_PROJECT_PATH)
    os.makedirs(INTEGRATION_PROJECT_PATH)
    
    yield # This is where the tests will run
    
    # Teardown: We are keeping the files for inspection, so no cleanup is needed here.
    # print(f"\nIntegration test files saved in: {INTEGRATION_PROJECT_PATH}")

@pytest.mark.integration
def test_transcribe_youtube_audio_integration(setup_teardown_integration_dir):
    """
    An integration test that performs a real transcription.
    It downloads audio from YouTube and calls the live OpenAI Whisper API.
    The output is saved to the 'projects/integration_test_run' directory.
    """
    print(f"\nRunning integration test: Transcribing {TEST_YOUTUBE_URL}")
    print(f"Output will be saved to: {OUTPUT_TRANSCRIPT_PATH}")
    
    # Execution: Call the function with the live URL and target path
    result_path = transcribe_youtube_audio(TEST_YOUTUBE_URL, OUTPUT_TRANSCRIPT_PATH)

    # Verification
    # Check that the function returns the correct path
    assert result_path == OUTPUT_TRANSCRIPT_PATH
    
    # Check that the transcript file was created
    assert os.path.exists(OUTPUT_TRANSCRIPT_PATH)
    
    # Check that the file is not empty
    assert os.path.getsize(OUTPUT_TRANSCRIPT_PATH) > 0

    print(f"\n✅ Integration test for transcription successful.")
