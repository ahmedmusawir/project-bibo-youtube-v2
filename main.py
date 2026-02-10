import os
from src import transcription
from src import summarization
from src import text_to_speech
from src import image_prompting
from src import metadata_generation
from src import image_creation
from src import video_composition
from src.logger import init_logging, stop_logging, get_log_path

# Pipeline stage definitions
PIPELINE_STAGES = [
    {"id": 0, "name": "Transcription", "output": "0_transcript.txt", "prereq": None},
    {"id": 1, "name": "Summarization", "output": "1_summary.txt", "prereq": "0_transcript.txt"},
    {"id": 2, "name": "Text-to-Speech", "output": "2_audio.mp3", "prereq": "1_summary.txt"},
    {"id": 3, "name": "Image Prompts", "output": "3_image_prompts.json", "prereq": "1_summary.txt"},
    {"id": 4, "name": "Metadata", "output": "4_metadata.json", "prereq": "1_summary.txt"},
    {"id": 5, "name": "Image Generation", "output": "5_images/", "prereq": "3_image_prompts.json"},
    {"id": 6, "name": "Video Composition", "output": "6_final_video.mp4", "prereq": "2_audio.mp3"},
]


def setup_project_directories(project_name):
    """Creates the necessary directory structure for a new video project."""
    base_path = os.path.join("projects", project_name)
    
    if os.path.exists(base_path):
        print(f"Project '{project_name}' already exists. Using existing directory.")
        return base_path

    os.makedirs(os.path.join(base_path, "5_images"))
    print(f"✅ Project '{project_name}' created successfully at: {base_path}")
    return base_path


def get_stage_status(project_path, output):
    """Check if a stage output exists."""
    path = os.path.join(project_path, output)
    if output.endswith("/"):
        # Directory - check if exists and has files
        return os.path.isdir(path) and len(os.listdir(path)) > 0
    else:
        return os.path.isfile(path) and os.path.getsize(path) > 0


def print_pipeline_status(project_name, project_path):
    """Display current pipeline status with checkmarks."""
    print(f"\n--- Pipeline Status ---")
    print(f"Project: {project_name}")
    print(f"Path: {os.path.abspath(project_path)}")
    print("-" * 30)
    
    for stage in PIPELINE_STAGES:
        exists = get_stage_status(project_path, stage["output"])
        status = "✅" if exists else "❌"
        print(f"  {stage['id']}. {stage['output']:<22} {status}")
    print("-" * 30)


def check_prerequisite(project_path, stage_id):
    """Check if prerequisite for a stage exists. Returns (ok, message)."""
    stage = PIPELINE_STAGES[stage_id]
    prereq = stage["prereq"]
    
    if prereq is None:
        return True, None
    
    prereq_path = os.path.join(project_path, prereq)
    if prereq.endswith("/"):
        exists = os.path.isdir(prereq_path) and len(os.listdir(prereq_path)) > 0
    else:
        exists = os.path.isfile(prereq_path) and os.path.getsize(prereq_path) > 0
    
    if not exists:
        return False, f"Missing prerequisite: {prereq}"
    return True, None


def confirm_overwrite(project_path, output):
    """Ask user to confirm overwrite if output exists."""
    if not get_stage_status(project_path, output):
        return True  # Doesn't exist, proceed
    
    print(f"\n⚠️  Output already exists: {output}")
    choice = input("Overwrite? (y/n): ").strip().lower()
    return choice == 'y'


