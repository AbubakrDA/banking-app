from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    file_name: str
    file_size_bytes: int
    mime_type: str
    status: str
    is_quarantined: bool
    quarantine_reason: Optional[str] = None
    created_at: datetime


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    conversation_id: Optional[str] = None
    customer_id: Optional[str] = None
    file_name: str
    file_size_bytes: int
    mime_type: str
    status: str
    is_quarantined: bool
    quarantine_reason: Optional[str] = None
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    download_url: Optional[str] = None
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: List[DocumentRead]
    total: int
