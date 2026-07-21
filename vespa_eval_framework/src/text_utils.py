import re
import unicodedata


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return text

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text
