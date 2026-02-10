import pytest

from src.metadata_generation import parse_metadata_output

# A realistic, multi-line raw output from the LLM
MOCK_LLM_OUTPUT = """
TITLES:
- This is the first title.
- This is the second title.

DESCRIPTION:
This is the first line of the description.
This is the second line.

HASHTAGS:
#hashtag1 #hashtag2 #hashtag3
"""

# A second test case with slightly different formatting
MOCK_LLM_OUTPUT_2 = """
TITLES:
-Title A
- Title B

DESCRIPTION: A single line description.

HASHTAGS: #tagA #tagB
"""

def test_parse_metadata_output_standard():
    """Tests the parsing logic with a standard, well-formatted input."""
    parsed_data = parse_metadata_output(MOCK_LLM_OUTPUT)
    assert parsed_data["titles"] == ["This is the first title.", "This is the second title."]
    assert parsed_data["description"] == "This is the first line of the description.\nThis is the second line."
    assert parsed_data["hashtags"] == ["#hashtag1", "#hashtag2", "#hashtag3"]

def test_parse_metadata_output_variant():
    """Tests the parsing logic with slightly different formatting."""
    parsed_data = parse_metadata_output(MOCK_LLM_OUTPUT_2)
    assert parsed_data["titles"] == ["Title A", "Title B"]
    assert parsed_data["description"] == "A single line description."
    assert parsed_data["hashtags"] == ["#tagA", "#tagB"]

def test_parse_metadata_output_empty():
    """Tests the parsing logic with an empty input."""
    parsed_data = parse_metadata_output("")
    assert parsed_data["titles"] == []
    assert parsed_data["description"] == ""
    assert parsed_data["hashtags"] == []
