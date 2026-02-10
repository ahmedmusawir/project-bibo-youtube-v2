import os
import pytest
from unittest.mock import patch, MagicMock

from src.transcription import transcribe_youtube_audio

# Define a dummy URL for testing
TEST_YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

@patch('src.transcription._get_speech_client')
@patch('src.transcription._convert_to_flac')
@patch('src.transcription._download_audio_to_temp')
def test_transcribe_youtube_audio_unit(
    mock_downloader,
    mock_convert_flac,
    mock_get_client,
    tmp_path
):
    """
    Unit test for transcribe_youtube_audio.
    Mocks the downloader, FLAC converter, and Google Speech client.
    """
    # 1. Setup Mocks and Temporary Files
    test_output_path = tmp_path / "transcript.txt"
    dummy_audio_path = tmp_path / "dummy_audio.mp3"
    dummy_flac_path = tmp_path / "dummy_audio.flac"

    # Create dummy files
    with open(dummy_audio_path, "w") as f:
        f.write("dummy audio")
    with open(dummy_flac_path, "w") as f:
        f.write("dummy flac")
    
    mock_downloader.return_value = str(dummy_audio_path)
    mock_convert_flac.return_value = str(dummy_flac_path)

    # Mock the Google Speech client
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    # Mock the long_running_recognize operation
    mock_operation = MagicMock()
    mock_client.long_running_recognize.return_value = mock_operation
    
    # Mock the response with transcript results
    mock_result = MagicMock()
    mock_alternative = MagicMock()
    mock_alternative.transcript = "This is a mocked transcript."
    mock_result.alternatives = [mock_alternative]
    
    mock_response = MagicMock()
    mock_response.results = [mock_result]
    mock_operation.result.return_value = mock_response

    # 2. Execution
    result_path = transcribe_youtube_audio(TEST_YOUTUBE_URL, str(test_output_path))

    # 3. Verification
    mock_downloader.assert_called_once_with(TEST_YOUTUBE_URL)
    mock_convert_flac.assert_called_once_with(str(dummy_audio_path))
    mock_client.long_running_recognize.assert_called_once()

    assert result_path == str(test_output_path)
    assert os.path.exists(test_output_path)
    assert os.path.isfile(test_output_path), "Output path must be a file, not a directory"
    with open(test_output_path, "r") as f:
        content = f.read()
    assert content == "This is a mocked transcript."


@patch('src.transcription._get_speech_client')
@patch('src.transcription._convert_to_flac')
@patch('src.transcription._download_audio_to_temp')
def test_transcribe_rejects_directory_path(mock_downloader, mock_convert_flac, mock_get_client, tmp_path):
    """
    Regression test: transcribe_youtube_audio must receive a file path, not a directory.
    If given a directory, it should fail (IsADirectoryError).
    """
    dummy_audio_path = tmp_path / "dummy_audio.mp3"
    dummy_flac_path = tmp_path / "dummy_audio.flac"
    
    with open(dummy_audio_path, "w") as f:
        f.write("dummy audio")
    with open(dummy_flac_path, "w") as f:
        f.write("dummy flac")
        
    mock_downloader.return_value = str(dummy_audio_path)
    mock_convert_flac.return_value = str(dummy_flac_path)
    
    # Mock client
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_operation = MagicMock()
    mock_client.long_running_recognize.return_value = mock_operation
    mock_response = MagicMock()
    mock_response.results = []
    mock_operation.result.return_value = mock_response

    # Passing a directory instead of a file path should raise IsADirectoryError
    with pytest.raises(IsADirectoryError):
        transcribe_youtube_audio(TEST_YOUTUBE_URL, str(tmp_path))


@patch('src.transcription._get_speech_client')
@patch('src.transcription._convert_to_flac')
@patch('src.transcription._download_audio_to_temp')
def test_transcribe_multiple_results(mock_downloader, mock_convert_flac, mock_get_client, tmp_path):
    """
    Test that multiple speech results are combined correctly.
    """
    test_output_path = tmp_path / "transcript.txt"
    dummy_audio_path = tmp_path / "dummy_audio.mp3"
    dummy_flac_path = tmp_path / "dummy_audio.flac"

    # Create dummy files
    with open(dummy_audio_path, "w") as f:
        f.write("dummy audio")
    with open(dummy_flac_path, "w") as f:
        f.write("dummy flac")

    mock_downloader.return_value = str(dummy_audio_path)
    mock_convert_flac.return_value = str(dummy_flac_path)
    
    # Mock client with multiple results
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_operation = MagicMock()
    mock_client.long_running_recognize.return_value = mock_operation
    
    # Create two results with different transcript parts
    mock_result1 = MagicMock()
    mock_alt1 = MagicMock()
    mock_alt1.transcript = "Part one."
    mock_result1.alternatives = [mock_alt1]
    
    mock_result2 = MagicMock()
    mock_alt2 = MagicMock()
    mock_alt2.transcript = "Part two."
    mock_result2.alternatives = [mock_alt2]
    
    mock_response = MagicMock()
    mock_response.results = [mock_result1, mock_result2]
    mock_operation.result.return_value = mock_response

    result_path = transcribe_youtube_audio(TEST_YOUTUBE_URL, str(test_output_path))

    assert mock_client.long_running_recognize.call_count == 1
    with open(test_output_path, "r") as f:
        content = f.read()
    assert content == "Part one. Part two."
