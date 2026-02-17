"""
Inputs Page - Paste text or YouTube URL to create initial script
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from pathlib import Path
from app.components.sidebar import render_sidebar
from app.state import get_project_path, stage_file_exists
from app.utils import capture_stdout_to_streamlit


# Page config
st.set_page_config(
    page_title="Inputs - VidGen",
    page_icon="📝",
    layout="wide"
)

# Render sidebar
render_sidebar()

# Main content
def main():
    """Inputs page main content."""

    # Check if project is selected
    if not st.session_state.get("current_project"):
        st.warning("👈 Please select or create a project first")
        return

    project_name = st.session_state.current_project
    project_path = get_project_path(project_name)

    # Page header
    st.markdown(f"# 📝 Inputs")
    st.markdown(f"**Project:** {project_name}")
    st.markdown("---")

    # Check if script already exists
    script_exists = stage_file_exists(project_name, "script")

    if script_exists:
        st.info("✅ Script already exists. You can view/edit it in the **Script** page.")
        st.markdown("**Or paste new content below to replace it:**")

    # Input section
    st.markdown("## Source Material")

    # Tab selector for input type
    tab1, tab2 = st.tabs(["📄 Paste Text", "🎥 YouTube URL"])

    with tab1:
        st.markdown("""
        Paste your text content below. This will be used to generate the video script.
        """)

        text_content = st.text_area(
            "Text Content",
            height=300,
            placeholder="Paste your article, blog post, or script here...",
            help="Maximum 10,000 characters recommended",
            key="text_input"
        )

        char_count = len(text_content) if text_content else 0
        st.caption(f"Characters: {char_count:,}")

        if st.button("💾 Save as Script", key="save_text_btn", type="primary"):
            if text_content and text_content.strip():
                # Save to 1_summary.txt
                script_file = project_path / "1_summary.txt"
                script_file.parent.mkdir(parents=True, exist_ok=True)

                with open(script_file, 'w', encoding='utf-8') as f:
                    f.write(text_content.strip())

                st.success(f"✅ Saved to `1_summary.txt` ({len(text_content.strip().split())} words)")
                st.info("👉 Go to **Script** page to review and approve")

            else:
                st.error("Please paste some text content")

    with tab2:
        st.markdown("""
        Enter a YouTube URL. The system will download the audio and transcribe it.
        Once the transcript is ready, head to the **Script** page to generate your script.
        """)

        # Show existing transcript if present
        transcript_file = project_path / "0_transcript.txt"
        if transcript_file.exists():
            transcript_text = transcript_file.read_text(encoding='utf-8')
            word_count = len(transcript_text.split())
            st.success(f"✅ Transcript ready — {word_count:,} words")
            st.info("👉 Go to **Script** page to generate your script from this transcript")
            with st.expander("📄 View Transcript", expanded=False):
                st.text_area(
                    "Transcript content",
                    value=transcript_text,
                    height=400,
                    disabled=True,
                    label_visibility="collapsed"
                )

        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://youtube.com/watch?v=...",
            key="youtube_url_input"
        )

        url_valid = youtube_url and ("youtube.com/watch" in youtube_url or "youtu.be/" in youtube_url)

        if st.button("🎥 Transcribe Video", key="transcribe_btn", disabled=not url_valid, type="primary"):
            # Force-load .env from project root so GOOGLE_STT_BUCKET etc. are available
            from dotenv import load_dotenv
            load_dotenv(project_root / ".env", override=True)

            from src.transcription import transcribe_youtube_audio

            transcript_path = str(project_path / "0_transcript.txt")

            project_path.mkdir(parents=True, exist_ok=True)

            st.info("⏳ This may take **10-30 minutes** for long videos. Do not close this page.")
            log_container = st.empty()

            with st.spinner("🔄 Transcribing... please wait"):
                try:
                    with capture_stdout_to_streamlit(log_container):
                        transcribe_youtube_audio(youtube_url, transcript_path)

                except Exception as e:
                    st.error(f"❌ Error: {e}")

            if Path(transcript_path).exists():
                st.success("🎉 Transcription complete!")
                st.rerun()

        if youtube_url and not url_valid:
            st.warning("Please enter a valid YouTube URL (e.g. https://www.youtube.com/watch?v=...)")


if __name__ == "__main__":
    main()
