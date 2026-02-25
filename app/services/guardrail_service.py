"""
Guardrail: answer only from context; if empty or irrelevant, return fallback with contact.
"""
from app.services.llm_service import complete, load_prompt_template


def build_qa_system_prompt(contact_email: str | None) -> str:
    """System prompt for Q&A from template; only use context, fallback to contact."""
    contact = contact_email or "your benefits administrator"
    try:
        template = load_prompt_template("qa_prompt.txt")
        return template.format(contact_email=contact)
    except Exception:
        return (
            f"You are an employee benefits assistant. Only use the provided context. "
            f"If information is not in the context, say so and tell the user to contact: {contact}."
        )


async def answer_with_guardrail(
    question: str,
    context_chunks: list[str],
    contact_email: str | None,
) -> str:
    """
    If context is empty or too small, return fallback with contact.
    Otherwise call LLM with context and return answer.
    """
    if not context_chunks or not any(c.strip() for c in context_chunks):
        contact = contact_email or "your benefits administrator"
        return (
            "The requested information is not available in the provided documents. "
            f"Please contact {contact} for assistance."
        )
    system = build_qa_system_prompt(contact_email)
    context = "\n\n---\n\n".join(context_chunks)
    user_content = f"Context:\n{context}\n\nQuestion:\n{question}"
    return await complete(system_content=system, user_content=user_content)
