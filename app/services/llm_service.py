"""
LLM service: build prompt from template, call OpenAI-compatible chat API.
"""
from pathlib import Path

from openai import AsyncOpenAI

from app.core.config import get_settings


def get_llm_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(**settings.llm_client_kwargs())


def load_prompt_template(name: str) -> str:
    """Load prompt from app/prompts/{name}.txt."""
    base = Path(__file__).resolve().parent.parent
    path = base / "prompts" / name
    return path.read_text(encoding="utf-8")


async def complete(
    system_content: str,
    user_content: str,
    max_tokens: int | None = None,
) -> str:
    """Single turn completion. Returns assistant message content."""
    settings = get_settings()
    client = get_llm_client()
    tokens = max_tokens if max_tokens is not None else settings.max_tokens
    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        max_tokens=tokens,
    )
    msg = response.choices[0].message
    return msg.content or ""
