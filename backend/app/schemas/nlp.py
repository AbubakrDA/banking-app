from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class LoggedQuestionCreate(BaseModel):
    raw_text: str = Field(min_length=3, description="Customer question text")
    customer_id: Optional[str] = None
    conversation_id: Optional[str] = None
    rag_confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)


class LoggedQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    cluster_id: Optional[str] = None
    customer_id: Optional[str] = None
    conversation_id: Optional[str] = None
    raw_text: str
    detected_language: str
    detected_intent: str
    sentiment: str
    was_rag_matched: bool
    rag_confidence_score: float
    created_at: datetime


class QuestionClusterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    canonical_question: str
    intent: str
    category: str
    frequency: int
    unique_customer_count: int
    average_sentiment: str
    trend_direction: str
    is_knowledge_gap: bool
    suggested_faq_answer: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class KnowledgeGapReport(BaseModel):
    id: str
    canonical_question: str
    frequency: int
    intent: str
    suggested_faq_answer: Optional[str] = None
    sample_variations: List[str]


class TrendAnalysisResponse(BaseModel):
    total_questions: int
    total_clusters: int
    knowledge_gap_count: int
    surging_clusters: List[QuestionClusterRead]
    intent_distribution: Dict[str, int]
    sentiment_distribution: Dict[str, int]
