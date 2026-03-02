"""
pgvector similarity search. Encapsulates all vector SQL; services use this only.
"""
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings


def _vector_to_str(embedding: list[float]) -> str:
    """PostgreSQL vector type accepts string like '[0.1, 0.2, ...]'."""
    return "[" + ",".join(str(x) for x in embedding) + "]"


async def search_similar_chunks(
    session: AsyncSession,
    tenant_id: UUID,
    query_embedding: list[float],
    top_k: int | None = None,
) -> list[tuple[UUID, str]]:
    """
    Returns list of (chunk_id, chunk_text) for the tenant, ordered by cosine similarity.
    """
    settings = get_settings()
    k = top_k if top_k is not None else settings.retrieval_top_k
    # pgvector cosine distance: <=> ; we want smallest distance = most similar
    # CAST avoids :embedding::vector being parsed as two bind params (:embedding and :vector)
    sql = text("""
        SELECT id, chunk_text
        FROM chunks
        WHERE tenant_id = :tenant_id
          AND embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :k
    """)
    result = await session.execute(
        sql,
        {
            "tenant_id": str(tenant_id),
            "embedding": _vector_to_str(query_embedding),
            "k": k,
        },
    )
    rows = result.fetchall()
    # row[0] may be asyncpg.pgproto.UUID; convert via str for Python uuid.UUID
    return [(UUID(str(row[0])), row[1]) for row in rows]
