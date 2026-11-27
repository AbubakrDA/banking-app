from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, BigInteger, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TenantScopedModel


class BankAccount(TenantScopedModel):
    """Customer bank account; monetary balance stored strictly as integer minor units."""

    __tablename__ = "bank_accounts"

    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    account_number_masked: Mapped[str] = mapped_column(String(32), nullable=False)
    account_number_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    account_type: Mapped[str] = mapped_column(String(32), default="checking", nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    balance_minor: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)


class BankTransaction(TenantScopedModel):
    """Immutable banking transaction ledger entry (integer minor units)."""

    __tablename__ = "bank_transactions"

    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    tx_type: Mapped[str] = mapped_column(String(32), nullable=False)  # debit | credit | transfer
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    counterparty_masked: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class BankTransfer(TenantScopedModel):
    """Transfer request with risk scoring and maker-checker approval state."""

    __tablename__ = "bank_transfers"

    from_account_id: Mapped[str] = mapped_column(String(36), ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    to_account_id: Mapped[str] = mapped_column(String(36), ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    requested_by_user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending_approval", nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    approved_by_user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class BankCard(TenantScopedModel):
    """Payment card linked to a bank account (masked last 4 digits only)."""

    __tablename__ = "bank_cards"

    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    card_last4: Mapped[str] = mapped_column(String(4), nullable=False)
    card_type: Mapped[str] = mapped_column(String(32), default="debit", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)  # active | blocked


class RiskAlert(TenantScopedModel):
    """Placeholder risk scoring alert & case queue entry."""

    __tablename__ = "risk_alerts"

    customer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    account_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    transfer_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    severity: Mapped[str] = mapped_column(String(16), default="medium", nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    summary: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False)  # open | investigating | closed


class PolicyDocument(TenantScopedModel):
    """Bank policy document; only 'approved' documents may feed AI retrieval."""

    __tablename__ = "policy_documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)  # pending | approved | rejected
    uploaded_by_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    reviewed_by_user_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    review_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    page_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class PolicyChunk(TenantScopedModel):
    """Page-cited policy chunk for RAG retrieval."""

    __tablename__ = "policy_chunks"

    policy_id: Mapped[str] = mapped_column(String(36), ForeignKey("policy_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
