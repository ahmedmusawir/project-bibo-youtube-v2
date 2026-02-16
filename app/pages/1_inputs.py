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
        Enter a YouTube URL. The system will transcribe the video and generate a script from it.

        ⚠️ **Note:** This feature requires additional implementation (transcription step).
        For MVP, use the "Paste Text" tab to directly input your script.
        """)

        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://youtube.com/watch?v=...",
            key="youtube_url_input"
        )

        if st.button("🎥 Transcribe Video", key="transcribe_btn", disabled=True):
            st.info("⚠️ Transcription feature coming in Phase 2")


if __name__ == "__main__":
    main()
