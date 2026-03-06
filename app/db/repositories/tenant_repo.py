"""Tenant repository: CRUD for tenants."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Tenant


async def get_tenant_by_id(session: AsyncSession, tenant_id: UUID) -> Tenant | None:
    result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
    return result.scalar_one_or_none()


async def get_tenant_by_api_key(session: AsyncSession, api_key: str) -> Tenant | None:
    result = await session.execute(select(Tenant).where(Tenant.api_key == api_key))
    return result.scalar_one_or_none()


async def list_tenants(session: AsyncSession) -> list[Tenant]:
    result = await session.execute(select(Tenant).order_by(Tenant.name.asc()))
    return list(result.scalars().all())


async def create_tenant(
    session: AsyncSession,
    name: str,
    contact_email: str | None,
    api_key: str,
) -> Tenant:
    tenant = Tenant(name=name, contact_email=contact_email, api_key=api_key)
    session.add(tenant)
    await session.flush()
    return tenant


async def update_tenant(
    session: AsyncSession,
    tenant_id: UUID,
    name: str | None = None,
    contact_email: str | None = None,
    api_key: str | None = None,
) -> Tenant | None:
    tenant = await get_tenant_by_id(session, tenant_id)
    if not tenant:
        return None
    if name is not None:
        tenant.name = name
    if contact_email is not None:
        tenant.contact_email = contact_email
    if api_key is not None:
        tenant.api_key = api_key
    await session.flush()
    return tenant


async def delete_tenant(session: AsyncSession, tenant_id: UUID) -> bool:
    tenant = await get_tenant_by_id(session, tenant_id)
    if not tenant:
        return False
    await session.delete(tenant)
    return True
