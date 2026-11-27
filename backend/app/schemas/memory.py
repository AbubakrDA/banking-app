from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class MemoryCreate(BaseModel):
    customer_id: str
    conversation_id: Optional[str] = None
    memory_type: Literal["working", "episodic", "semantic"] = Field(
        description="Memory tier: working (session/temporary), episodic (event history), semantic (stable preferences)"
    )
    key: str = Field(min_length=1, max_length=128, description="Identifier for this memory item (e.g. preferred_time, allergy)")
    value: str = Field(min_length=1, description="Fact, interaction record, or preference content")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    provenance: Optional[Dict[str, Any]] = Field(default_factory=dict)
    expires_at: Optional[datetime] = None


class MemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    customer_id: str
    conversation_id: Optional[str] = None
    memory_type: str
    key: str
    value: str
    confidence_score: float
    provenance: Dict[str, Any]
    expires_at: Optional[datetime] = None
    is_flagged: bool
    flag_reason: Optional[str] = None
    is_active: bool
    created_at: datetime


class CustomerMemoryContextResponse(BaseModel):
    customer_id: str
    tenant_id: str
    working_memory: Dict[str, str]
    episodic_memory: List[Dict[str, Any]]
    semantic_memory: Dict[str, str]
    formatted_context_envelope: str
    total_memories: int


class MemoryPurgeResponse(BaseModel):
    customer_id: str
    tenant_id: str
    purged_count: int
    purged_at: datetime
