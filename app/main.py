"""
EB3 Microsite Chatbot — RAG API for employee benefits Q&A.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import chat, documents, tenants, upload
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import get_db, init_db

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # shutdown if needed


app = FastAPI(
    title=get_settings().app_name,
    description="RAG API: upload documents, ask questions. Multi-tenant via API key.",
    lifespan=lifespan,
)

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(tenants.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
