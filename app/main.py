"""
VidGen Streamlit App - Main Entry Point
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from app.components.sidebar import render_sidebar


# Page configuration
st.set_page_config(
    page_title="VidGen - YouTube Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        color: #FF6B35;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    /* Section headers */
    .section-header {
        color: #FF6B35;
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    /* Status badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: 600;
        font-size: 0.875rem;
    }

    .status-ready {
        background-color: #10B981;
        color: white;
    }

    .status-pending {
        background-color: #F59E0B;
        color: white;
    }

    .status-missing {
        background-color: #6B7280;
        color: white;
    }

    /* Button styling */
    .stButton > button {
        background-color: #FF6B35;
        color: white;
        font-weight: 600;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 2rem;
    }

    .stButton > button:hover {
        background-color: #E85A24;
    }
</style>
""", unsafe_allow_html=True)

# Render sidebar
render_sidebar()

# Main content area
def main():
    """Main app content."""

    # Check if project is selected
    if not st.session_state.get("current_project"):
        st.markdown('<p class="main-title">🎬 Welcome to VidGen</p>', unsafe_allow_html=True)
        st.markdown("""
        ### Get Started

        VidGen helps you create professional YouTube videos automatically:

        1. **📝 Input:** Paste text or YouTube URL
        2. **📄 Script:** AI generates engaging script
        3. **🎵 Audio:** Text-to-speech narration
        4. **📋 Metadata:** Titles, descriptions, hashtags
        5. **🖼️ Images:** AI-generated visuals
        6. **🎬 Video:** Final video assembly

        👈 **Create a new project in the sidebar to begin!**
        """)
        return

    # Show current project
    project_name = st.session_state.current_project
    st.markdown(f'<p class="main-title">Project: {project_name}</p>', unsafe_allow_html=True)

    # Instructions
    st.info("👈 Use the sidebar to navigate between pipeline stages")

    # Quick status overview
    from app.state import get_all_stages_status

    st.markdown('<p class="section-header">Pipeline Status</p>', unsafe_allow_html=True)

    stages_status = get_all_stages_status(project_name)

    cols = st.columns(5)
    stage_info = [
        ("script", "📄 Script", cols[0]),
        ("audio", "🎵 Audio", cols[1]),
        ("metadata", "📋 Metadata", cols[2]),
        ("images", "🖼️ Images", cols[3]),
        ("video", "🎬 Video", cols[4])
    ]

    for stage_key, label, col in stage_info:
        status = stages_status[stage_key]
        with col:
            st.markdown(f"**{label}**")
            if status["approved"]:
                st.success("✅ Approved")
            elif status["exists"]:
                st.warning("⚠️ Pending")
            else:
                st.info("⭕ Not Started")


if __name__ == "__main__":
    main()
