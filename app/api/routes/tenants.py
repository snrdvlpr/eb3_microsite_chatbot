"""
Tenant CRUD routes.

- List (GET /tenants) and Create (POST /tenants): admin-style, no auth.
- Get / Update / Delete "current" tenant: use X-API-Key; actions are by API key, not ID.
"""
from __future__ import annotations

import secrets
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_tenant_id
from app.db.repositories import tenant_repo
from app.db.session import get_db
from app.schemas.tenant_schema import TenantCreate, TenantOut, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["tenants"])


# ---- Admin-style: list all, create (no tenant auth) ----

@router.get("", response_model=list[TenantOut])
async def list_tenants(session: AsyncSession = Depends(get_db)) -> list[TenantOut]:
    """List all tenants. For admin/internal use."""
    tenants = await tenant_repo.list_tenants(session)
    return [TenantOut.model_validate(t) for t in tenants]


@router.post("", response_model=TenantOut, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    body: TenantCreate,
    session: AsyncSession = Depends(get_db),
) -> TenantOut:
    """Create a new tenant and API key. If api_key omitted, one is generated."""
    api_key = body.api_key or secrets.token_urlsafe(32)
    existing = await tenant_repo.get_tenant_by_api_key(session, api_key)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key already exists. Use another or omit to auto-generate.",
        )
    tenant = await tenant_repo.create_tenant(
        session=session,
        name=body.name,
        contact_email=body.contact_email,
        api_key=api_key,
    )
    return TenantOut.model_validate(tenant)


# ---- By API key (X-API-Key): get/update/delete current tenant ----

@router.get("/me", response_model=TenantOut)
async def get_current_tenant(
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_db),
) -> TenantOut:
    """Get the current tenant identified by X-API-Key."""
    tenant = await tenant_repo.get_tenant_by_id(session, tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")
    return TenantOut.model_validate(tenant)


@router.patch("/me", response_model=TenantOut)
async def update_current_tenant(
    body: TenantUpdate,
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_db),
) -> TenantOut:
    """
    Partially update the current tenant (identified by X-API-Key).

    PATCH: send only the fields you want to change (name, contact_email, api_key).
    Omitted fields are left unchanged.
    """
    if body.api_key is not None:
        existing = await tenant_repo.get_tenant_by_api_key(session, body.api_key)
        if existing and existing.id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key already in use by another tenant.",
            )
    tenant = await tenant_repo.update_tenant(
        session=session,
        tenant_id=tenant_id,
        name=body.name,
        contact_email=body.contact_email,
        api_key=body.api_key,
    )
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")
    return TenantOut.model_validate(tenant)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_tenant(
    tenant_id: UUID = Depends(get_tenant_id),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete the current tenant and all associated documents/chunks. Requires X-API-Key."""
    ok = await tenant_repo.delete_tenant(session, tenant_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found.")
