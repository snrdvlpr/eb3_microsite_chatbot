"""Upload API schemas."""
from uuid import UUID

from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: UUID
    file_name: str
    message: str = "Document uploaded and indexed."


class UploadPreviewResponse(BaseModel):
    file_name: str
    length: int  # number of characters in the parsed text
    text: str    # full parsed/cleaned text
