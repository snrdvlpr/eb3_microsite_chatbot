"""
PDF text extraction for benefit booklets, certificates, SPDs.
"""
from pathlib import Path
from typing import Optional

import pdfplumber


def extract_text_from_pdf(file_path: str | Path) -> str:
    """Extract raw text from PDF. Uses pdfplumber for better table/text handling."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    texts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texts.append(t)
    return "\n\n".join(texts) if texts else ""


def extract_text_from_pdf_bytes(data: bytes) -> str:
    """Extract text from PDF given as bytes (e.g. from upload)."""
    import io
    texts: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                texts.append(t)
    return "\n\n".join(texts) if texts else ""
