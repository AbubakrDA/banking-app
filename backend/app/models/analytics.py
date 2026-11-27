from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Float, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TenantScopedModel


class AIInsight(TenantScopedModel):
    __tablename__ = "ai_insights"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(
        String(64),
        default="operations",
        nullable=False,
        comment="operations | support | product | billing | customer_experience",
    )
    evidence_tier: Mapped[str] = mapped_column(
        String(32),
        default="PROBABLE",
        nullable=False,
        comment="PROVEN | PROBABLE | PLAUSIBLE | SPECULATIVE",
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    supporting_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    actionable_recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(
        String(32),
        default="MEDIUM",
        nullable=False,
        comment="HIGH | MEDIUM | LOW",
    )
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("domain", "operations")
        kwargs.setdefault("evidence_tier", "PROBABLE")
        kwargs.setdefault("confidence_score", 0.85)
        kwargs.setdefault("priority", "MEDIUM")
        kwargs.setdefault("is_acknowledged", False)
        super().__init__(**kwargs)


class OrganizationalMemoryEntry(TenantScopedModel):
    __tablename__ = "organizational_memory"

    category: Mapped[str] = mapped_column(
        String(64),
        default="operations",
        nullable=False,
        comment="operations | support | product | billing | general",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_findings: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    playbook_steps: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
        comment="active | archived",
    )

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("category", "operations")
        kwargs.setdefault("status", "active")
        super().__init__(**kwargs)


class ExecutiveReport(TenantScopedModel):
    __tablename__ = "executive_reports"

    period_type: Mapped[str] = mapped_column(
        String(32),
        default="weekly",
        nullable=False,
        comment="daily | weekly | monthly | custom",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    kpis: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    insights_summary: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    top_issues: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    generated_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("period_type", "weekly")
        super().__init__(**kwargs)