def run_stage(project_path, stage_id):
    """Run a specific pipeline stage. Returns True on success."""
    stage = PIPELINE_STAGES[stage_id]
    output = stage["output"]
    
    # Check prerequisite
    ok, msg = check_prerequisite(project_path, stage_id)
    if not ok:
        print(f"❌ Cannot run {stage['name']}: {msg}")
        return False
    
    # Check overwrite
    if not confirm_overwrite(project_path, output):
        print("Skipped.")
        return True  # User chose to skip, not a failure
    
    print(f"\n🚀 Running: {stage['name']}...")
    
    try:
        if stage_id == 0:
            # Transcription - needs YouTube URL
            youtube_url = input("Enter the YouTube URL to transcribe: ").strip()
            if not youtube_url:
                print("❌ URL cannot be empty.")
                return False
            output_path = os.path.join(project_path, "0_transcript.txt")
            transcription.transcribe_youtube_audio(youtube_url, output_path)
            
        elif stage_id == 1:
            # Summarization
            input_path = os.path.join(project_path, "0_transcript.txt")
            output_path = os.path.join(project_path, "1_summary.txt")
            summarization.summarize_transcript(input_path, output_path)
            
        elif stage_id == 2:
            # Text-to-Speech
            input_path = os.path.join(project_path, "1_summary.txt")
            output_path = os.path.join(project_path, "2_audio.mp3")
            text_to_speech.synthesize_speech(input_path, output_path)
            
        elif stage_id == 3:
            # Image Prompts
            summary_path = os.path.join(project_path, "1_summary.txt")
            audio_path = os.path.join(project_path, "2_audio.mp3")
            output_path = os.path.join(project_path, "3_image_prompts.json")
            # Audio might not exist yet - check and handle
            if not os.path.exists(audio_path):
                print("⚠️  Audio file not found. Running TTS first...")
                if not run_stage(project_path, 2):
                    return False
            image_prompting.generate_image_prompts(summary_path, audio_path, output_path)
            
        elif stage_id == 4:
            # Metadata
            input_path = os.path.join(project_path, "1_summary.txt")
            output_path = os.path.join(project_path, "4_metadata.json")
            metadata_generation.generate_metadata(input_path, output_path)
            
        elif stage_id == 5:
            # Image Generation
            input_path = os.path.join(project_path, "3_image_prompts.json")
            output_dir = os.path.join(project_path, "5_images")
            os.makedirs(output_dir, exist_ok=True)
            image_creation.create_images_from_prompts(input_path, output_dir)
            
        elif stage_id == 6:
            # Video Composition
            audio_path = os.path.join(project_path, "2_audio.mp3")
            images_dir = os.path.join(project_path, "5_images")
            output_path = os.path.join(project_path, "6_final_video.mp4")
            # Check images exist
            if not get_stage_status(project_path, "5_images/"):
                print("❌ No images found. Run image generation first.")
                return False
            video_composition.compose_video(images_dir, audio_path, output_path)
        
        print(f"✅ {stage['name']} complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error in {stage['name']}: {e}")
        return False


def get_next_missing_stage(project_path):
    """Find the first stage with missing output. Returns stage_id or None."""
    for stage in PIPELINE_STAGES:
        if not get_stage_status(project_path, stage["output"]):
            return stage["id"]
    return None


def run_full_pipeline(project_path):
    """Run all remaining stages from current point."""
    print("\n🔄 Running full pipeline from current point...")
    
    # Determine starting point
    start_stage = get_next_missing_stage(project_path)
    
    if start_stage is None:
        print("✅ All stages complete! Nothing to run.")
        return
    
    # Special case: if starting from stage 0, need YouTube URL
    # If starting from stage 1+, we can auto-run
    
    for stage in PIPELINE_STAGES:
        if stage["id"] < start_stage:
            continue  # Skip completed stages
        
        # Skip if output already exists
        if get_stage_status(project_path, stage["output"]):
            print(f"⏭️  Skipping {stage['name']} (already exists)")
            continue
        
        if not run_stage(project_path, stage["id"]):
            print(f"\n⚠️  Pipeline stopped at {stage['name']}")
            return
    
    print("\n🎉 Pipeline complete! Final video ready.")


