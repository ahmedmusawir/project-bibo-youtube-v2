import os
import shutil
from src.transcription import transcribe_youtube_audio

# A reliable, short YouTube video for testing
LIVE_TEST_URL = "https://youtu.be/VuV-LZUkRJs"
# LIVE_TEST_URL = "https://www.youtube.com/watch?v=VuV-LZUkRJs"
LIVE_PROJECT_NAME = "live_test"
LIVE_PROJECT_PATH = os.path.join("projects", LIVE_PROJECT_NAME)

def run_live_transcription_test():
    """
    Performs a real download and transcription to verify the live service.
    """
    print("--- Starting Live Transcription Test ---")

    # Setup: Create a clean directory for the test
    if os.path.exists(LIVE_PROJECT_PATH):
        shutil.rmtree(LIVE_PROJECT_PATH)
    os.makedirs(LIVE_PROJECT_PATH)

    try:
        # Execution: Call the actual function
        transcribe_youtube_audio(LIVE_TEST_URL, LIVE_PROJECT_PATH)
        print("\n--- ✅ Live Test Successful ---")
    except Exception as e:
        # Catch and print any errors from the live call
        print(f"\n--- ❌ Live Test Failed ---")
        print(f"An error occurred: {e}")
    finally:
        # Teardown: Clean up the test directory
        if os.path.exists(LIVE_PROJECT_PATH):
            shutil.rmtree(LIVE_PROJECT_PATH)
            print("--- Test cleanup complete. ---")

# This makes the script runnable from the command line
if __name__ == "__main__":
    run_live_transcription_test()
