"""
Upload routes: POST /upload (store + enqueue indexing) and POST /upload/preview (parse-only).
"""
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_tenant_id
from app.core.config import get_settings
from app.db.repositories import document_repo
from app.db.session import async_session_factory, get_db
from app.schemas.upload_schema import UploadPreviewResponse, UploadResponse
from app.services.ingestion_service import (
    extract_cleaned_text,
    process_document_content,
)
from app.storage.s3_client import upload_file

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
):
    """
    Upload a document. Requires X-API-Key.

    Short-term optimization:
    - Store file and create Document row within the request.
    - Kick off heavy parsing/embedding in a background task.
    - Return immediately with document_id.
    """
    if not file.filename:
        raise HTTPException(400, detail="Missing filename")
    content = await file.read()
    if not content:
        raise HTTPException(400, detail="Empty file")
    content_type = file.content_type or ""

    # 1. Store file
    settings = get_settings()
    bucket = settings.s3_bucket
    storage_path = f"{tenant_id}/{file.filename}"
    await upload_file(
        bucket=bucket,
        key=storage_path,
        body=content,
        content_type=content_type,
    )

    # 2. Create document row
    doc = await document_repo.create_document(
        session,
        tenant_id=tenant_id,
        file_name=file.filename,
        storage_path=storage_path,
    )
    document_id = doc.id

    # 3. Enqueue heavy ingestion work in the background
    async def run_ingestion_task(
        tenant: UUID,
        document: UUID,
        file_name: str,
        file_bytes: bytes,
        ctype: str | None,
    ) -> None:
        async with async_session_factory() as bg_session:
            try:
                await process_document_content(
                    tenant_id=tenant,
                    document_id=document,
                    file_name=file_name,
                    file_content=file_bytes,
                    content_type=ctype,
                    session=bg_session,
                )
                await bg_session.commit()
            except Exception:
                await bg_session.rollback()
                # In a real system, log the error or update a status field on the document

    background_tasks.add_task(
        run_ingestion_task,
        tenant_id,
        document_id,
        file.filename,
        content,
        content_type,
    )

    return UploadResponse(
        document_id=document_id,
        file_name=file.filename,
        message="Document stored and indexing has been queued.",
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
