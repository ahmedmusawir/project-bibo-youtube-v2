import os
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage

from src.image_prompting import _calculate_num_images, _split_summary_into_chunks, _generate_style_bible, generate_image_prompts

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

# --- Tests for _generate_style_bible ---

@patch('src.image_prompting.ChatGoogleGenerativeAI')
def test_generate_style_bible(mock_llm_class):
    """Tests that _generate_style_bible calls the LLM and returns stripped output."""
    # Mock the LLM instance that gets created inside the function
    mock_llm_instance = MagicMock()
    mock_llm_class.return_value = mock_llm_instance

    # When llm is used in a chain, it's called as a callable.
    # The chain calls mock_llm_instance(input) and passes the result to StrOutputParser.
    # StrOutputParser expects an AIMessage, so we return one.
    style_text = "Cool blue-toned lighting with warm amber accents. Documentary photography style — shallow depth of field, natural lighting. No text overlays, no watermarks, no logos rendered in the image."
    mock_llm_instance.return_value = AIMessage(content=f"  {style_text}  ")

    result = _generate_style_bible("This is a test script about AI technology.")

    assert "Cool blue-toned lighting" in result
    assert "No text overlays" in result
    # Verify leading/trailing whitespace is stripped
    assert not result.startswith(" ")
    assert not result.endswith(" ")

# --- Tests for generate_image_prompts with style bible ---

@patch('src.image_prompting.ChatGoogleGenerativeAI')
@patch('src.image_prompting.AudioSegment')
def test_generate_image_prompts_creates_style_bible(mock_audio_segment, mock_llm_class, tmp_path):
    """Tests that generate_image_prompts generates and saves a style bible."""
    # Setup mock audio (60 seconds = 3 images at 20s/image)
    mock_audio = mock_audio_segment.from_mp3.return_value
    mock_audio.__len__.return_value = 60 * 1000

    # Mock LLM instances - function creates 2 instances (style bible + scene prompts)
    # We need to mock the return value for each call
    mock_llm_instance = MagicMock()
    mock_llm_class.return_value = mock_llm_instance

    # Mock LLM calls: first call = style bible, next 3 = scene prompts
    mock_llm_instance.side_effect = [
        AIMessage(content="Cool blue documentary style. Shallow depth of field. No text overlays, no watermarks, no logos rendered in the image."),
        AIMessage(content="A photorealistic wide shot of a modern office"),
        AIMessage(content="A photorealistic close-up of a computer screen"),
        AIMessage(content="A photorealistic aerial view of a city skyline"),
    ]

    # Create input files
    summary_path = tmp_path / "1_summary.txt"
    summary_path.write_text("word " * 30)  # 30 words, will be split into 3 chunks
    audio_path = tmp_path / "2_audio.mp3"
    audio_path.write_text("fake audio")
    prompts_path = tmp_path / "3_image_prompts.json"
    style_bible_path = tmp_path / "3a_style_bible.txt"

    result = generate_image_prompts(str(summary_path), str(audio_path), str(prompts_path))

    # Style bible file should be created
    assert style_bible_path.exists()
    style_bible_content = style_bible_path.read_text()
    assert "Cool blue" in style_bible_content

    # Prompts file should be created with numbered lines
    assert prompts_path.exists()
    prompts_content = prompts_path.read_text()
    lines = prompts_content.strip().split("\n")
    assert len(lines) == 3
    assert lines[0].startswith("1.")
    assert lines[1].startswith("2.")
    assert lines[2].startswith("3.")

@patch('src.image_prompting.ChatGoogleGenerativeAI')
@patch('src.image_prompting.AudioSegment')
def test_generate_image_prompts_loads_existing_style_bible(mock_audio_segment, mock_llm_class, tmp_path):
    """Tests that generate_image_prompts loads an existing style bible instead of regenerating."""
    # Setup mock audio (40 seconds = 2 images at 20s/image)
    mock_audio = mock_audio_segment.from_mp3.return_value
    mock_audio.__len__.return_value = 40 * 1000

    # Mock LLM instance — should only be called for scene prompts (style bible loaded from file)
    mock_llm_instance = MagicMock()
    mock_llm_class.return_value = mock_llm_instance

    mock_llm_instance.side_effect = [
        AIMessage(content="A photorealistic wide shot of a modern office"),
        AIMessage(content="A photorealistic close-up of a computer screen"),
    ]

    # Create input files
    summary_path = tmp_path / "1_summary.txt"
    summary_path.write_text("word " * 20)
    audio_path = tmp_path / "2_audio.mp3"
    audio_path.write_text("fake audio")
    prompts_path = tmp_path / "3_image_prompts.json"

    # Pre-create the style bible file
    style_bible_path = tmp_path / "3a_style_bible.txt"
    style_bible_path.write_text("Existing style bible content for reuse.")

    result = generate_image_prompts(str(summary_path), str(audio_path), str(prompts_path))

    # Style bible should still contain the pre-existing content (not overwritten)
    assert style_bible_path.read_text() == "Existing style bible content for reuse."

    # Scene prompts should still be generated
    assert prompts_path.exists()
    prompts_content = prompts_path.read_text()
    lines = prompts_content.strip().split("\n")
    assert len(lines) == 2

    # LLM instance was called exactly 2 times (scene prompts only, no style bible generation)
    assert mock_llm_instance.call_count == 2
