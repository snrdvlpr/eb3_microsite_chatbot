"""
Documents route: list documents for tenant.
"""
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_tenant_id
from app.db.session import get_db
from app.db.repositories.document_repo import list_documents

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentItem(BaseModel):
    id: UUID
    file_name: str
    created_at: str


@router.get("", response_model=list[DocumentItem])
async def list_docs(
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_db),
):
    """List documents for the tenant. Requires X-API-Key."""
    docs = await list_documents(session, tenant_id=tenant_id)
    return [
        DocumentItem(
            id=d.id,
            file_name=d.file_name,
            created_at=d.created_at.isoformat() if d.created_at else "",
        )
        for d in docs
    ]
