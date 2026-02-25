"""
Environment and app configuration.
Supports OpenAI (dev) and vLLM (prod) via same client with base_url + model.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "eb3-microsite-chatbot"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/eb3chatbot"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/eb3chatbot"

    # LLM (OpenAI-compatible: OpenAI or vLLM)
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None  # set for vLLM, e.g. http://vllm:8000/v1
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    max_tokens: int = 1024

    # RAG
    chunk_size: int = 800
    chunk_overlap: int = 100
    retrieval_top_k: int = 5

    # S3
    s3_bucket: str = "eb3-documents"
    s3_region: str = "us-east-1"
    s3_endpoint_url: Optional[str] = None  # for MinIO/local
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    use_local_storage: bool = False  # True = store under ./local_storage (no S3 needed)

    def llm_client_kwargs(self) -> dict:
        """Kwargs for OpenAI client: works with OpenAI and vLLM."""
        d: dict = {"api_key": self.openai_api_key or "not-set"}
        if self.openai_base_url:
            d["base_url"] = self.openai_base_url
        return d


@lru_cache
def get_settings() -> Settings:
    return Settings()
