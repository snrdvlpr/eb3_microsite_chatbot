"""
Text cleaning for PDF artifacts and noisy content.
"""
import re


def clean_extracted_text(text: str) -> str:
    """Remove common PDF junk: excess whitespace, repeated headers/footers."""
    if not text:
        return ""
    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text
