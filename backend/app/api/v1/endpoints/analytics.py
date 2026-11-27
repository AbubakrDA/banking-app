import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import get_current_user, require_roles, AuthenticatedUser
from app.models.analytics import AIInsight, OrganizationalMemoryEntry, ExecutiveReport
from app.schemas.envelope import APIResponse
from app.schemas.analytics import (
    KPIDashboardResponse,
    AIInsightCreate,
    AIInsightRead,
    AIInsightAcknowledge,
    OrganizationalMemoryCreate,
    OrganizationalMemoryRead,
    CopilotQueryRequest,
    CopilotQueryResponse,
    ExecutiveReportCreate,
    ExecutiveReportRead,
    ExecutiveReportExportResponse,
)
from app.services.analytics.intelligence import AdminIntelligenceService

router = APIRouter()


@router.get("/kpis", response_model=APIResponse[KPIDashboardResponse])
async def get_kpis(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[KPIDashboardResponse]:
    """Retrieve live aggregated KPI metrics for the tenant."""
    data = await AdminIntelligenceService.get_kpi_dashboard(current_user.tenant_id, db)
    return APIResponse.ok(
        data=KPIDashboardResponse.model_validate(data),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/insights", response_model=APIResponse[List[AIInsightRead]])
async def list_insights(
    request: Request,
    domain: Optional[str] = None,
    evidence_tier: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[AIInsightRead]]:
    """List AI Insights for the tenant."""
    query = select(AIInsight).where(AIInsight.tenant_id == current_user.tenant_id)
    if domain:
        query = query.where(AIInsight.domain == domain)
    if evidence_tier:
        query = query.where(AIInsight.evidence_tier == evidence_tier)

    query = query.order_by(AIInsight.created_at.desc())
    res = await db.execute(query)
    insights = res.scalars().all()

    return APIResponse.ok(
        data=[AIInsightRead.model_validate(i) for i in insights],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/insights/generate", response_model=APIResponse[List[AIInsightRead]])
async def generate_insights(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[AIInsightRead]]:
    """Trigger real-time operational analysis and synthesize AI insights."""
    insights = await AdminIntelligenceService.generate_ai_insights(
        tenant_id=current_user.tenant_id,
        db=db,
        generated_by=current_user.user_id,
    )
    await db.commit()
    return APIResponse.ok(
        data=[AIInsightRead.model_validate(i) for i in insights],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.patch("/insights/{insight_id}/acknowledge", response_model=APIResponse[AIInsightRead])
async def acknowledge_insight(
    insight_id: str,
    ack: AIInsightAcknowledge,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[AIInsightRead]:
    """Acknowledge or dismiss an AI insight."""
    res = await db.execute(
        select(AIInsight).where(
            AIInsight.id == insight_id,
            AIInsight.tenant_id == current_user.tenant_id,
        )
    )
    insight = res.scalar_one_or_none()
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "INSIGHT_NOT_FOUND", "message": f"Insight {insight_id} not found."},
        )

    insight.is_acknowledged = ack.acknowledged
    insight.acknowledged_by = current_user.user_id
    insight.acknowledged_at = datetime.now(timezone.utc)
    await db.commit()

    return APIResponse.ok(
        data=AIInsightRead.model_validate(insight),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/organizational-memory", response_model=APIResponse[List[OrganizationalMemoryRead]])
async def list_organizational_memory(
    request: Request,
    category: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[OrganizationalMemoryRead]]:
    """Retrieve organizational memory playbooks and historical resolutions."""
    query = select(OrganizationalMemoryEntry).where(
        OrganizationalMemoryEntry.tenant_id == current_user.tenant_id
    )
    if category:
        query = query.where(OrganizationalMemoryEntry.category == category)

    query = query.order_by(OrganizationalMemoryEntry.created_at.desc())
    res = await db.execute(query)
    entries = res.scalars().all()

    return APIResponse.ok(
        data=[OrganizationalMemoryRead.model_validate(e) for e in entries],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/organizational-memory", response_model=APIResponse[OrganizationalMemoryRead])
async def create_organizational_memory(
    entry_in: OrganizationalMemoryCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[OrganizationalMemoryRead]:
    """Record a new organizational memory entry or operational playbook."""
    entry = OrganizationalMemoryEntry(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        category=entry_in.category,
        title=entry_in.title,
        summary=entry_in.summary,
        key_findings=entry_in.key_findings,
        playbook_steps=entry_in.playbook_steps,
        tags=entry_in.tags,
        status=entry_in.status,
    )
    db.add(entry)
    await db.commit()

    return APIResponse.ok(
        data=OrganizationalMemoryRead.model_validate(entry),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/copilot/query", response_model=APIResponse[CopilotQueryResponse])
async def query_copilot(
    query_in: CopilotQueryRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[CopilotQueryResponse]:
    """Ask Analytics Copilot an administrative analytics query (governed read-only)."""
    resp = await AdminIntelligenceService.query_analytics_copilot(
        tenant_id=current_user.tenant_id,
        query_text=query_in.query,
        db=db,
    )
    return APIResponse.ok(
        data=resp,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/reports", response_model=APIResponse[List[ExecutiveReportRead]])
async def list_reports(
    request: Request,
    period_type: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[ExecutiveReportRead]]:
    """List compiled executive intelligence reports."""
    query = select(ExecutiveReport).where(ExecutiveReport.tenant_id == current_user.tenant_id)
    if period_type:
        query = query.where(ExecutiveReport.period_type == period_type)

    query = query.order_by(ExecutiveReport.created_at.desc())
    res = await db.execute(query)
    reports = res.scalars().all()

    return APIResponse.ok(
        data=[ExecutiveReportRead.model_validate(r) for r in reports],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/reports/generate", response_model=APIResponse[ExecutiveReportRead])
async def generate_report(
    rep_in: ExecutiveReportCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ExecutiveReportRead]:
    """Compile and persist an Executive Intelligence Report."""
    report = await AdminIntelligenceService.generate_executive_report(
        tenant_id=current_user.tenant_id,
        period_type=rep_in.period_type,
        title=rep_in.title,
        generated_by=current_user.user_id,
        db=db,
    )
    await db.commit()
    return APIResponse.ok(
        data=ExecutiveReportRead.model_validate(report),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/reports/{report_id}/export", response_model=APIResponse[ExecutiveReportExportResponse])
async def export_report(
    report_id: str,
    request: Request,
    export_format: str = Query("json", alias="format", pattern="^(json|csv)$"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ExecutiveReportExportResponse]:
    """Export an executive report as structured JSON or CSV."""
    res = await db.execute(
        select(ExecutiveReport).where(
            ExecutiveReport.id == report_id,
            ExecutiveReport.tenant_id == current_user.tenant_id,
        )
    )
    report = res.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "REPORT_NOT_FOUND", "message": f"Report {report_id} not found."},
        )

    if export_format == "csv":
        content = AdminIntelligenceService.export_report_to_csv(report)
        filename = f"banking_ai_report_{report.id}.csv"
    else:
        content = json.dumps(
            {
                "id": report.id,
                "title": report.title,
                "period_type": report.period_type,
                "period_start": report.period_start.isoformat(),
                "period_end": report.period_end.isoformat(),
                "kpis": report.kpis,
                "insights_summary": report.insights_summary,
                "top_issues": report.top_issues,
                "recommendations": report.recommendations,
            },
            indent=2,
        )
        filename = f"banking_ai_report_{report.id}.json"

    return APIResponse.ok(
        data=ExecutiveReportExportResponse(
            report_id=report.id,
            format=export_format,
            filename=filename,
            content=content,
        ),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
