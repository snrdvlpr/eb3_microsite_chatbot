"""Document repository: create, get by id, list by tenant, delete."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document


async def create_document(
    session: AsyncSession,
    tenant_id: UUID,
    file_name: str,
    storage_path: str,
) -> Document:
    doc = Document(
        tenant_id=tenant_id,
        file_name=file_name,
        storage_path=storage_path,
    )
    session.add(doc)
    await session.flush()
    return doc


async def get_document(
    session: AsyncSession, document_id: UUID, tenant_id: UUID
) -> Document | None:
    result = await session.execute(
        select(Document).where(
            Document.id == document_id,
            Document.tenant_id == tenant_id,
        )
    )
    return result.scalar_one_or_none()


async def list_documents(
    session: AsyncSession, tenant_id: UUID
) -> list[Document]:
    result = await session.execute(
        select(Document).where(Document.tenant_id == tenant_id).order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_document(
    session: AsyncSession, document_id: UUID, tenant_id: UUID
) -> bool:
    doc = await get_document(session, document_id, tenant_id)
    if not doc:
        return False
    await session.delete(doc)
    return True
