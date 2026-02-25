"""
Tenant resolution via API key.
Every request that needs tenant context must pass X-API-Key (or Authorization: Bearer <key>).
"""
from typing import Annotated

from fastapi import Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Tenant


async def get_tenant_from_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> str | None:
    """
    Returns raw API key if present (from X-API-Key or Bearer token).
    Does not validate; use with get_tenant_for_request when DB is available.
    """
    if x_api_key:
        return x_api_key.strip()
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


async def get_tenant_id_for_request(
    session: AsyncSession,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    """
    Resolve tenant_id from API key. Raises 401 if missing or invalid.
    """
    key = await get_tenant_from_api_key(x_api_key=x_api_key, authorization=authorization)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header or Authorization: Bearer <key>.",
        )
    result = await session.execute(
        select(Tenant.id).where(Tenant.api_key == key)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    return str(row)
