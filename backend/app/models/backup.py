import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Boolean, ForeignKey, BigInteger, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimeStampedModel


class BackupRecord(TimeStampedModel):
    __tablename__ = "backup_records"

    # tenant_id can be None/null for system-wide/cluster backups
    tenant_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    backup_type: Mapped[str] = mapped_column(String(32), default="FULL", nullable=False)  # FULL, INCREMENTAL, WAL, SNAPSHOT
    target_type: Mapped[str] = mapped_column(String(32), default="POSTGRESQL", nullable=False)  # POSTGRESQL, OBJECT_STORAGE, FULL_SYSTEM
    status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False)  # COMPLETED, IN_PROGRESS, FAILED, PRUNED
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    sha256_checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    encryption_algorithm: Mapped[str] = mapped_column(String(32), default="AES-256-GCM", nullable=False)
    retention_tier: Mapped[str] = mapped_column(String(32), default="DAILY", nullable=False)  # DAILY, WEEKLY, MONTHLY, MANUAL
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict, nullable=True)

    drills: Mapped[list["RestoreDrill"]] = relationship("RestoreDrill", back_populates="backup", cascade="all, delete-orphan")


class RestoreDrill(TimeStampedModel):
    __tablename__ = "restore_drills"

    backup_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("backup_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(32), default="SUCCESS", nullable=False)  # SUCCESS, FAILED, SIMULATED
    rto_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rpo_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tables_validated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_validated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checksum_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    drill_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    executed_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    backup: Mapped["BackupRecord"] = relationship("BackupRecord", back_populates="drills")


class BackupRetentionPolicy(TimeStampedModel):
    __tablename__ = "backup_retention_policies"

    tenant_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    daily_retention_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    weekly_retention_weeks: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    monthly_retention_months: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    auto_drills_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    drill_frequency_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
