"""
Retrieval: embed question, vector search, return context strings.
"""
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import embedding_service
from app.vector.pgvector_client import search_similar_chunks


async def retrieve_context(
    session: AsyncSession,
    tenant_id: UUID,
    question: str,
    top_k: int | None = None,
) -> list[str]:
    """Get relevant chunk texts for the question (for RAG context)."""
    query_embedding = await embedding_service.embed_single(question)
    pairs = await search_similar_chunks(
        session, tenant_id=tenant_id, query_embedding=query_embedding, top_k=top_k
    )
    return [text for _, text in pairs]
