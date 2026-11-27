from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class KPIDashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_conversations: int = Field(..., description="Total customer conversations")
    ai_deflection_rate: float = Field(..., description="Percentage of conversations resolved without human escalation")
    human_escalations: int = Field(..., description="Number of conversations escalated to human agents")
    active_customers: int = Field(..., description="Number of unique active customers")
    average_csat: float = Field(..., description="Average CSAT rating (1.0 - 5.0)")
    csat_response_count: int = Field(..., description="Total feedback submissions received")
    sentiment_breakdown: Dict[str, int] = Field(..., description="Sentiment distribution: positive, neutral, negative, frustrated")
    total_tickets: int = Field(..., description="Total customer support tickets created")
    open_tickets: int = Field(..., description="Current count of open or pending tickets")
    urgent_tickets: int = Field(..., description="Current count of urgent priority tickets")
    avg_ticket_resolution_hours: float = Field(..., description="Mean resolution time in hours")
    total_questions_logged: int = Field(..., description="Total NLP logged inquiries")
    knowledge_gaps_count: int = Field(..., description="Number of identified knowledge gaps needing FAQ coverage")
    surging_clusters_count: int = Field(..., description="Count of surging question clusters")


class AIInsightCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    domain: str = Field("operations", description="operations | support | product | billing | customer_experience")
    evidence_tier: str = Field("PROBABLE", description="PROVEN | PROBABLE | PLAUSIBLE | SPECULATIVE")
    confidence_score: float = Field(0.85, ge=0.0, le=1.0)
    supporting_metrics: Optional[Dict[str, Any]] = None
    actionable_recommendation: str
    priority: str = Field("MEDIUM", description="HIGH | MEDIUM | LOW")


class AIInsightRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    title: str
    description: str
    domain: str
    evidence_tier: str
    confidence_score: float
    supporting_metrics: Optional[Dict[str, Any]] = None
    actionable_recommendation: str
    priority: str
    is_acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class AIInsightAcknowledge(BaseModel):
    acknowledged: bool = True


class OrganizationalMemoryCreate(BaseModel):
    category: str = Field("operations", description="operations | support | product | billing | general")
    title: str = Field(..., max_length=255)
    summary: str
    key_findings: Optional[List[str]] = None
    playbook_steps: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: str = Field("active", description="active | archived")


class OrganizationalMemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    category: str
    title: str
    summary: str
    key_findings: Optional[List[str]] = None
    playbook_steps: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: str
    created_at: datetime
    updated_at: datetime


class CopilotQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500, description="Natural language analytics query")


class CopilotQueryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    query: str
    intent_detected: str
    answer_summary: str
    metrics: Dict[str, Any]
    evidence_level: str
    citations: List[str]


class ExecutiveReportCreate(BaseModel):
    period_type: str = Field("weekly", description="daily | weekly | monthly | custom")
    title: Optional[str] = None


class ExecutiveReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    period_type: str
    title: str
    period_start: datetime
    period_end: datetime
    kpis: Dict[str, Any]
    insights_summary: Optional[List[Dict[str, Any]]] = None
    top_issues: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    generated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ExecutiveReportExportResponse(BaseModel):
    report_id: str
    format: str
    filename: str
    content: str
