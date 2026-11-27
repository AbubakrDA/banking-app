from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ToolDefinitionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Function purpose and behavior")
    target_subsystem: str = Field(..., description="Underlying module e.g. Business Data, Knowledge Base")
    risk_level: str = Field(..., description="LOW | MEDIUM | HIGH")
    parameters_schema: Dict[str, Any] = Field(..., description="JSON Schema for tool arguments")
    requires_human_approval: bool = Field(..., description="Whether human approval is required prior to execution")


class ToolExecuteRequest(BaseModel):
    tool_name: str = Field(..., min_length=2, max_length=128)
    caller_agent: str = Field("customer_support_agent", description="customer_support_agent | billing_agent | supervisor_agent | admin_copilot")
    caller_id: Optional[str] = Field(None, description="Identifier of customer, conversation, or operator")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Execution parameters matching tool schema")


class ToolExecuteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    execution_id: str
    tool_name: str
    risk_level: str
    status: str
    requires_approval: bool
    result: Optional[Dict[str, Any]] = None
    message: str
    duration_ms: float = 0.0


class ToolApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="approve | reject")
    reason: Optional[str] = Field(None, description="Optional justification or rejection reason")


class ToolExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    tool_name: str
    caller_agent: str
    caller_id: str
    requested_by_user_id: Optional[str] = None
    requested_by_role: Optional[str] = None
    risk_level: str
    status: str
    input_parameters: Dict[str, Any]
    raw_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: float
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MCPServerConfigCreate(BaseModel):
    name: str = Field(..., max_length=128)
    transport_type: str = Field("http", description="http | sse | stdio")
    endpoint_url: str = Field(..., max_length=512)
    auth_token: Optional[str] = Field(None, max_length=512)
    is_enabled: bool = True


class MCPServerConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    name: str
    transport_type: str
    endpoint_url: str
    is_enabled: bool
    discovered_tools: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime
