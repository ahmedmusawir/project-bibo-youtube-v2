"""
Script Page - Review, edit, and approve the generated script
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
from app.state import (
    get_project_path,
    stage_file_exists,
    get_approval_status,
    set_approval
)
from app.utils import capture_stdout_to_streamlit, show_process_log
from src.summarization import summarize_transcript
from src.utils.config import (
    get_summarization_llm,
    get_available_summarization_llms,
    set_summarization_llm
)


# Page config
st.set_page_config(
    page_title="Script - VidGen",
    page_icon="📄",
    layout="wide"
)

# Render sidebar
render_sidebar()


def main():
    """Script page main content."""

    # Check if project is selected
    if not st.session_state.get("current_project"):
        st.warning("👈 Please select or create a project first")
        return

    project_name = st.session_state.current_project
    project_path = get_project_path(project_name)
    script_file = project_path / "1_summary.txt"
    transcript_file = project_path / "0_transcript.txt"

    # Page header
    st.markdown(f"# 📄 Script")
    st.markdown(f"**Project:** {project_name}")
    st.markdown("---")

    # LLM Model Configuration Section
    st.markdown("## 🤖 AI Model Configuration")
    
    # Get available models
    available_models = get_available_summarization_llms()
    current_model = get_summarization_llm()
    
    # Create model selector
    try:
        current_index = available_models.index(current_model)
    except ValueError:
        current_index = 0
    
    selected_model = st.selectbox(
        "Select Summarization Model",
        available_models,
        index=current_index,
        key="summarization_model_selector"
    )
    
    # Display model info and save button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"**Selected:** {selected_model}")
    with col2:
        if selected_model != current_model:
            if st.button("💾 Save Model", key="save_model_btn"):
                set_summarization_llm(selected_model)
                st.success("✅ Model saved to config")
                st.rerun()
    
    st.markdown("---")

    # Check if script exists
    script_exists = stage_file_exists(project_name, "script")

    if not script_exists:
        # Check if transcript exists
        if transcript_file.exists():
            transcript_text = transcript_file.read_text(encoding='utf-8')
            word_count = len(transcript_text.split())

            st.success(f"✅ Transcript ready — **{word_count:,} words** (`0_transcript.txt`)")

            with st.expander("📄 View Transcript", expanded=False):
                st.text_area(
                    "Transcript content",
                    value=transcript_text,
                    height=300,
                    disabled=True,
                    label_visibility="collapsed"
                )

            st.markdown("---")
            st.markdown("### 🎬 Create YouTube Script")
            st.markdown("Generate a polished YouTube script from your transcript using AI summarization.")

            if st.button("🎬 Create YouTube Script", key="gen_script_btn", type="primary", use_container_width=True):
                log_container = st.empty()
                with st.spinner("Generating YouTube script from transcript..."):
                    try:
                        with capture_stdout_to_streamlit(log_container, session_key="script_gen_log"):
                            summarize_transcript(
                                str(transcript_file),
                                str(script_file)
                            )
                        st.success("✅ YouTube script created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error generating script: {str(e)}")

            show_process_log("script_gen_log", "📋 Script Generation Log")

        else:
            st.warning("⚠️ No transcript found. Please create one first.")
            st.info("👈 Go to **Inputs** page to paste text or transcribe a YouTube video")

        return

    # Load script content
    with open(script_file, 'r', encoding='utf-8') as f:
        script_content = f.read()

    # Get approval status
    is_approved = get_approval_status(project_name, "script")

    # Stats
    word_count = len(script_content.split())
    char_count = len(script_content)
    estimated_duration = word_count / 150  # ~150 words per minute

    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Words", f"{word_count:,}")
    with col2:
        st.metric("Characters", f"{char_count:,}")
    with col3:
        st.metric("Est. Duration", f"{estimated_duration:.1f} min")
    with col4:
        if is_approved:
            st.success("✅ Approved")
        else:
            st.warning("⚠️ Pending")

    st.markdown("---")

    # Edit/View Script
    st.markdown("## Script Content")

    # Toggle between view and edit mode
    edit_mode = st.checkbox("✏️ Edit Mode", value=False, key="edit_mode")

    if edit_mode:
        st.info("💡 **Tip:** Make your edits below and click **Save Changes**")

        edited_content = st.text_area(
            "Script",
            value=script_content,
            height=400,
            key="script_editor"
        )

        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("💾 Save Changes", key="save_script_btn", type="primary"):
                with open(script_file, 'w', encoding='utf-8') as f:
                    f.write(edited_content)

                # Reset approval if content changed
                if edited_content != script_content:
                    set_approval(project_name, "script", False)
                    st.success("✅ Changes saved! Please re-approve the script.")
                else:
                    st.info("No changes detected")

                st.rerun()

        with col2:
            if st.button("🔄 Regenerate Script", key="regen_script_btn"):
                if transcript_file.exists():
                    log_container = st.empty()
                    with st.spinner("Regenerating script..."):
                        try:
                            with capture_stdout_to_streamlit(log_container, session_key="script_gen_log"):
                                summarize_transcript(
                                    str(transcript_file),
                                    str(script_file)
                                )
                            set_approval(project_name, "script", False)
                            st.success("✅ Script regenerated! Review and approve below.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("❌ Transcript not found. Cannot regenerate.")

    else:
        # View mode - display as markdown
        st.markdown(f"""
        <div style="
            background-color: #f8f9fa;
            padding: 2rem;
            border-radius: 0.5rem;
            border-left: 4px solid #FF6B35;
            max-height: 500px;
            overflow-y: auto;
        ">
            {script_content.replace('\n', '<br>')}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Process Log
    show_process_log("script_gen_log", "📋 Script Generation Log")

    # Approval Section
    st.markdown("## Approval")

    if is_approved:
        st.success("✅ **This script is approved and ready for audio generation**")

        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("❌ Revoke Approval", key="revoke_approval_btn"):
                set_approval(project_name, "script", False)
                st.success("✅ Approval revoked")
                st.rerun()

        with col2:
            st.info("👉 Go to **Audio** page to generate narration")

    else:
        st.warning("⚠️ **Script pending approval**")
        st.markdown("""
        Review the script above and approve it to proceed to audio generation.
        You can also edit the script if needed.
        """)

        if st.button("✅ Approve Script", key="approve_script_btn", type="primary"):
            set_approval(project_name, "script", True)
            st.success("✅ Script approved! You can now generate audio.")
            st.balloons()
            st.rerun()


if __name__ == "__main__":
    main()
