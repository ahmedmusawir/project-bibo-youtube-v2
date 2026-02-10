import os
import pytest
from unittest.mock import patch, MagicMock

from src.image_creation import create_images_from_prompts

# A sample prompt file content
PROMPTS_CONTENT = """
1. A futuristic cityscape at dawn.
2. A robot reading a book in a library.
3. A spaceship landing in a forest.
"""

@patch('src.image_creation.vertexai')
@patch('src.image_creation.ImageGenerationModel')
def test_create_images_from_prompts_unit(mock_image_model, mock_vertexai, tmp_path):
    """
    Unit test for create_images_from_prompts.
    Mocks the Vertex AI client and ImageGenerationModel.
    """
    # 1. Setup
    temp_prompts_path = tmp_path / "prompts.txt"
    temp_output_dir = tmp_path / "images"
    temp_prompts_path.write_text(PROMPTS_CONTENT)

    # Mock the model and its response
    mock_model_instance = mock_image_model.from_pretrained.return_value
    mock_image = MagicMock()
    mock_model_instance.generate_images.return_value.images = [mock_image]

    # Ensure the mock for vertexai.init() will be called
    mock_vertexai.global_config.project = None

    # 2. Execution
    result_dir = create_images_from_prompts(str(temp_prompts_path), str(temp_output_dir))

    # 3. Verification
    # Verify Vertex AI was initialized
    mock_vertexai.init.assert_called_once()

    # Verify the model was loaded
    mock_image_model.from_pretrained.assert_called_once_with("imagen-4.0-generate-preview-06-06")

    # Verify that generate_images was called 3 times (for 3 prompts)
    assert mock_model_instance.generate_images.call_count == 3

    # Verify that the save method was called 3 times
    assert mock_image.save.call_count == 3

    # Check that the output directory was created and returned
    assert os.path.isdir(result_dir)
    assert result_dir == str(temp_output_dir)

    # Check that a log file was created
    assert os.path.exists(os.path.join(result_dir, "_image_log.json"))
