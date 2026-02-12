"""Centralized configuration management for model and voice selection."""
import json
from pathlib import Path

# Path traversal: src/utils/config.py -> src/utils -> src -> project_root -> config/models.json
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "models.json"


def get_model_config() -> dict:
    """Load the full model configuration from config/models.json."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_summarization_llm() -> str:
    """Get the currently selected LLM model for summarization tasks."""
    return get_model_config()["llm_summarization"]["current"]


def get_prompting_llm() -> str:
    """Get the currently selected LLM model for image prompting and metadata generation tasks."""
    return get_model_config()["llm_prompting"]["current"]


def get_current_voice() -> tuple[str, str]:
    """Get the currently selected TTS voice ID and language code.

    Returns:
        tuple[str, str]: (voice_id, language_code) e.g. ("en-US-Studio-O", "en-US")
    """
    config = get_model_config()["tts"]
    return config["current_voice"], config["current_lang"]


def get_current_image_model() -> str:
    """Get the currently selected image generation model."""
    return get_model_config()["image_gen"]["current"]


def save_model_config(config: dict) -> None:
    """Save updated configuration back to config/models.json.

    Args:
        config: The complete configuration dictionary to save.
    """
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
