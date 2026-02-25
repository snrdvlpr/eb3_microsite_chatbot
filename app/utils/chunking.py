"""
Chunking with overlap for RAG. Keeps semantic boundaries where possible.
"""
from app.core.config import get_settings


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[str]:
    """
    Split text into chunks with overlap. Prefer splitting on paragraph/sentence.
    """
    settings = get_settings()
    size = chunk_size if chunk_size is not None else settings.chunk_size
    overlap = chunk_overlap if chunk_overlap is not None else settings.chunk_overlap
    if not text or not text.strip():
        return []
    text = text.strip()
    if len(text) <= size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + size
        if end >= len(text):
            chunks.append(text[start:].strip())
            break
        # Prefer break at newline or sentence end
        segment = text[start:end]
        break_at = -1
        for sep in ("\n\n", "\n", ". "):
            idx = segment.rfind(sep)
            if idx > size // 2:
                break_at = idx + len(sep)
                break
        if break_at > 0:
            chunk = text[start : start + break_at].strip()
            start = start + break_at - overlap
        else:
            chunk = segment.strip()
            start = end - overlap
        if chunk:
            chunks.append(chunk)
    return [c for c in chunks if c]
