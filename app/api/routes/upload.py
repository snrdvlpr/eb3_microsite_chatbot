"""
Upload routes: POST /upload (store+index) and POST /upload/preview (parse-only).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_tenant_id
from app.db.session import get_db
from app.schemas.upload_schema import UploadPreviewResponse, UploadResponse
from app.services.ingestion_service import extract_cleaned_text, ingest_document

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def upload_document(
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
):
    """Upload a document. Requires X-API-Key. File is stored and indexed for RAG."""
    if not file.filename:
        raise HTTPException(400, detail="Missing filename")
    content = await file.read()
    if not content:
        raise HTTPException(400, detail="Empty file")
    content_type = file.content_type or ""
    try:
        document_id = await ingest_document(
            tenant_id=tenant_id,
            file_name=file.filename,
            file_content=content,
            content_type=content_type,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return UploadResponse(
        document_id=document_id,
        file_name=file.filename,
    )


@router.post("/preview", response_model=UploadPreviewResponse)
async def preview_document(
    tenant_id: UUID = Depends(get_tenant_id),
    file: UploadFile = File(...),
):
    """
    Preview how a document will be parsed.
    Does NOT store the file or write to the database.
    Returns the parsed text and its length.
    """
    if not file.filename:
        raise HTTPException(400, detail="Missing filename")
    content = await file.read()
    if not content:
        raise HTTPException(400, detail="Empty file")
    content_type = file.content_type or ""
    try:
        text = extract_cleaned_text(
            file_name=file.filename,
            file_content=content,
            content_type=content_type,
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return UploadPreviewResponse(
        file_name=file.filename,
        length=len(text),
        text=text,
    )
