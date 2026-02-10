import os
import pytest

from src.metadata_generation import generate_metadata

# --- Test Setup ---
# The dedicated directory for our "golden file" integration test run
INTEGRATION_PROJECT_PATH = os.path.abspath("projects/integration_test_run")
INPUT_SUMMARY_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "1_summary.txt")
OUTPUT_METADATA_PATH = os.path.join(INTEGRATION_PROJECT_PATH, "3_metadata.txt")

# We depend on the summarization integration test having run first.
@pytest.mark.dependency(depends=["tests/integration/test_summarization.py::test_summarize_transcript_integration"])
@pytest.mark.integration
def test_generate_metadata_integration():
    """
    An integration test that performs real metadata generation.
    It reads the summary from the integration directory, calls the live Anthropic API,
    and saves the consolidated output back to the same directory.
    """
    print(f"\nRunning integration test: Generating metadata for {INPUT_SUMMARY_PATH}")
    print(f"Output will be saved to: {OUTPUT_METADATA_PATH}")

    # Pre-condition check: Ensure the input summary exists
    assert os.path.exists(INPUT_SUMMARY_PATH), \
        f"Input summary not found. Run the summarization integration test first."
    assert os.path.getsize(INPUT_SUMMARY_PATH) > 0

    # Execution: Call the function with the real input and output paths
    result_path = generate_metadata(INPUT_SUMMARY_PATH, OUTPUT_METADATA_PATH)

    # Verification
    # Check that the function returns the correct path
    assert result_path == OUTPUT_METADATA_PATH
    
    # Check that the metadata file was created and is not empty
    assert os.path.exists(OUTPUT_METADATA_PATH)
    assert os.path.getsize(OUTPUT_METADATA_PATH) > 50 # Check for a reasonable amount of content

    # A simple check to see if it contains the separator, a key part of our format
    with open(result_path, "r") as f:
        content = f.read()
    assert "-------------------" in content

    print(f"\n✅ Integration test for metadata generation successful.")
