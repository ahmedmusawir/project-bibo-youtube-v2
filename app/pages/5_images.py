"""
Images Page - Generate image prompts and AI images for the video
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
from src.image_prompting import generate_image_prompts
from src.image_creation import create_images_from_prompts


# Page config
st.set_page_config(
    page_title="Images - VidGen",
    page_icon="🖼️",
    layout="wide"
)

# Render sidebar
render_sidebar()


def main():
    """Images page main content."""

    # Check if project is selected
    if not st.session_state.get("current_project"):
        st.warning("👈 Please select or create a project first")
        return

    project_name = st.session_state.current_project
    project_path = get_project_path(project_name)
    script_file = project_path / "1_summary.txt"
    audio_file = project_path / "2_audio.mp3"
    prompts_file = project_path / "3_image_prompts.json"
    images_dir = project_path / "5_images"

    # Page header
    st.markdown(f"# 🖼️ Images")
    st.markdown(f"**Project:** {project_name}")
    st.markdown("---")

    # Check prerequisites
    audio_exists = stage_file_exists(project_name, "audio")
    audio_approved = get_approval_status(project_name, "audio")

    if not audio_exists or not audio_approved:
        st.warning("⚠️ **Audio must be approved first**")
        st.info("👈 Go to **Audio** page to generate and approve the narration")
        return

    # Step 1: Image Prompts
    st.markdown("## 📝 Step 1: Generate Image Prompts")

    prompts_exist = prompts_file.exists()

    if not prompts_exist:
        st.info("💡 Generate AI prompts for images that will sync with your audio")

        if st.button("🤖 Generate Image Prompts", key="gen_prompts_btn", type="primary", use_container_width=True):
            with st.spinner("Generating image prompts from script..."):
                try:
                    generate_image_prompts(
                        str(script_file),
                        str(audio_file),
                        str(prompts_file)
                    )

                    st.success("✅ Image prompts generated!")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)

    else:
        # Display prompts
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts_content = f.read()

        prompts_list = [p.strip() for p in prompts_content.split('\n') if p.strip()]

        with st.expander(f"📋 View Image Prompts ({len(prompts_list)} prompts)", expanded=False):
            st.text_area(
                "Image Prompts",
                value=prompts_content,
                height=300,
                key="prompts_viewer"
            )

        col1, col2 = st.columns([5, 1])
        with col1:
            st.success(f"✅ {len(prompts_list)} image prompts ready")
        with col2:
            if st.button("🔄 Regenerate", key="regen_prompts_btn"):
                with st.spinner("Regenerating prompts..."):
                    try:
                        generate_image_prompts(
                            str(script_file),
                            str(audio_file),
                            str(prompts_file)
                        )
                        st.success("✅ Prompts regenerated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        st.markdown("---")

        # Step 2: Generate Images
        st.markdown("## 🎨 Step 2: Generate Images")

        images_exist = images_dir.exists() and any(images_dir.glob("*.png"))

        if not images_exist:
            st.info(f"💡 Generate {len(prompts_list)} AI images using Vertex AI Imagen")

            st.warning("⚠️ **Note:** Image generation can take 5-10 minutes depending on the number of images")

            if st.button("🎨 Generate Images", key="gen_images_btn", type="primary", use_container_width=True):
                with st.spinner(f"Generating {len(prompts_list)} images... This may take several minutes..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        # Generate images
                        create_images_from_prompts(
                            str(prompts_file),
                            str(images_dir)
                        )

                        progress_bar.progress(100)
                        status_text.empty()

                        st.success(f"✅ {len(prompts_list)} images generated!")
                        st.balloons()
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.exception(e)

        else:
            # Display Images Gallery
            st.markdown("### 🖼️ Image Gallery")

            image_files = sorted(images_dir.glob("*.png"))

            col1, col2 = st.columns([5, 1])
            with col1:
                st.success(f"✅ {len(image_files)} images generated")
            with col2:
                if st.button("🔄 Regenerate", key="regen_images_btn"):
                    with st.spinner("Regenerating images..."):
                        try:
                            create_images_from_prompts(
                                str(prompts_file),
                                str(images_dir)
                            )

                            # Reset approval
                            set_approval(project_name, "images", False)

                            st.success("✅ Images regenerated!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

            st.markdown("---")

            # Display images in grid
            cols_per_row = 3
            for i in range(0, len(image_files), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(image_files):
                        with col:
                            img_file = image_files[idx]
                            st.image(str(img_file), use_container_width=True, caption=f"Image {idx + 1}")

            st.markdown("---")

            # Approval Section
            is_approved = get_approval_status(project_name, "images")

            st.markdown("## ✅ Approval")

            if is_approved:
                st.success("✅ **Images are approved and ready for video composition**")

                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("❌ Revoke", key="revoke_approval_btn"):
                        set_approval(project_name, "images", False)
                        st.success("✅ Approval revoked")
                        st.rerun()

                with col2:
                    st.info("👉 Go to **Video** page to compose the final video")

            else:
                st.warning("⚠️ **Images pending approval**")

                if st.button("✅ Approve Images", key="approve_images_btn", type="primary", use_container_width=True):
                    set_approval(project_name, "images", True)
                    st.success("✅ Images approved! Ready for video composition.")
                    st.balloons()
                    st.rerun()


if __name__ == "__main__":
    main()
