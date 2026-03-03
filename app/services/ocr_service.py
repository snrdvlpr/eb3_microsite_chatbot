"""
OCR service: extract text from image-based documents (PDF, PPTX, images) using Tesseract.

This module is intentionally self-contained so you can swap out the OCR backend
later (e.g. Google Vision, AWS Textract) without touching ingestion_service.
"""
from __future__ import annotations

from typing import Optional

from app.utils.text_cleaning import clean_extracted_text


def _ocr_image(image) -> str:
    """Run Tesseract OCR on a single PIL.Image."""
    import pytesseract

    text = pytesseract.image_to_string(image)
    return clean_extracted_text(text)


def _ocr_pdf_bytes(data: bytes) -> str:
    """Render PDF pages to images and OCR each page."""
    from pdf2image import convert_from_bytes

    pages = convert_from_bytes(data)
    parts: list[str] = []
    for page in pages:
        t = _ocr_image(page)
        if t:
            parts.append(t)
    return "\n\n".join(parts).strip()


def _ocr_pptx_bytes(data: bytes) -> str:
    """
    OCR image content from a PPTX file given as bytes.

    Text-based shapes are already handled by the PPT parser; here we focus on
    picture shapes (e.g. scanned documents embedded as images).
    """
    import io

    from PIL import Image
    from pptx import Presentation  # type: ignore[import]

    prs = Presentation(io.BytesIO(data))
    parts: list[str] = []

    for slide in prs.slides:
        for shape in slide.shapes:
            image = getattr(shape, "image", None)
            if image is None:
                continue
            try:
                with Image.open(io.BytesIO(image.blob)) as img:
                    t = _ocr_image(img)
            except Exception:
                t = ""
            if t:
                parts.append(t)

    return "\n\n".join(parts).strip()


def extract_text_with_ocr(
    file_content: bytes,
    file_name: str,
    content_type: Optional[str] = None,
) -> str:
    """
    Dispatch OCR based on file type.

    - PDF: render pages to images and OCR each page.
    - PPTX/PPT: OCR picture shapes.
    - Other types: currently unsupported (returns empty string).
    """
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    if (content_type and "pdf" in content_type.lower()) or ext == "pdf":
        return _ocr_pdf_bytes(file_content)
    if ext in {"pptx", "ppt"}:
        return _ocr_pptx_bytes(file_content)
    # Fallback: no OCR for this type yet
    return ""

