import re

def clean_text(text: str) -> str:
    """Lowercase + strip non-alphanumerics (but keep letters+digits)."""
    text = text.lower()
    return re.sub(r'[^a-z0-9\s]', '', text)

def extract_id(text: str) -> str:
    """
    Grabs the last whitespace‐separated token if it’s alphanumeric.
    E.g. “Get patient OBJC70912835” → “OBJC70912835”
    """
    parts = text.strip().split()
    if not parts:
        return None
    candidate = parts[-1]
    return candidate if re.fullmatch(r'[A-Za-z0-9]+', candidate) else None
