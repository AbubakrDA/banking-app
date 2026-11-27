from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TenantScopedModel


class QuestionCluster(TenantScopedModel):
    __tablename__ = "question_clusters"

    canonical_question: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    intent: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unique_customer_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    average_sentiment: Mapped[str] = mapped_column(String(32), default="neutral", nullable=False)
    trend_direction: Mapped[str] = mapped_column(
        String(32),
        default="stable",
        nullable=False,
        comment="surging | stable | declining",
    )
    is_knowledge_gap: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    suggested_faq_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)

    questions: Mapped[List["LoggedQuestion"]] = relationship(
        "LoggedQuestion",
        back_populates="cluster",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("intent", "general")
        kwargs.setdefault("category", "general")
        kwargs.setdefault("frequency", 1)
        kwargs.setdefault("unique_customer_count", 1)
        kwargs.setdefault("average_sentiment", "neutral")
        kwargs.setdefault("trend_direction", "stable")
        kwargs.setdefault("is_knowledge_gap", False)
        super().__init__(**kwargs)


class LoggedQuestion(TenantScopedModel):
    __tablename__ = "logged_questions"

    cluster_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("question_clusters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    conversation_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    detected_language: Mapped[str] = mapped_column(String(16), default="en", nullable=False)
    detected_intent: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    sentiment: Mapped[str] = mapped_column(String(32), default="neutral", nullable=False)
    was_rag_matched: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rag_confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    cluster: Mapped[Optional["QuestionCluster"]] = relationship("QuestionCluster", back_populates="questions")

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("detected_language", "en")
        kwargs.setdefault("detected_intent", "general")
        kwargs.setdefault("sentiment", "neutral")
        kwargs.setdefault("was_rag_matched", True)
        kwargs.setdefault("rag_confidence_score", 1.0)
        super().__init__(**kwargs)

