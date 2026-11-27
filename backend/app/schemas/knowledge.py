from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = True


class CollectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    is_public: bool
    created_at: datetime


class KBDocumentCreate(BaseModel):
    collection_id: str
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=10, description="Raw document text to be chunked and indexed")
    source_type: str = Field(default="manual_entry")
    source_url: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class KBChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chunk_index: int
    content: str
    token_count: int
    chunk_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class KBDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    collection_id: str
    title: str
    source_type: str
    source_url: Optional[str] = None
    version: int
    status: str
    chunk_count: int
    doc_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    chunks: Optional[List[KBChunkRead]] = Field(default_factory=list)
    created_at: datetime


class RAGQueryRequest(BaseModel):
    query: str = Field(min_length=2, description="User search query")
    collection_ids: Optional[List[str]] = Field(default=None, description="Optional collection IDs to filter")
    top_k: int = Field(default=5, ge=1, le=20)
    alpha: float = Field(default=0.7, ge=0.0, le=1.0, description="Balance between vector (1.0) and keyword (0.0)")


class RAGSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    collection_name: str
    content: str
    score: float
    sources: Dict[str, Any]


class RAGQueryResponse(BaseModel):
    query: str
    results: List[RAGSearchResult]
    total_matched: int
