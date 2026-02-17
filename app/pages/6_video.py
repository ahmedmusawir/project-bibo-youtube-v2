"""
Video Page - Compose final video and download
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
from src.video_composition import compose_video


# Page config
st.set_page_config(
    page_title="Video - VidGen",
    page_icon="🎬",
    layout="wide"
)

# Render sidebar
render_sidebar()


def main():
    """Video page main content."""

    # Check if project is selected
    if not st.session_state.get("current_project"):
        st.warning("👈 Please select or create a project first")
        return

    project_name = st.session_state.current_project
    project_path = get_project_path(project_name)
    audio_file = project_path / "2_audio.mp3"
    images_dir = project_path / "5_images"
    video_file = project_path / "6_final_video.mp4"

    # Page header
    st.markdown(f"# 🎬 Video")
    st.markdown(f"**Project:** {project_name}")
    st.markdown("---")

    # Check prerequisites
    audio_exists = stage_file_exists(project_name, "audio")
    audio_approved = get_approval_status(project_name, "audio")
    images_exist = stage_file_exists(project_name, "images")
    images_approved = get_approval_status(project_name, "images")

    # Prerequisites check
    if not audio_exists or not audio_approved:
        st.error("❌ **Audio must be approved first**")
        st.info("👈 Go to **Audio** page")
        return

    if not images_exist or not images_approved:
        st.error("❌ **Images must be approved first**")
        st.info("👈 Go to **Images** page")
        return

    # Video Composition Section
    st.markdown("## 🎬 Video Composition")

    video_exists = stage_file_exists(project_name, "video")

    if not video_exists:
        st.info("💡 Compose the final video by combining audio narration and AI-generated images")

        st.warning("⚠️ **Note:** Video composition can take 10-15 minutes for longer videos")

        if st.button("🎬 Compose Video", key="compose_video_btn", type="primary", use_container_width=True):
            log_container = st.empty()
            with st.spinner("Composing video... This may take 10-15 minutes..."):
                try:
                    with capture_stdout_to_streamlit(log_container, session_key="video_gen_log"):
                        compose_video(
                            str(images_dir),
                            str(audio_file),
                            str(video_file)
                        )

                    st.success("✅ Video composed successfully!")
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error composing video: {str(e)}")
                    st.exception(e)

    else:
        # Display Video
        st.markdown("### 🎥 Final Video")

        # Get video stats
        video_size = video_file.stat().st_size / (1024 * 1024)  # MB

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{video_size:.2f} MB")
        with col2:
            st.metric("Format", "MP4")
        with col3:
            is_approved = get_approval_status(project_name, "video")
            if is_approved:
                st.success("✅ Approved")
            else:
                st.warning("⚠️ Pending")

        st.markdown("---")

        # Video Player
        with open(video_file, 'rb') as f:
            video_bytes = f.read()

        st.video(video_bytes)

        st.markdown("---")

        # Actions Section
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔄 Regenerate")

            if st.button("🔄 Regenerate Video", key="regen_video_btn", use_container_width=True):
                log_container = st.empty()
                with st.spinner("Regenerating video... This may take 10-15 minutes..."):
                    try:
                        with capture_stdout_to_streamlit(log_container, session_key="video_gen_log"):
                            compose_video(
                                str(images_dir),
                                str(audio_file),
                                str(video_file)
                            )

                        # Reset approval
                        set_approval(project_name, "video", False)

                        st.success("✅ Video regenerated!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        with col2:
            st.markdown("### 💾 Download")

            # Download button
            with open(video_file, 'rb') as f:
                video_bytes = f.read()

            st.download_button(
                label="⬇️ Download Video",
                data=video_bytes,
                file_name=f"{project_name}_final.mp4",
                mime="video/mp4",
                use_container_width=True
            )

        st.markdown("---")

        # Process Log
        show_process_log("video_gen_log", "📋 Video Composition Log")

        # Approval Section
        st.markdown("## ✅ Final Approval")

        if is_approved:
            st.success("✅ **Video is approved and ready for upload!**")

            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("❌ Revoke", key="revoke_approval_btn"):
                    set_approval(project_name, "video", False)
                    st.success("✅ Approval revoked")
                    st.rerun()

            with col2:
                st.markdown("""
                ### 🎉 **Congratulations!**

                Your video is complete and ready for YouTube upload!

                **Next Steps:**
                1. Download the video using the button above
                2. Upload to YouTube
                3. Use the metadata from the **Metadata** page for title/description
                4. Create a new project to generate more videos!
                """)

        else:
            st.warning("⚠️ **Video pending final approval**")

            if st.button("✅ Approve Video", key="approve_video_btn", type="primary", use_container_width=True):
                set_approval(project_name, "video", True)
                st.success("✅ Video approved! 🎉")
                st.balloons()
                st.rerun()


if __name__ == "__main__":
    main()
