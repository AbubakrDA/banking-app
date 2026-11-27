from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class TicketNoteCreate(BaseModel):
    content: str = Field(min_length=1, description="Note or reply text")
    note_type: Literal["internal", "customer_reply"] = Field(
        default="internal",
        description="internal (staff only) or customer_reply",
    )


class TicketNoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    user_id: Optional[str] = None
    author_name: str
    note_type: str
    content: str
    created_at: datetime


class FeedbackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    customer_id: str
    channel: str
    token: str
    expires_at: datetime
    rating: Optional[int] = None
    was_resolved: Optional[bool] = None
    comment: Optional[str] = None
    submitted_at: Optional[datetime] = None


class TicketCreate(BaseModel):
    customer_id: str
    conversation_id: Optional[str] = None
    subject: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=5)
    category: Optional[str] = None  # Auto-classified if omitted
    priority: Optional[str] = None  # Auto-classified if omitted
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TicketStatusUpdate(BaseModel):
    status: Literal[
        "new",
        "categorized",
        "assigned",
        "in_progress",
        "waiting_customer",
        "escalated",
        "resolved",
        "closed",
    ]
    reason: Optional[str] = None


class TicketAssignUpdate(BaseModel):
    assigned_user_id: str


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    customer_id: str
    conversation_id: Optional[str] = None
    ticket_number: str
    subject: str
    description: str
    category: str
    priority: str
    status: str
    assigned_user_id: Optional[str] = None
    sla_due_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    is_escalated: bool
    escalation_reason: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)
    notes: List[TicketNoteRead] = Field(default_factory=list)
    feedback: Optional[FeedbackRead] = None
    created_at: datetime


class FeedbackRequestCreate(BaseModel):
    channel: Literal["whatsapp", "email", "web"] = "web"


class FeedbackSubmit(BaseModel):
    token: str
    rating: int = Field(ge=1, le=5, description="CSAT Rating 1 to 5 stars")
    was_resolved: bool
    comment: Optional[str] = None
