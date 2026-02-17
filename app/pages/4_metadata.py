"""
Metadata Page - Generate YouTube titles, descriptions, and hashtags
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
import json
from pathlib import Path
from app.components.sidebar import render_sidebar
from app.state import (
    get_project_path,
    stage_file_exists,
    get_approval_status,
    set_approval
)
from app.utils import capture_stdout_to_streamlit, show_process_log
from src.metadata_generation import generate_metadata


# Page config
st.set_page_config(
    page_title="Metadata - VidGen",
    page_icon="📋",
    layout="wide"
)

# Render sidebar
render_sidebar()


def main():
    """Metadata page main content."""

    # Check if project is selected
    if not st.session_state.get("current_project"):
        st.warning("👈 Please select or create a project first")
        return

    project_name = st.session_state.current_project
    project_path = get_project_path(project_name)
    script_file = project_path / "1_summary.txt"
    metadata_file = project_path / "4_metadata.json"

    # Page header
    st.markdown(f"# 📋 Metadata")
    st.markdown(f"**Project:** {project_name}")
    st.markdown("---")

    # Check prerequisites
    script_exists = stage_file_exists(project_name, "script")
    script_approved = get_approval_status(project_name, "script")

    if not script_exists or not script_approved:
        st.warning("⚠️ **Script must be approved first**")
        st.info("👈 Go to **Script** page to review and approve the script")
        return

    # Check if metadata exists
    metadata_exists = stage_file_exists(project_name, "metadata")
    is_approved = get_approval_status(project_name, "metadata")

    # Metadata Generation Section
    st.markdown("## 📝 Generate Metadata")

    if not metadata_exists:
        st.info("💡 Generate YouTube-optimized titles, descriptions, and hashtags from your script")

        if st.button("🤖 Generate Metadata", key="gen_metadata_btn", type="primary", use_container_width=True):
            log_container = st.empty()
            with st.spinner("Generating metadata with AI..."):
                try:
                    with capture_stdout_to_streamlit(log_container, session_key="metadata_gen_log"):
                        generate_metadata(
                            str(script_file),
                            str(metadata_file)
                        )

                    st.success("✅ Metadata generated successfully!")
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error generating metadata: {str(e)}")
                    st.exception(e)

    else:
        # Load and parse metadata
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to parse as JSON first
            try:
                metadata = json.loads(content)
            except json.JSONDecodeError:
                # Fallback: parse as plain text
                metadata = {
                    "titles": [],
                    "description": content,
                    "hashtags": []
                }

            # Display Metadata
            st.markdown("### 📌 Title Options")

            if metadata.get("titles"):
                for i, title in enumerate(metadata["titles"], 1):
                    st.markdown(f"**{i}.**")
                    st.code(title, language=None)
            else:
                st.info("No titles generated")

            st.markdown("---")

            # Description
            st.markdown("### 📄 Description")

            description = metadata.get("description", "")
            if description:
                st.markdown("**Click the copy icon (top-right of box) to copy:**")
                st.code(description, language=None)

                with st.expander("✏️ Edit Description"):
                    edited_description = st.text_area(
                        "Video Description",
                        value=description,
                        height=200,
                        key="description_editor"
                    )

                    if edited_description != description:
                        if st.button("💾 Save Description", key="save_desc_btn"):
                            metadata["description"] = edited_description
                            with open(metadata_file, 'w', encoding='utf-8') as f:
                                json.dump(metadata, f, indent=2)
                            st.success("✅ Description saved!")
                            set_approval(project_name, "metadata", False)
                            st.rerun()
            else:
                st.info("No description generated")

            st.markdown("---")

            # Hashtags
            st.markdown("### #️⃣ Hashtags")

            if metadata.get("hashtags"):
                hashtags_str = " ".join(metadata["hashtags"])
                st.markdown(f"""
                <div style="
                    background-color: #f0f7ff;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    font-size: 1.1rem;
                ">
                    {hashtags_str}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No hashtags generated")

            st.markdown("---")

            # Regenerate Section
            col1, col2 = st.columns([4, 1])

            with col1:
                st.info("💡 Not satisfied with the metadata? Regenerate below")

            with col2:
                if st.button("🔄 Regenerate", key="regen_metadata_btn"):
                    log_container = st.empty()
                    with st.spinner("Regenerating metadata..."):
                        try:
                            with capture_stdout_to_streamlit(log_container, session_key="metadata_gen_log"):
                                generate_metadata(
                                    str(script_file),
                                    str(metadata_file)
                                )

                            set_approval(project_name, "metadata", False)
                            st.success("✅ Metadata regenerated!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

            st.markdown("---")

            # Process Log
            show_process_log("metadata_gen_log", "📋 Metadata Generation Log")

            # Approval Section
            st.markdown("## ✅ Approval")

            if is_approved:
                st.success("✅ **Metadata is approved**")

                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("❌ Revoke", key="revoke_approval_btn"):
                        set_approval(project_name, "metadata", False)
                        st.success("✅ Approval revoked")
                        st.rerun()

                with col2:
                    st.info("👉 Metadata is optional. You can proceed to **Images** page")

            else:
                st.warning("⚠️ **Metadata pending approval**")

                if st.button("✅ Approve Metadata", key="approve_metadata_btn", type="primary", use_container_width=True):
                    set_approval(project_name, "metadata", True)
                    st.success("✅ Metadata approved!")
                    st.balloons()
                    st.rerun()

        except Exception as e:
            st.error(f"❌ Error loading metadata: {str(e)}")


if __name__ == "__main__":
    main()
