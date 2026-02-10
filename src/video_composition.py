from moviepy import ImageClip, concatenate_videoclips, AudioFileClip, vfx
from PIL import Image, ImageOps
from PIL.Image import Resampling
import numpy as np
import os

def compose_video(images_dir: str, audio_path: str, output_path: str, video_size=(1920, 1080), fade_duration=1.5, fps=24):
    """
    Composes a video from a directory of images and an audio file using moviepy 2.x syntax.

    Args:
        images_dir (str): Path to the directory containing the source images.
        audio_path (str): Path to the audio file for the narration.
        output_path (str): Path to save the final rendered video.
        video_size (tuple): The (width, height) of the output video.
        fade_duration (float): The duration of the fade in/out effect in seconds.
        fps (int): The frames per second of the output video.
    """
    print(f"\n-> Starting video composition...")
    print(f"   - Images from: {images_dir}")
    print(f"   - Audio from: {audio_path}")

    image_clips = []
    width, height = video_size

    image_files = sorted([f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
    if not image_files:
        raise ValueError("No valid images found in the specified directory.")

    print(f"-> Found {len(image_files)} images to process.")
    for filename in image_files:
        filepath = os.path.join(images_dir, filename)
        try:
            img = Image.open(filepath).convert("RGB")
            img = ImageOps.exif_transpose(img)
            img = img.resize((width, height), resample=Resampling.LANCZOS)
            img_array = np.array(img)
            clip = ImageClip(img_array)
            image_clips.append(clip)
        except Exception as e:
            print(f"Skipping {filename} due to error: {e}")

    if not image_clips:
        raise RuntimeError("Could not create any valid image clips.")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at: {audio_path}")

    audio = AudioFileClip(audio_path)
    duration_per_image = audio.duration / len(image_clips)
    print(f"-> Auto-calculated duration per image: {duration_per_image:.2f} seconds")

    processed_clips = []
    for clip in image_clips:
        clip = clip.with_duration(duration_per_image)
        clip = clip.with_position(('center', 'center'))
        clip = clip.with_effects([
            vfx.Resize(lambda t: 1 + 0.05 * t),
            vfx.FadeIn(fade_duration),
            vfx.FadeOut(fade_duration),
        ])
        processed_clips.append(clip)

    video = concatenate_videoclips(processed_clips, method="compose")
    video = video.with_audio(audio)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"-> Rendering final video to: {output_path} (this may take a while)...")
    video.write_videofile(output_path, fps=fps)

    print(f"\n✅ Video rendering complete! Check: {output_path}")
    return output_path

if __name__ == "__main__":
    # This block allows you to run the script directly for a manual test
    # It uses the assets from our "golden" integration test run
    images_dir = "projects/integration_test_run/5_images"
    audio_path = "projects/integration_test_run/2_audio.mp3"
    output_path = "projects/integration_test_run/6_final_video.mp4"
    
    compose_video(images_dir, audio_path, output_path)
