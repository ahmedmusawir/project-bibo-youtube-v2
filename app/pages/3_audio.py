"""
Audio Page - Generate narration audio with voice selection
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
from src.text_to_speech import synthesize_speech
from src.utils.config import (
    get_tts_voice,
    get_tts_lang,
    get_available_tts_voices,
    set_tts_voice
)


# Page config
st.set_page_config(
    page_title="Audio - VidGen",
    page_icon="🎵",
    layout="wide"
)

# Render sidebar
render_sidebar()


def main():
    """Audio page main content."""

    # Check if project is selected
    if not st.session_state.get("current_project"):
        st.warning("👈 Please select or create a project first")
        return

    project_name = st.session_state.current_project
    project_path = get_project_path(project_name)
    script_file = project_path / "1_summary.txt"
    audio_file = project_path / "2_audio.mp3"

    # Page header
    st.markdown(f"# 🎵 Audio")
    st.markdown(f"**Project:** {project_name}")
    st.markdown("---")

    # Check prerequisites
    script_exists = stage_file_exists(project_name, "script")
    script_approved = get_approval_status(project_name, "script")

    if not script_exists:
        st.error("❌ **Script not found**")
        st.info("👈 Go to **Script** page to create your script first")
        return

    if not script_approved:
        st.warning("⚠️ **Script not approved yet**")
        st.info("👈 Go to **Script** page to review and approve the script before generating audio")
        return

    # Voice Configuration Section
    st.markdown("## 🎤 Voice Configuration")

    # Get available voices
    available_voices = get_available_tts_voices()
    current_voice_id = get_tts_voice()
    current_lang = get_tts_lang()

    # Create voice selector
    voice_options = {v["id"]: v["label"] for v in available_voices}
    voice_labels = list(voice_options.values())
    voice_ids = list(voice_options.keys())

    # Find current voice index
    try:
        current_index = voice_ids.index(current_voice_id)
    except ValueError:
        current_index = 0

    selected_label = st.selectbox(
        "Select Voice",
        voice_labels,
        index=current_index,
        key="voice_selector"
    )

    # Get selected voice ID
    selected_voice_id = voice_ids[voice_labels.index(selected_label)]

    # Display voice info
    selected_voice_info = next((v for v in available_voices if v["id"] == selected_voice_id), None)
    if selected_voice_info:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"**Selected:** {selected_voice_info['label']} ({selected_voice_info['lang']})")
        with col2:
            if selected_voice_id != current_voice_id:
                if st.button("💾 Save Voice", key="save_voice_btn"):
                    set_tts_voice(selected_voice_id, selected_voice_info['lang'])
                    st.success("✅ Voice saved to config")
                    st.rerun()

    st.markdown("---")

    # Check if audio exists
    audio_exists = stage_file_exists(project_name, "audio")
    is_approved = get_approval_status(project_name, "audio")

    # Audio Generation Section
    st.markdown("## 🎙️ Audio Generation")

    if not audio_exists:
        st.info("💡 Click the button below to generate narration audio from your script")

        if st.button("🎵 Generate Audio", key="gen_audio_btn", type="primary", use_container_width=True):
            log_container = st.empty()
            with st.spinner(f"Generating audio with {selected_voice_info['label']}..."):
                try:
                    # Update voice config before generation
                    if selected_voice_id != current_voice_id:
                        set_tts_voice(selected_voice_id, selected_voice_info['lang'])

                    # Generate audio
                    with capture_stdout_to_streamlit(log_container, session_key="audio_gen_log"):
                        synthesize_speech(
                            str(script_file),
                            str(audio_file)
                        )

                    st.success("✅ Audio generated successfully!")
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error generating audio: {str(e)}")
                    st.exception(e)

    else:
        # Audio Player
        st.markdown("### 🔊 Audio Player")

        # Get audio file size and duration
        audio_size = audio_file.stat().st_size / (1024 * 1024)  # MB

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{audio_size:.2f} MB")
        with col2:
            if is_approved:
                st.success("✅ Approved")
            else:
                st.warning("⚠️ Pending")
        with col3:
            st.metric("Voice", selected_voice_info['label'] if selected_voice_info else "Unknown")

        # Play audio
        with open(audio_file, 'rb') as f:
            audio_bytes = f.read()

        st.audio(audio_bytes, format='audio/mp3')

        st.markdown("---")

        # Regenerate Section
        st.markdown("### 🔄 Regenerate")

        col1, col2 = st.columns(2)

        with col1:
            st.info("**Change voice and regenerate if needed**")

        with col2:
            if st.button("🔄 Regenerate Audio", key="regen_audio_btn"):
                log_container = st.empty()
                with st.spinner("Regenerating audio..."):
                    try:
                        # Update voice if changed
                        if selected_voice_id != current_voice_id:
                            set_tts_voice(selected_voice_id, selected_voice_info['lang'])

                        # Regenerate
                        with capture_stdout_to_streamlit(log_container, session_key="audio_gen_log"):
                            synthesize_speech(
                                str(script_file),
                                str(audio_file)
                            )

                        # Reset approval
                        set_approval(project_name, "audio", False)

                        st.success("✅ Audio regenerated! Review and approve below.")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        st.markdown("---")

        # Process Log
        show_process_log("audio_gen_log", "📋 Audio Generation Log")

        # Approval Section
        st.markdown("## ✅ Approval")

        if is_approved:
            st.success("✅ **Audio is approved and ready for image generation**")

            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("❌ Revoke Approval", key="revoke_approval_btn"):
                    set_approval(project_name, "audio", False)
                    st.success("✅ Approval revoked")
                    st.rerun()

            with col2:
                st.info("👉 Go to **Images** page to generate visuals")

        else:
            st.warning("⚠️ **Audio pending approval**")
            st.markdown("Listen to the audio above and approve it to proceed to image generation.")

            if st.button("✅ Approve Audio", key="approve_audio_btn", type="primary", use_container_width=True):
                set_approval(project_name, "audio", True)
                st.success("✅ Audio approved! You can now generate images.")
                st.balloons()
                st.rerun()


if __name__ == "__main__":
    main()