def pipeline_menu(project_name, project_path):
    """Display pipeline menu and handle actions."""
    while True:
        print_pipeline_status(project_name, project_path)
        
        print("\nChoose action:")
        print("1. Run next missing step")
        print("2. Run full pipeline from current point")
        print("3. Run specific step")
        print("4. Show project folder path")
        print("9. Back to main menu")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            next_stage = get_next_missing_stage(project_path)
            if next_stage is None:
                print("✅ All stages complete!")
            else:
                run_stage(project_path, next_stage)
                
        elif choice == '2':
            run_full_pipeline(project_path)
            
        elif choice == '3':
            print("\nAvailable stages:")
            for stage in PIPELINE_STAGES:
                print(f"  {stage['id']}. {stage['name']}")
            stage_choice = input("Enter stage number (0-6): ").strip()
            try:
                stage_id = int(stage_choice)
                if 0 <= stage_id <= 6:
                    run_stage(project_path, stage_id)
                else:
                    print("Invalid stage number.")
            except ValueError:
                print("Please enter a number.")
                
        elif choice == '4':
            abs_path = os.path.abspath(project_path)
            print(f"\n📁 Project folder: {abs_path}")
            print(f"   Open with: cd {abs_path}")
            log_file = get_log_path()
            if log_file:
                print(f"📝 Log file: {log_file}")
            
        elif choice == '9':
            break
        else:
            print("Invalid choice.")


def handle_youtube_url(project_path):
    """Handles the YouTube URL transcription workflow."""
    youtube_url = input("Enter the YouTube URL to transcribe: ").strip()
    if youtube_url:
        transcript_file_path = os.path.join(project_path, "0_transcript.txt")
        try:
            transcription.transcribe_youtube_audio(youtube_url, transcript_file_path)
            print(f"\n✅ Transcription complete!")
            return True
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            return False
    else:
        print("URL cannot be empty.")
        return False


def handle_ready_script(project_path):
    """Handles the workflow for a user-provided script."""
    script_path = os.path.join(project_path, "1_summary.txt")
    abs_path = os.path.abspath(script_path)
    
    print("\n" + "=" * 50)
    print("Ready-Made Script Mode")
    print("=" * 50)
    print(f"\nPlease save your script to:\n  {abs_path}")
    print("\nThis file should contain your final narration script.")
    print("=" * 50)
    
    input("\nPress Enter after you have saved the file...")
    
    if os.path.exists(script_path) and os.path.getsize(script_path) > 0:
        print(f"✅ Script detected!")
        return True
    else:
        print("❌ Script file not found or is empty.")
        return False


def main_menu(project_name, project_path):
    """Displays the main menu and handles user choices."""
    while True:
        print("\n" + "=" * 40)
        print("--- Main Menu ---")
        print(f"Project: {project_name}")
        print("=" * 40)
        print("\nChoose your input source:")
        print("1. Transcribe from YouTube URL")
        print("2. Scrape from Article URL (coming soon)")
        print("3. Use a Ready-Made Script")
        print("4. Go to Pipeline Menu")
        print("9. Exit")
        
        choice = input("\nEnter your choice: ").strip()

        if choice == '1':
            if handle_youtube_url(project_path):
                # After successful transcription, go to pipeline menu
                pipeline_menu(project_name, project_path)
        elif choice == '2':
            print("\n⏳ This feature will be implemented soon using crawl4ai.")
        elif choice == '3':
            if handle_ready_script(project_path):
                # After script is ready, go to pipeline menu
                pipeline_menu(project_name, project_path)
        elif choice == '4':
            pipeline_menu(project_name, project_path)
        elif choice == '9':
            print("\n👋 Exiting. Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")


def main():
    """Main function to run the video generator application."""
    print("\n" + "=" * 50)
    print("🎬 Bibo YouTube Video Generator")
    print("=" * 50)
    
    project_name = input("\nEnter project name (e.g., 'MyNewVideo'): ").strip()
    
    if not project_name:
        print("Project name cannot be empty. Exiting.")
        return

    # Initialize logging
    log_path = init_logging(project_name)
    print(f"📝 Logging to: {log_path}")

    try:
        project_path = setup_project_directories(project_name)
        main_menu(project_name, project_path)
    finally:
        stop_logging()
        print(f"\n📝 Log saved to: {log_path}")


if __name__ == "__main__":
    main()