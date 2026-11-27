from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.auth import require_roles, AuthenticatedUser
from app.models.nlp import QuestionCluster, LoggedQuestion
from app.schemas.envelope import APIResponse
from app.schemas.nlp import (
    LoggedQuestionCreate,
    LoggedQuestionRead,
    QuestionClusterRead,
    KnowledgeGapReport,
    TrendAnalysisResponse,
)
from app.services.nlp.question_intelligence import QuestionIntelligenceService

router = APIRouter()


@router.post("/questions", response_model=APIResponse[LoggedQuestionRead])
async def log_question(
    q_in: LoggedQuestionCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[LoggedQuestionRead]:
    logged_q, _ = await QuestionIntelligenceService.cluster_and_log_question(
        raw_text=q_in.raw_text,
        tenant_id=current_user.tenant_id,
        customer_id=q_in.customer_id,
        conversation_id=q_in.conversation_id,
        rag_confidence_score=q_in.rag_confidence_score,
        db=db,
    )

    return APIResponse.ok(
        data=LoggedQuestionRead.model_validate(logged_q),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/clusters", response_model=APIResponse[List[QuestionClusterRead]])
async def list_clusters(
    request: Request,
    is_knowledge_gap: Optional[bool] = None,
    intent: Optional[str] = None,
    category: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[QuestionClusterRead]]:
    query = select(QuestionCluster).where(QuestionCluster.tenant_id == current_user.tenant_id)
    if is_knowledge_gap is not None:
        query = query.where(QuestionCluster.is_knowledge_gap == is_knowledge_gap)
    if intent:
        query = query.where(QuestionCluster.intent == intent)
    if category:
        query = query.where(QuestionCluster.category == category)

    query = query.order_by(QuestionCluster.frequency.desc())
    result = await db.execute(query)
    clusters = result.scalars().all()
    data = [QuestionClusterRead.model_validate(c) for c in clusters]

    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/knowledge-gaps", response_model=APIResponse[List[KnowledgeGapReport]])
async def get_knowledge_gaps(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[KnowledgeGapReport]]:
    query = (
        select(QuestionCluster)
        .options(selectinload(QuestionCluster.questions))
        .where(
            QuestionCluster.tenant_id == current_user.tenant_id,
            QuestionCluster.is_knowledge_gap.is_(True),
        )
        .order_by(QuestionCluster.frequency.desc())
    )
    result = await db.execute(query)
    clusters = result.scalars().all()

    gaps = []
    for c in clusters:
        variations = [q.raw_text for q in (c.questions or [])[:5]]
        gaps.append(
            KnowledgeGapReport(
                id=c.id,
                canonical_question=c.canonical_question,
                frequency=c.frequency,
                intent=c.intent,
                suggested_faq_answer=c.suggested_faq_answer,
                sample_variations=variations,
            )
        )

    return APIResponse.ok(
        data=gaps,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/trends", response_model=APIResponse[TrendAnalysisResponse])
async def get_trends(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TrendAnalysisResponse]:
    # 1. Total questions
    total_q_res = await db.execute(
        select(func.count(LoggedQuestion.id)).where(LoggedQuestion.tenant_id == current_user.tenant_id)
    )
    total_questions = total_q_res.scalar() or 0

    # 2. Clusters
    clusters_res = await db.execute(
        select(QuestionCluster).where(QuestionCluster.tenant_id == current_user.tenant_id)
    )
    clusters = clusters_res.scalars().all()

    gap_count = sum(1 for c in clusters if c.is_knowledge_gap)
    surging = [QuestionClusterRead.model_validate(c) for c in clusters if c.trend_direction == "surging"]

    # 3. Intent & Sentiment distributions
    intents: Dict[str, int] = {}
    sentiments: Dict[str, int] = {}

    for c in clusters:
        intents[c.intent] = intents.get(c.intent, 0) + c.frequency
        sentiments[c.average_sentiment] = sentiments.get(c.average_sentiment, 0) + c.frequency

    report = TrendAnalysisResponse(
        total_questions=total_questions,
        total_clusters=len(clusters),
        knowledge_gap_count=gap_count,
        surging_clusters=surging,
        intent_distribution=intents,
        sentiment_distribution=sentiments,
    )

    return APIResponse.ok(
        data=report,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
