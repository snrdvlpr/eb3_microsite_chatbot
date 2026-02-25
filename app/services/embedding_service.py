"""
Embedding service: call OpenAI-compatible embeddings API.
"""
from openai import AsyncOpenAI

from app.core.config import get_settings


def get_embedding_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(**settings.llm_client_kwargs())


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return list of embedding vectors for the given texts."""
    if not texts:
        return []
    settings = get_settings()
    client = get_embedding_client()
    response = await client.embeddings.create(
        input=texts,
        model=settings.embedding_model,
    )
    return [item.embedding for item in response.data]


async def embed_single(text: str) -> list[float]:
    """Embed one string. Returns the embedding vector."""
    vectors = await embed_texts([text])
    return vectors[0] if vectors else []
