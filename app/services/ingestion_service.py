"""
Ingestion: store file in S3, extract text, chunk, embed, save to DB.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.repositories import chunk_repo, document_repo
from app.parsers.docx_parser import extract_text_from_docx_bytes
from app.parsers.excel_parser import extract_text_from_excel_bytes
from app.parsers.pdf_parser import extract_text_from_pdf_bytes
from app.parsers.ppt_parser import extract_text_from_pptx_bytes
from app.services import embedding_service
from app.services.ocr_service import extract_text_with_ocr
from app.storage.s3_client import upload_file
from app.utils.chunking import chunk_text
from app.utils.text_cleaning import clean_extracted_text


def extract_cleaned_text(
    file_name: str,
    file_content: bytes,
    content_type: Optional[str] = None,
) -> str:
    """
    Extract text from the uploaded file (PDF/DOCX/XLSX/PPTX/etc.),
    run cleaning and OCR if needed, and return the final cleaned text.

    Raises ValueError if no usable text can be extracted.
    """
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""

    # Primary extraction based on type
    if (content_type and "pdf" in content_type.lower()) or ext == "pdf":
        raw_text = extract_text_from_pdf_bytes(file_content)
    elif ext in {"docx"}:
        raw_text = extract_text_from_docx_bytes(file_content)
    elif ext in {"xlsx", "xls"}:
        raw_text = extract_text_from_excel_bytes(file_content)
    elif ext in {"pptx", "ppt"}:
        raw_text = extract_text_from_pptx_bytes(file_content)
    else:
        # Fallback: treat as UTF-8 text
        raw_text = file_content.decode("utf-8", errors="replace")

    text = clean_extracted_text(raw_text)
    cleaned = text.strip()

    # If little or no text, attempt OCR for supported types (e.g. image-based PDFs/PPTX)
    if not cleaned or len(cleaned) < 50:
        ocr_text = extract_text_with_ocr(
            file_content=file_content,
            file_name=file_name,
            content_type=content_type,
        )
        ocr_text = clean_extracted_text(ocr_text)
        cleaned = ocr_text.strip()

    if not cleaned:
        raise ValueError(
            "No text could be extracted from the document, even with OCR. "
            "It may be purely image-based or an unsupported format."
        )

    return cleaned


async def process_document_content(
    tenant_id: UUID,
    document_id: UUID,
    file_name: str,
    file_content: bytes,
    content_type: str | None,
    session: AsyncSession,
) -> None:
    """
    Heavy part of ingestion: extract, chunk, embed, and save chunks.
    Assumes the file is already stored and a Document row already exists.
    """
    # Extract and clean text (includes OCR if needed)
    cleaned = extract_cleaned_text(
        file_name=file_name,
        file_content=file_content,
        content_type=content_type,
    )

    # Chunk
    chunks_list = chunk_text(cleaned)

    # Embed
    embeddings = await embedding_service.embed_texts(chunks_list)

    # Save chunks with embeddings
    chunks_with_embeddings = list(zip(chunks_list, embeddings))
    await chunk_repo.create_chunks(
        session,
        tenant_id=tenant_id,
        document_id=document_id,
        chunks_with_embeddings=chunks_with_embeddings,
    )


async def ingest_document(
    tenant_id: UUID,
    file_name: str,
    file_content: bytes,
    content_type: str | None,
    session: AsyncSession,
) -> UUID:
    """
    Upload file to storage, extract text, chunk, embed, save document + chunks.
    Returns document_id.
    """
    settings = get_settings()
    bucket = settings.s3_bucket
    storage_path = f"{tenant_id}/{file_name}"

    # 1. Store file
    await upload_file(
        bucket=bucket,
        key=storage_path,
        body=file_content,
        content_type=content_type,
    )

    # 2. Save document row
    doc = await document_repo.create_document(
        session, tenant_id=tenant_id, file_name=file_name, storage_path=storage_path
    )
    document_id = doc.id

    # 3. Process content (extract, chunk, embed, save chunks)
    await process_document_content(
        tenant_id=tenant_id,
        document_id=document_id,
        file_name=file_name,
        file_content=file_content,
        content_type=content_type,
        session=session,
    )

    return document_id
