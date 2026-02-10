import os
import pytest
from unittest.mock import patch, MagicMock

from src.summarization import summarize_transcript

@patch('src.summarization.create_stuff_documents_chain')
@patch('src.summarization.TextLoader')
@patch('src.summarization.ChatAnthropic') # Patch the class to mock the instance
def test_summarize_transcript_unit(
    mock_chat_anthropic,
    mock_text_loader,
    mock_create_chain,
    tmp_path # Use pytest's built-in temporary directory fixture
):
    """
    Unit test for summarize_transcript.
    Mocks the entire LangChain chain to test the function's orchestration.
    """
    # 1. Setup
    # Define temporary file paths using the tmp_path fixture
    temp_transcript_path = tmp_path / "transcript.txt"
    temp_summary_path = tmp_path / "summary.txt"

    # Create a dummy transcript file
    temp_transcript_path.write_text("This is a test transcript.")

    # Mock the loader to return dummy documents
    mock_text_loader.return_value.load.return_value = [MagicMock(page_content="dummy content")]

    # Mock the chain and its invocation to return a specific result
    mock_chain_instance = MagicMock()
    mock_chain_instance.invoke.return_value = "This is the mocked summary."
    mock_create_chain.return_value = mock_chain_instance

    # 2. Execution
    result_path = summarize_transcript(str(temp_transcript_path), str(temp_summary_path))

    # 3. Verification
    # Verify that the loader was called with the correct transcript path
    mock_text_loader.assert_called_once_with(str(temp_transcript_path))

    # Verify that the chain was created and invoked
    mock_create_chain.assert_called_once()
    mock_chain_instance.invoke.assert_called_once()

    # Verify the function returned the correct path
    assert result_path == str(temp_summary_path)

    # Verify the summary file was created with the mocked content
    assert os.path.exists(temp_summary_path)
    with open(temp_summary_path, "r") as f:
        content = f.read()
    assert content == "This is the mocked summary."
