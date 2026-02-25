"""
Chat route: POST /chat (question + tenant via API key).
"""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_tenant_id
from app.db.session import get_db
from app.db.repositories.tenant_repo import get_tenant_by_id
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services import guardrail_service, retrieval_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_db),
):
    """
    Ask a question about the tenant's documents. Requires X-API-Key (microsite sends it).
    Returns answer from RAG or fallback with contact info.
    """
    context_chunks = await retrieval_service.retrieve_context(
        session, tenant_id=tenant_id, question=body.question
    )
    tenant = await get_tenant_by_id(session, tenant_id)
    contact_email = tenant.contact_email if tenant else None
    answer = await guardrail_service.answer_with_guardrail(
        question=body.question,
        context_chunks=context_chunks,
        contact_email=contact_email,
    )
    return ChatResponse(answer=answer)
