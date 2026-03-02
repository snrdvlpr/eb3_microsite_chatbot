"""
FastAPI dependencies: DB session, tenant from API key.
"""
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_tenant_id_for_request
from app.db.session import get_db


async def get_tenant_id(
    session: AsyncSession = Depends(get_db),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
) -> UUID:
    """Resolve tenant UUID from API key. Use for upload and document routes."""
    tenant_id_str = await get_tenant_id_for_request(
        session, x_api_key=x_api_key
    )
    return UUID(tenant_id_str)
