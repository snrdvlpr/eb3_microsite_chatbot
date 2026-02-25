"""Chunk repository: insert chunks, similarity search (delegated to vector client), delete by document."""
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk


async def create_chunks(
    session: AsyncSession,
    tenant_id: UUID,
    document_id: UUID,
    chunks_with_embeddings: list[tuple[str, list[float]]],
) -> None:
    for text, embedding in chunks_with_embeddings:
        chunk = Chunk(
            tenant_id=tenant_id,
            document_id=document_id,
            chunk_text=text,
            embedding=embedding,
        )
        session.add(chunk)
    await session.flush()


async def delete_chunks_by_document(
    session: AsyncSession, document_id: UUID, tenant_id: UUID
) -> int:
    result = await session.execute(
        delete(Chunk).where(
            Chunk.document_id == document_id,
            Chunk.tenant_id == tenant_id,
        )
    )
    return result.rowcount or 0
