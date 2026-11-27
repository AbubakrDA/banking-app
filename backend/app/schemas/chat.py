from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, description="Message text from customer or user")
    channel: Optional[str] = Field(default="web", description="Channel identifier (web, whatsapp, email)")


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    tenant_id: str
    sender_type: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    is_flagged: bool = False
    created_at: datetime


class ConversationCreate(BaseModel):
    customer_id: Optional[str] = Field(default=None, description="Existing customer ID or omitted to create guest")
    customer_name: Optional[str] = Field(default="Valued Customer", description="Customer name if creating guest")
    channel: str = Field(default="web", description="web | whatsapp | email")


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    customer_id: str
    assigned_user_id: Optional[str] = None
    channel: str
    status: str
    summary: Optional[str] = None
    messages: List[MessageRead] = Field(default_factory=list)
    created_at: datetime


class EscalationRequest(BaseModel):
    reason: str = Field(description="Reason for human escalation")
    assigned_user_id: Optional[str] = Field(default=None, description="Optional user ID to assign")


class TurnResult(BaseModel):
    customer_message: MessageRead
    agent_message: MessageRead
    intent: str
    sentiment: str
    should_escalate: bool
    escalation_reason: Optional[str] = None
    is_security_violation: bool = False
