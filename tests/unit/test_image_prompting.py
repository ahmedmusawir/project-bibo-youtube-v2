import pytest
from unittest.mock import patch

from src.image_prompting import _calculate_num_images, _split_summary_into_chunks

# --- Tests for _calculate_num_images ---

@patch('src.image_prompting.AudioSegment')
def test_calculate_num_images(mock_audio_segment):
    """Tests the image calculation logic with a mocked AudioSegment."""
    # Mock the return value of from_mp3
    mock_audio = mock_audio_segment.from_mp3.return_value
    
    # Test case 1: Exact multiple
    mock_audio.__len__.return_value = 60 * 1000 # 60 seconds
    assert _calculate_num_images("dummy_path.mp3", 15) == 4

    # Test case 2: Rounding up
    mock_audio.__len__.return_value = 61 * 1000 # 61 seconds
    assert _calculate_num_images("dummy_path.mp3", 15) == 5

    # Test case 3: Zero duration
    mock_audio.__len__.return_value = 0
    assert _calculate_num_images("dummy_path.mp3", 15) == 0

# --- Tests for _split_summary_into_chunks ---

def test_split_summary_into_chunks():
    """Tests the text splitting logic with various inputs."""
    # Test case 1: Even split
    summary_even = "one two three four five six seven eight"
    chunks_even = _split_summary_into_chunks(summary_even, 4)
    assert len(chunks_even) == 4
    assert chunks_even[0] == "one two"
    assert chunks_even[3] == "seven eight"

    # Test case 2: Uneven split
    summary_uneven = "one two three four five"
    chunks_uneven = _split_summary_into_chunks(summary_uneven, 3)
    assert len(chunks_uneven) == 3
    assert chunks_uneven[0] == "one two"
    assert chunks_uneven[1] == "three four"
    assert chunks_uneven[2] == "five"

    # Test case 3: Empty input
    summary_empty = ""
    chunks_empty = _split_summary_into_chunks(summary_empty, 5)
    assert len(chunks_empty) == 0
