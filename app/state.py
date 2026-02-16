"""
Simple state management for project approvals.
Reads/writes projects/{name}/config.json for approval tracking.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent


def get_project_path(project_name: str) -> Path:
    """Get the path to a project directory."""
    return get_project_root() / "projects" / project_name


def get_project_config_path(project_name: str) -> Path:
    """Get the path to a project's config.json."""
    return get_project_path(project_name) / "config.json"


def project_exists(project_name: str) -> bool:
    """Check if a project directory exists."""
    return get_project_path(project_name).exists()


def list_projects() -> list[str]:
    """List all project names."""
    projects_dir = get_project_root() / "projects"
    if not projects_dir.exists():
        return []
    return sorted([p.name for p in projects_dir.iterdir() if p.is_dir()])


def create_project(project_name: str) -> None:
    """Create a new project directory with default config."""
    project_path = get_project_path(project_name)
    project_path.mkdir(parents=True, exist_ok=True)

    # Create default config.json
    default_config = {
        "project_name": project_name,
        "approvals": {
            "script": False,
            "audio": False,
            "metadata": False,
            "images": False,
            "video": False
        }
    }

    config_path = get_project_config_path(project_name)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2)


def load_project_config(project_name: str) -> Dict[str, Any]:
    """Load a project's config.json."""
    config_path = get_project_config_path(project_name)

    if not config_path.exists():
        # Return default if config doesn't exist
        return {
            "project_name": project_name,
            "approvals": {
                "script": False,
                "audio": False,
                "metadata": False,
                "images": False,
                "video": False
            }
        }

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_project_config(project_name: str, config: Dict[str, Any]) -> None:
    """Save a project's config.json."""
    config_path = get_project_config_path(project_name)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)


def get_approval_status(project_name: str, stage: str) -> bool:
    """Check if a stage is approved."""
    config = load_project_config(project_name)
    return config.get("approvals", {}).get(stage, False)


def set_approval(project_name: str, stage: str, approved: bool) -> None:
    """Set approval status for a stage."""
    config = load_project_config(project_name)

    if "approvals" not in config:
        config["approvals"] = {}

    config["approvals"][stage] = approved
    save_project_config(project_name, config)


def stage_file_exists(project_name: str, stage: str) -> bool:
    """Check if a stage's output file exists."""
    project_path = get_project_path(project_name)

    # Map stages to their output files
    stage_files = {
        "script": "1_summary.txt",
        "audio": "2_audio.mp3",
        "metadata": "4_metadata.json",
        "images": "5_images",  # Directory
        "video": "6_final_video.mp4"
    }

    if stage not in stage_files:
        return False

    file_path = project_path / stage_files[stage]

    # For images, check if directory exists and has files
    if stage == "images":
        return file_path.exists() and any(file_path.iterdir())

    return file_path.exists()


def get_stage_status(project_name: str, stage: str) -> Dict[str, Any]:
    """Get complete status of a stage (exists + approved)."""
    return {
        "exists": stage_file_exists(project_name, stage),
        "approved": get_approval_status(project_name, stage)
    }


def get_all_stages_status(project_name: str) -> Dict[str, Dict[str, Any]]:
    """Get status of all stages."""
    stages = ["script", "audio", "metadata", "images", "video"]
    return {stage: get_stage_status(project_name, stage) for stage in stages}
