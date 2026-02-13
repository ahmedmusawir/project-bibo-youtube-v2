"""
Configuration utilities for model and voice selection across the pipeline.
Reads from config/config.json to enable easy model swapping in Streamlit UI.
"""
import json
from pathlib import Path
from typing import Dict, List, Any


def get_config_path() -> Path:
    """Get the path to config.json config file."""
    # Find project root (where main.py lives)
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "main.py").exists():
            return current / "config" / "config.json"
        current = current.parent
    # Fallback
    return Path("config/config.json")


def load_config() -> Dict[str, Any]:
    """Load the pipeline configuration from config.json."""
    config_path = get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config: Dict[str, Any]) -> None:
    """Save the pipeline configuration to config.json."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ===== LLM SUMMARIZATION =====

def get_summarization_llm() -> str:
    """Get the current summarization LLM model name."""
    config = load_config()
    return config["llm_summarization"]["current"]


def get_available_summarization_llms() -> List[str]:
    """Get list of available summarization LLM models."""
    config = load_config()
    return config["llm_summarization"]["available"]


def set_summarization_llm(model: str) -> None:
    """Set the current summarization LLM model."""
    config = load_config()
    if model not in config["llm_summarization"]["available"]:
        raise ValueError(f"Model {model} not in available list")
    config["llm_summarization"]["current"] = model
    save_config(config)


# ===== LLM PROMPTING =====

def get_prompting_llm() -> str:
    """Get the current prompting LLM model name (for image prompts, metadata)."""
    config = load_config()
    return config["llm_prompting"]["current"]


def get_available_prompting_llms() -> List[str]:
    """Get list of available prompting LLM models."""
    config = load_config()
    return config["llm_prompting"]["available"]


def set_prompting_llm(model: str) -> None:
    """Set the current prompting LLM model."""
    config = load_config()
    if model not in config["llm_prompting"]["available"]:
        raise ValueError(f"Model {model} not in available list")
    config["llm_prompting"]["current"] = model
    save_config(config)


# ===== TEXT-TO-SPEECH =====

def get_tts_voice() -> str:
    """Get the current TTS voice ID."""
    config = load_config()
    return config["tts"]["current_voice"]


def get_tts_lang() -> str:
    """Get the current TTS language code."""
    config = load_config()
    return config["tts"]["current_lang"]


def get_available_tts_voices() -> List[Dict[str, str]]:
    """Get list of available TTS voices with metadata."""
    config = load_config()
    return config["tts"]["available"]


def set_tts_voice(voice_id: str, lang: str = None) -> None:
    """Set the current TTS voice and optionally language."""
    config = load_config()

    # Validate voice exists
    available = config["tts"]["available"]
    voice_ids = [v["id"] for v in available]
    if voice_id not in voice_ids:
        raise ValueError(f"Voice {voice_id} not in available list")

    config["tts"]["current_voice"] = voice_id

    # Auto-detect language from voice if not provided
    if lang is None:
        for voice in available:
            if voice["id"] == voice_id:
                lang = voice["lang"]
                break

    if lang:
        config["tts"]["current_lang"] = lang

    save_config(config)


# ===== IMAGE GENERATION =====

def get_image_gen_model() -> str:
    """Get the current image generation model."""
    config = load_config()
    return config["image_gen"]["current"]


def get_available_image_gen_models() -> List[str]:
    """Get list of available image generation models."""
    config = load_config()
    return config["image_gen"]["available"]


def set_image_gen_model(model: str) -> None:
    """Set the current image generation model."""
    config = load_config()
    if model not in config["image_gen"]["available"]:
        raise ValueError(f"Model {model} not in available list")
    config["image_gen"]["current"] = model
    save_config(config)


# ===== CONVENIENCE FUNCTIONS =====

def get_all_current_models() -> Dict[str, str]:
    """Get all currently selected models in one dict."""
    config = load_config()
    return {
        "summarization_llm": config["llm_summarization"]["current"],
        "prompting_llm": config["llm_prompting"]["current"],
        "tts_voice": config["tts"]["current_voice"],
        "tts_lang": config["tts"]["current_lang"],
        "image_gen": config["image_gen"]["current"],
    }


def print_current_config() -> None:
    """Print the current configuration (useful for debugging)."""
    current = get_all_current_models()
    print("\n" + "="*60)
    print("CURRENT MODEL CONFIGURATION")
    print("="*60)
    print(f"Summarization LLM:  {current['summarization_llm']}")
    print(f"Prompting LLM:      {current['prompting_llm']}")
    print(f"TTS Voice:          {current['tts_voice']} ({current['tts_lang']})")
    print(f"Image Generation:   {current['image_gen']}")
    print("="*60 + "\n")
