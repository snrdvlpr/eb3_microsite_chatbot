"""Upload API schemas."""
from uuid import UUID

from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: UUID
    file_name: str
    message: str = "Document uploaded and indexed."
