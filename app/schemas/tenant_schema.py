"""Tenant API schemas."""
from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class TenantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr | None = None


class TenantCreate(TenantBase):
    api_key: str | None = Field(
        default=None,
        description="Optional API key. If omitted, the server will generate one.",
    )


class TenantUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    contact_email: str | None = Field(default=None, max_length=255)
    api_key: str | None = Field(default=None, max_length=255)


class TenantOut(TenantBase):
    id: UUID
    api_key: str

    class Config:
        from_attributes = True