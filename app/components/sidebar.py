"""
Sidebar component for project selection and navigation.
"""
import streamlit as st
from app.state import list_projects, create_project, get_all_stages_status


def render_sidebar():
    """Render the sidebar with project selector and navigation."""
    with st.sidebar:
        st.title("🎬 VidGen")

        # Project Selection Section
        st.markdown("---")
        st.subheader("Project")

        # List existing projects
        projects = list_projects()

        # Project selector
        if projects:
            # Use current_project from session_state as source of truth
            if "current_project" not in st.session_state or st.session_state.current_project not in projects:
                st.session_state.current_project = projects[0]

            current_index = projects.index(st.session_state.current_project)

            selected_project = st.selectbox(
                "Select Project",
                projects,
                index=current_index,
                key="project_selector"
            )

            # Update session state if user changed selection
            if selected_project != st.session_state.current_project:
                st.session_state.current_project = selected_project
                st.rerun()
        else:
            st.info("No projects yet. Create one below!")
            selected_project = None
            st.session_state.current_project = None

        # Show success toast after project creation
        if st.session_state.get("_project_created"):
            st.success(f"✅ Project '{st.session_state._project_created}' created!")
            del st.session_state["_project_created"]

        # New Project Input
        with st.expander("➕ Create New Project"):
            new_project_name = st.text_input(
                "Project Name",
                placeholder="e.g., BBC_Robots",
                key="new_project_input"
            )

            if st.button("Create Project", key="create_project_btn"):
                if new_project_name and new_project_name.strip():
                    try:
                        create_project(new_project_name.strip())
                        st.session_state.current_project = new_project_name.strip()
                        st.session_state["_project_created"] = new_project_name.strip()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to create project: {e}")
                        st.code(str(e))
                else:
                    st.error("Please enter a project name")

        # Navigation Section
        if st.session_state.get("current_project"):
            st.markdown("---")
            st.subheader("Pipeline")

            # Get stage status
            project_name = st.session_state.current_project
            stages_status = get_all_stages_status(project_name)

            # Define stages with icons
            stages = [
                ("1_inputs", "📝 Inputs", None),  # No status for inputs
                ("2_script", "📄 Script", "script"),
                ("3_audio", "🎵 Audio", "audio"),
                ("4_metadata", "📋 Metadata", "metadata"),
                ("5_images", "🖼️ Images", "images"),
                ("6_video", "🎬 Video", "video")
            ]

            # Render navigation buttons
            for page_key, label, status_key in stages:
                if status_key:
                    status = stages_status[status_key]
                    if status["approved"]:
                        icon = "✅"
                    elif status["exists"]:
                        icon = "⚠️"  # Generated but not approved
                    else:
                        icon = "⭕"  # Not generated yet
                    full_label = f"{icon} {label}"
                else:
                    full_label = label

                # Navigation is handled by Streamlit's built-in page routing
                st.markdown(f"**{full_label}**")

        # Footer
        st.markdown("---")
        st.caption("VidGen v2.0")
