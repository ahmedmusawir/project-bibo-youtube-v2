import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Mock the problematic imports BEFORE importing our module
sys.modules['moviepy'] = MagicMock()
sys.modules['moviepy.editor'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageOps'] = MagicMock()

# Now we can safely import our module
from src.video_composition import compose_video

class TestVideoComposition:
    @patch('src.video_composition.Image')
    @patch('src.video_composition.ImageOps')
    @patch('src.video_composition.AudioFileClip')
    @patch('src.video_composition.ImageClip')
    @patch('src.video_composition.concatenate_videoclips')
    def test_compose_video_from_assets_unit(
        self,
        mock_concatenate,
        mock_image_clip,
        mock_audio_clip,
        mock_image_ops,
        mock_image,
        tmp_path
    ):
        """
        Unit test for compose_video_from_assets.
        Mocks all external dependencies properly.
        """
        # 1. Setup test data
        temp_images_dir = tmp_path / "images"
        temp_images_dir.mkdir()
        
        # Create 3 fake image files
        for i in range(3):
            (temp_images_dir / f"image_{i}.png").touch()
        
        temp_audio_path = tmp_path / "audio.mp3"
        temp_audio_path.touch()
        temp_output_path = tmp_path / "video.mp4"

        # 2. Configure mocks
        # Mock PIL Image operations
        mock_img = MagicMock()
        mock_img.convert.return_value = mock_img
        mock_img.resize.return_value = mock_img
        mock_image.open.return_value = mock_img
        mock_image_ops.exif_transpose.return_value = mock_img
        
        # Mock ImageClip creation
        mock_clip = MagicMock()
        mock_clip.set_duration.return_value = mock_clip
        mock_clip.resize.return_value = mock_clip
        mock_clip.set_position.return_value = mock_clip
        mock_clip.fadein.return_value = mock_clip
        mock_clip.fadeout.return_value = mock_clip
        mock_image_clip.return_value = mock_clip

        # Mock audio clip with duration
        mock_audio = MagicMock()
        mock_audio.duration = 30.0  # 30 seconds
        mock_audio_clip.return_value = mock_audio

        # Mock final video concatenation
        mock_final_video = MagicMock()
        mock_final_video.with_audio.return_value = mock_final_video
        mock_concatenate.return_value = mock_final_video

        # 3. Execute the function
        result_path = compose_video(
            str(temp_images_dir), 
            str(temp_audio_path), 
            str(temp_output_path)
        )

        # 4. Verify behavior
        # Check that 3 images were processed
        assert mock_image.open.call_count == 3
        assert mock_image_clip.call_count == 3
        
        # Check audio was loaded
        mock_audio_clip.assert_called_once_with(str(temp_audio_path))
        
        # Check clips were concatenated
        mock_concatenate.assert_called_once()
        
        # Check audio was set on final video (MoviePy 2.x uses with_audio)
        mock_final_video.with_audio.assert_called_once_with(mock_audio)
        
        # Check video was written with correct parameters
        mock_final_video.write_videofile.assert_called_once_with(str(temp_output_path), fps=24)
        
        # Check return value
        assert result_path == str(temp_output_path)

    def test_compose_video_no_images_error(self, tmp_path):
        """Test that function raises error when no images found."""
        # Create empty images directory
        temp_images_dir = tmp_path / "images"
        temp_images_dir.mkdir()
        
        temp_audio_path = tmp_path / "audio.mp3"
        temp_audio_path.touch()
        temp_output_path = tmp_path / "video.mp4"

        with pytest.raises(ValueError, match="No valid images found"):
            compose_video(
                str(temp_images_dir), 
                str(temp_audio_path), 
                str(temp_output_path)
            )