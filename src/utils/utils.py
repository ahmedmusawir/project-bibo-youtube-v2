import tiktoken
from pathlib import Path

def count_words(text: str) -> int:
    """Return the number of words in the given text."""
    return len(text.split())

def count_tokens_openai(text: str, model: str = "gpt-4") -> int:
    """Return approximate token count using OpenAI's tiktoken."""
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def analyze_text_file(filepath: Path, model: str = "gpt-4") -> dict:
    """Reads a text file and returns word and token counts."""
    text = filepath.read_text(encoding='utf-8')
    return {
        "words": count_words(text),
        "tokens": count_tokens_openai(text, model)
    }
